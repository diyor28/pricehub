import asyncio
import typing

import httpx as httpx
import tqdm
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand

from products.management.commands.utils import get_headers, AsyncPool
from products.models import ProductModel, ProductPhotoModel


class Command(BaseCommand):
    help = 'Post process'
    client = httpx.AsyncClient(http2=True)
    pbar: typing.Optional[tqdm.tqdm] = None

    async def get_product(self, product_id: str):
        url = f"https://api.uzum.uz/api/v2/product/{product_id}"
        resp = await self.client.get(url, headers=get_headers())
        if resp.status_code not in [200, 201]:
            return
        data = resp.json()
        if not data["payload"]:
            return
        return data["payload"]["data"]

    async def _process_product(self, product: ProductModel):
        data = await self.get_product(product.uzum_remote_id)
        if data is None:
            return
        product.sku = data["skuList"][0]["id"] if data["skuList"] else None
        photos = []
        for ph in data["photos"]:
            photos.append(ProductPhotoModel(
                original=ph["photo"]["800"]["high"],
                large=ph["photo"]["540"]["high"],
                small=ph["photo"]["240"]["high"],
                product_id=product.pk
            ))
        await asyncio.gather(
            sync_to_async(ProductPhotoModel.objects.bulk_create)(photos),
            sync_to_async(product.save)()
        )
        self.pbar.update(1)

    async def _download_skus(self, products: list[ProductModel]):
        pool = AsyncPool(20)
        self.pbar = tqdm.tqdm(total=len(products))
        await pool.map(self._process_product, products)
        await self.client.aclose()
        self.pbar.close()

    def handle(self, *args, **options):
        products = list(ProductModel.objects.all())
        asyncio.run(self._download_skus(products))
