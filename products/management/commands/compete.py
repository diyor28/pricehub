import requests
from django.core.management import BaseCommand

from pricehub.products import timeit
from products.api import emojis


def get_emojy():
    return requests.get('http://localhost:8000/api/emojis').json()[0]


class Command(BaseCommand):
    help = 'Downloads categories from API'

    @timeit
    def handle(self, *args, **options):
        collected = set()
        # your code goes here
        futures = []

        assert len(collected) == len(emojis)
        assert set(collected) == set(emojis)
        print('Congrats! Drinks on me')
