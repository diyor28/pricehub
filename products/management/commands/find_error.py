from django.core.management.base import BaseCommand

from products.models import ProductModel


def url(product):
    return "https://uzum.uz/ru/product/" + product["title"] + product["remote-id"]


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    @staticmethod
    def get_products(src="uzum"):
        return ProductModel.objects.filter(category__source=src)

    def handle(self, *args, **options):
        categories = self.get_products()
        urls = []
        for category in categories:
            urls.append(url(category))
        print(urls[0])
