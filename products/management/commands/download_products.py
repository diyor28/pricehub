import asyncio

import httpx
import tqdm
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand

from pricehub.products import timeit
from products.management.commands.utils import title_to_link, query, GLOBAL_HEADERS, variables
from products.models import CategoriesModel, ProductModel, PriceHistory


class UzumClient:

    def __init__(self):
        limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
        self.client = httpx.AsyncClient(http2=True, limits=limits)

    @timeit
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


class ProductsDownloader:
    client: UzumClient

    def __init__(self, categories: list[CategoriesModel], concurrent: int):
        self.categories = categories
        self.concurrent = concurrent
        self.pbar = tqdm.tqdm(total=len(categories))
        self.client = UzumClient()

    async def process_category(self, category: CategoriesModel):
        products = await self.client.download_products(int(category.remote_id))
        to_be_created = []
        to_be_updated = []
        to_be_created_ph = []

        seen = set()
        products = [seen.add(p["productId"]) or p for p in products if p["productId"] not in seen]

        for p in products:
            price = p["minSellPrice"]
            title = p["title"]
            photo = p["photos"][0]["link"]["high"]
            url = title_to_link(p["title"]) + f"-{p['productId']}"
            try:
                existing = await sync_to_async(ProductModel.objects.get)(uzum_remote_id=str(p["productId"]))
                existing.title = title
                existing.price = price
                existing.photo = photo
                existing.url = url
                to_be_created_ph.append(PriceHistory(price=price, product_id=existing.pk))
                to_be_updated.append(existing)
            except ProductModel.DoesNotExist:
                product = ProductModel(
                    title=title,
                    price=price,
                    uzum_remote_id=str(p["productId"]),
                    category_id=category.id,
                    anchor_category_id=category.anchor_id,
                    photo=photo,
                    url=url
                )
                to_be_created.append(product)

        await asyncio.gather(
            sync_to_async(PriceHistory.objects.bulk_create)(to_be_created_ph),
            sync_to_async(ProductModel.objects.bulk_create)(to_be_created),
            sync_to_async(ProductModel.objects.bulk_update)(to_be_updated, fields=['title', 'price', 'photo', 'url'])
        )
        self.pbar.update(1)

    async def _download_multiple(self, categories):
        await asyncio.gather(*[self.process_category(cat) for cat in categories])

    async def _async_download(self):
        for i in range(0, len(self.categories), self.concurrent):
            await self._download_multiple(self.categories[i:i + 5])
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
