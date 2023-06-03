import os

from django.core.management import BaseCommand

from products.models import ProductModel


class Command(BaseCommand):
    help = 'Downloads categories from data.json'

    def handle(self, *args, **options):
        products = []
        with open('data/data.txt', 'r') as file:
            lines = file.read().split('\n')
            for p in lines:
                prd = p.split(' | ')
                if len(prd) >= 4:
                    title = prd[0].strip()
                    price = prd[1].strip()
                    sku = prd[2].strip()
                    photo = prd[3].strip()
                    product_url = prd[4].strip()
                    product = ProductModel(
                        title=title,
                        price=price,
                        sku=sku,
                        uzum_remote_id=2,
                        url=product_url,
                        photo=photo
                    )
                    products.append(product)
        ProductModel.objects.bulk_create(products)
        self.stdout.write(self.style.SUCCESS('Products from .txt downloaded successfully.'))
        os.remove("data/data.txt")

