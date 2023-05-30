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
        limits = httpx.Limits(max_keepalive_connections=10, max_connections=50)
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
            except ValueError:
                break
            if not data["items"]:
                return
            products += [p["catalogCard"] for p in data["items"]]
            if data["total"] < offset + limit:
                break
        skus = await asyncio.gather(*[self.get_sku(p["id"]) for p in products])
        for p, sku in zip(products, skus):
            p["sku"] = sku
        return products

    async def get_sku(self, product_id: str):
        url = f"https://api.uzum.uz/api/v2/product/{product_id}"
        resp = await self.client.get(url, headers=GLOBAL_HEADERS)
        if resp.status_code not in [200, 201]:
            return
        data = resp.json()
        if not data["payload"]:
            return
        if not data["payload"]["data"]["skuList"]:
            return
        return data["payload"]["data"]["skuList"][0]["id"]

    def aclose(self):
        return self.client.aclose()


class ProductsDownloader:
    client: UzumClient

    def __init__(self, categories: list[CategoriesModel]):
        self.pbar = tqdm.tqdm(total=len(categories))
        self.categories = categories
        self.client = UzumClient()

    async def process_category(self, category: CategoriesModel):
        products = await self.client.download_products(int(category.remote_id))

        to_be_created = []
        to_be_updated = []
        to_be_created_ph = []

        for p in products:
            price = p["minSellPrice"]
            title = p["title"]
            photo = p["photos"][0]["link"]["high"]
            sku = p["sku"]
            url = title_to_link(p["title"]) + f"-{p['id']}"
            try:
                if not sku:
                    raise ProductModel.DoesNotExist("Bullshit")
                existing_product = await sync_to_async(ProductModel.objects.get)(sku=sku)
                existing_product.title = title
                existing_product.price = price
                existing_product.photo = photo
                existing_product.url = url
                to_be_created_ph.append(PriceHistory(price=price, product_id=existing_product.pk))
                to_be_updated.append(existing_product)
            except ProductModel.DoesNotExist:
                product = ProductModel(
                    title=title,
                    sku=sku,
                    price=price,
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
        for i in range(0, len(self.categories), 5):
            await self._download_multiple(self.categories[i:i + 5])
        await self.client.aclose()
        self.pbar.close()

    def download(self):
        asyncio.run(self._async_download())


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    @timeit
    def handle(self, *args, **options):
        uzum_categories = list(CategoriesModel.objects.all()[:100])
        downloader = ProductsDownloader(uzum_categories)
        downloader.download()
