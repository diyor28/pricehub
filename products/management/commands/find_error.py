from django.core.management.base import BaseCommand

from products.models import ProductModel


def url(product):
    return "https://uzum.uz/ru/product/" + product.title + product.category.remote_id


def translit(text):
    return ""


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        assert translit("Стиральная") == "Stiralnaya"
