from django.core.management import BaseCommand

from pricehub.products import timeit

urls = [
    "https://api.umarket.uz/api/v2/product/389704",
    "https://api.umarket.uz/api/v2/product/3702",
    "https://api.umarket.uz/api/v2/product/278740",
    "https://api.umarket.uz/api/v2/product/380004",
    "https://api.umarket.uz/api/v2/product/389704",
    "https://api.umarket.uz/api/v2/product/3702",
    "https://api.umarket.uz/api/v2/product/278740",
    "https://api.umarket.uz/api/v2/product/380004",
    "https://api.umarket.uz/api/v2/product/389704",
    "https://api.umarket.uz/api/v2/product/3702",
    "https://api.umarket.uz/api/v2/product/278740",
    "https://api.umarket.uz/api/v2/product/380004",
    "https://api.umarket.uz/api/v2/product/389704",
    "https://api.umarket.uz/api/v2/product/3702",
    "https://api.umarket.uz/api/v2/product/278740",
    "https://api.umarket.uz/api/v2/product/380004",
    "https://api.umarket.uz/api/v2/product/389704",
    "https://api.umarket.uz/api/v2/product/3702",
    "https://api.umarket.uz/api/v2/product/278740",
    "https://api.umarket.uz/api/v2/product/380004",
    "https://api.umarket.uz/api/v2/product/389704",
    "https://api.umarket.uz/api/v2/product/3702",
    "https://api.umarket.uz/api/v2/product/278740",
    "https://api.umarket.uz/api/v2/product/380004",
    "https://api.umarket.uz/api/v2/product/389704",
    "https://api.umarket.uz/api/v2/product/3702",
    "https://api.umarket.uz/api/v2/product/278740",
    "https://api.umarket.uz/api/v2/product/380004",
    "https://api.umarket.uz/api/v2/product/389704",
    "https://api.umarket.uz/api/v2/product/3702",
    "https://api.umarket.uz/api/v2/product/278740",
    "https://api.umarket.uz/api/v2/product/380004",
]


class Command(BaseCommand):
    help = 'Downloads categories from API'

    @timeit
    def handle(self, *args, **options):
        assert len(results) == len(urls)
        print('Congrats! Drinks on me')
