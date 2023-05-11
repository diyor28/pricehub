import json

from django.core.management import BaseCommand

from products.models import ProductModel


class Command(BaseCommand):
    help = 'Downloads categories from data.json'

    def handle(self, *args, **options):
        with open('data/data.json', 'r') as file:
            products = json.load(file)
        ProductModel.objects.bulk_create([ProductModel(**item) for item in products])
        self.stdout.write(self.style.SUCCESS('Categories downloaded successfully.'))
