import asyncio
import logging
import os

import aiohttp
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand

from pricehub.products import timeit
from products.models import ProductModel

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Download product photos'

    async def download_product_photos(self):
        products = await sync_to_async(list)(ProductModel.objects.filter(photo__isnull=False).all()[:100])
        os.makedirs('photos', exist_ok=True)
        max_connections = 10

        async with aiohttp.ClientSession() as session:
            tasks = []

            for product in products:
                filename = f'product_{product.pk}.png'
                save_path = os.path.join('photos', filename)

                task = self.download_image(session, product.photo, save_path, filename)
                tasks.append(task)

                if len(tasks) >= max_connections:
                    await asyncio.gather(*tasks)
                    tasks = []

            if tasks:
                await asyncio.gather(*tasks)

        logger.info('All photos downloaded successfully.')

    async def download_image(self, session, image_url, save_path, filename):
        try:
            async with session.get(image_url) as response:
                response.raise_for_status()
                expected_size = int(response.headers['Content-Length'])
                data = await response.read()

                if len(data) != expected_size:
                    raise ValueError('Incomplete download')

                with open(save_path, 'wb') as file:
                    file.write(data)

                logger.info(f'Saved photo: {filename}')

        except aiohttp.ClientError as e:
            if isinstance(e, aiohttp.ClientResponseError) and e.status == 403:
                logger.warning(f'Skipped photo: {filename} (Forbidden)')
            else:
                logger.error(f'Error downloading photo: {filename}')

        except (ValueError, Exception) as e:
            logger.error(f'Skipped photo: {filename} (Incomplete download)')
            logger.error(f'Error: {str(e)}')

    @timeit
    def handle(self, *args, **options):
        asyncio.run(self.download_product_photos())
