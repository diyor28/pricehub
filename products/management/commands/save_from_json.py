from django.core.management import BaseCommand
import json
from products.models import ProductModel


class Command(BaseCommand):
    help = 'Downloads categories from data.json'

    def handle(self, *args, **options):
        to_be_saved = []
        with open('data/data.json', 'r') as file:
            products = json.load(file)
            for item in products:
                product = ProductModel(
                    title=item["title"],
                    price=item["price"],
                    sku=item["sku"],
                    photo=item["photo"]
                )
                to_be_saved.append(product)
        ProductModel.objects.bulk_create(to_be_saved)

        self.stdout.write(self.style.SUCCESS('Categories downloaded successfully.'))
