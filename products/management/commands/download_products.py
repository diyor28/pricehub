import asyncio
import typing

import httpx
import tqdm
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand

from pricehub.products import timeit
from products.management.commands.utils import title_to_link, query, GLOBAL_HEADERS, variables
from products.models import CategoriesModel, ProductModel


class UzumClient:

    def __init__(self):
        limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
        self.client = httpx.AsyncClient(http2=True, limits=limits)

    async def _get_page(self, v):
        response = await self.client.post("https://graphql.umarket.uz", json={
            "query": query,
            "variables": v,
        }, headers=GLOBAL_HEADERS)
        resp = response.json()
        if resp.get("errors"):
            raise ValueError(resp.get("errors"))
        data = resp["data"]["makeSearch"]
        return data

    async def download_products(self, categoryId: int):
        products = []
        limit = 100
        for offset in range(0, 100_000, limit):
            try:
                data = await self._get_page(variables(categoryId, offset, limit))
            except ValueError as e:
                print(e)
                break
            if not data["items"]:
                return
            products += [p["catalogCard"] for p in data["items"]]
            if data["total"] < offset + limit:
                break
        return products

    def aclose(self):
        return self.client.aclose()


class AsyncPool:
    def __init__(self, workers: int):
        self.workers = workers
        self._executing: list[asyncio.Task] = []

    async def map(self, f: typing.Callable, iterable: typing.Iterable):
        for el in iterable:
            if len(self._executing) >= self.workers:
                _, pending = await asyncio.wait(self._executing, return_when=asyncio.FIRST_COMPLETED)
                self._executing = list(pending)
            self._executing.append(asyncio.create_task(f(el)))
        await asyncio.wait(self._executing, return_when=asyncio.ALL_COMPLETED)


class ProductsDownloader:
    client: UzumClient

    def __init__(self, categories: list[CategoriesModel], concurrent: int):
        self.categories = categories
        self.concurrent = concurrent
        self.pbar = tqdm.tqdm(total=len(categories))
        self.client = UzumClient()

    async def _save_products(self, category: CategoriesModel, products: list[dict]):
        to_be_created = []
        existing: list[ProductModel] = await sync_to_async(list)(ProductModel.objects.filter(uzum_remote_id__in=[p["productId"] for p in products]).all())
        existing_ids = [ex.uzum_remote_id for ex in existing]
        for p in products:
            product_id = str(p['productId'])
            price = p["minSellPrice"]
            title = p["title"]
            photo = p["photos"][0]["link"]["high"]
            url = title_to_link(p["title"]) + f"-{product_id}"
            if product_id in existing_ids:
                continue
            to_be_created.append(ProductModel(
                title=title,
                price=price,
                uzum_remote_id=product_id,
                category_id=category.id,
                anchor_category_id=category.anchor_id,
                photo=photo,
                url=url
            ))
        await sync_to_async(ProductModel.objects.bulk_create)(to_be_created)

    async def process_category(self, category: CategoriesModel):
        products = await self.client.download_products(int(category.remote_id))
        seen = set()
        products = [seen.add(p["productId"]) or p for p in products if p["productId"] not in seen]
        await self._save_products(category, products)
        self.pbar.update(1)

    async def _async_download(self):
        pool = AsyncPool(self.concurrent)
        await pool.map(self.process_category, self.categories)
        await self.client.aclose()
        self.pbar.close()

    def download(self):
        asyncio.run(self._async_download())


class Command(BaseCommand):
    help = 'Download products'

    def add_arguments(self, parser):
        parser.add_argument('--categories', type=int, default=10)
        parser.add_argument('--concurrent', type=int, default=4)

    @timeit
    def handle(self, *args, **options):
        limit = options["categories"]
        concurrent = options["concurrent"]
        uzum_categories = list(CategoriesModel.objects.all()[:limit])
        downloader = ProductsDownloader(uzum_categories, concurrent)
        downloader.download()
