from django.core.management import BaseCommand

from products.models import ProductModel


class Command(BaseCommand):
    help = 'Downloads categories from data.json'

    def handle(self, *args, **options):
        products = []
        with open("data/data.txt", "r", encoding="utf8") as file:
            lines = file.readlines()
            for p in lines:
                prd = p.split('|')
                if len(prd) < 4:
                    continue

                title, price, sku, photo, product_url = prd
                product = ProductModel(title=title, price=price, sku=sku, url=product_url, photo=photo)
                products.append(product)
        ProductModel.objects.bulk_create(products)
        self.stdout.write(self.style.SUCCESS('Products from .txt downloaded successfully.'))
