import os
import urllib.request
import logging
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from django.core.management.base import BaseCommand
from products.models import ProductModel

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Command(BaseCommand):
    help = 'Download and save product images from ProductModel'

    def handle(self, *args, **options):
        download_product_photos()

def download_product_photos():
    products = ProductModel.objects.exclude(photo__isnull=True)
    os.makedirs('photos', exist_ok=True)

    max_workers = 10
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []

        for product in products:
            image_url = product.photo
            product_id = product.id

            filename = f'product_{product_id}.png'
            save_path = os.path.join('photos', filename)

            future = executor.submit(download_image, image_url, save_path, filename)
            futures.append(future)

        for future in futures:
            future.result()

    logging.info('All photos downloaded successfully.')

def download_image(image_url, save_path, filename):
    try:
        response = urllib.request.urlopen(image_url)
        expected_size = int(response.headers['Content-Length'])
        data = response.read()

        if len(data) != expected_size:
            raise ValueError('Incomplete download')

        with open(save_path, 'wb') as file:
            file.write(data)

        logging.info(f'Saved photo: {filename}')
    except urllib.error.URLError as e:
        if isinstance(e.reason, urllib.error.HTTPError) and e.reason.code == 403:
            logging.warning(f'Skipped photo: {filename} (Forbidden)')
        else:
            logging.error(f'Error downloading photo: {filename}')
    except (ValueError, Exception) as e:
        logging.error(f'Skipped photo: {filename} (Incomplete download)')
        logging.error(f'Error: {str(e)}')

if __name__ == '__main__':
    command = Command()
    command.handle()
