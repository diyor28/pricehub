from django.core.management.base import BaseCommand
import os
import aiohttp
import asyncio
import logging
import time
import psycopg2


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Download product photos'

    async def download_product_photos(self):
        connection_params = {
            'host': '127.0.0.1',
            'port': '5432',
            'database': 'pricehub',
            'user': 'postgres',
            'password': 'postgres'
        }

        conn = None
        cursor = None

        try:
            conn = psycopg2.connect(**connection_params)
            cursor = conn.cursor()

            cursor.execute("SELECT id, photo FROM products WHERE photo IS NOT NULL")
            products = cursor.fetchall()

            os.makedirs('photos', exist_ok=True)
            max_connections = 10

            async with aiohttp.ClientSession() as session:
                tasks = []

                for product in products:
                    product_id = product[0]
                    image_url = product[1]

                    filename = f'product_{product_id}.png'
                    save_path = os.path.join('photos', filename)

                    task = self.download_image(session, image_url, save_path, filename)
                    tasks.append(task)

                    if len(tasks) >= max_connections:
                        await asyncio.gather(*tasks)
                        tasks = []

                if tasks:
                    await asyncio.gather(*tasks)

            logger.info('All photos downloaded successfully.')

        except psycopg2.Error as e:
            logger.error(f'Error connecting to PostgreSQL: {str(e)}')

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

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

    def handle(self, *args, **options):
        start_time = time.time()

        asyncio.run(self.download_product_photos())

        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f'Total execution time: {execution_time} seconds')
