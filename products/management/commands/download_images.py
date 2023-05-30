import argparse
import asyncio
import logging
import os
import typing

import httpx
import tqdm
from django.core.management.base import BaseCommand

from pricehub.products import timeit, Timer
from products.management.commands.utils import AsyncPool
from products.models import ProductModel

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Download product photos'
    client = httpx.AsyncClient(http2=False, limits=httpx.Limits(max_connections=20, max_keepalive_connections=10))
    pbar: typing.Optional[tqdm.tqdm] = None

    async def download_product_photos(self, products: list[ProductModel], concurrent: int):
        self.pbar = tqdm.tqdm(total=len(products))
        pool = AsyncPool(concurrent)
        await pool.map(self.download_image, products)
        logger.info('All photos downloaded successfully.')
        await self.client.aclose()
        self.pbar.close()

    async def _download(self, url):
        response = await self.client.get(url)
        response.raise_for_status()
        expected_size = int(response.headers['Content-Length'])
        data = response.read()
        assert len(data) == expected_size
        return data

    async def download_image(self, product: ProductModel):
        save_path = os.path.join('photos', f'product_{product.pk}.png')
        try:
            data = await self._download(product.photo)
            with open(save_path, 'wb') as file:
                file.write(data)
        except Exception as e:
            print('Some shit happened')
            print(e)
        self.pbar.update(1)

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument('--limit', type=int, default=400)
        parser.add_argument('--concurrent', type=int, default=20)

    @timeit
    def handle(self, *args, limit=1000, concurrent=10, **kwargs):
        os.makedirs('photos', exist_ok=True)
        products = list(ProductModel.objects.filter(photo__isnull=False).order_by('id').all()[:limit])
        asyncio.run(self.download_product_photos(products, concurrent))
