from queue import Queue
from threading import Thread

import requests
from django.core.management import BaseCommand

from pricehub.products import timeit
from pricehub.views import headers

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


def do_task(task_q, res_q):
    while not task_q.empty():
        url = task_q.get(block=True)
        resp = requests.get(url, headers=headers)
        res_q.put(resp.json())


class Command(BaseCommand):
    help = 'Downloads categories from API'

    @timeit
    def handle(self, *args, **options):
        task_q = Queue(maxsize=1000)
        res_q = Queue(maxsize=1000)
        fabrics = []
        sklad = []

        for url in urls:
            task_q.put(url)

        for i in range(10):
            th = Thread(target=do_task, args=(task_q, res_q))
            th.start()
            fabrics.append(th)

        while len(sklad) < len(urls):
            sklad.append(res_q.get(block=True))

        for th in fabrics:
            th.join()

        # your code goes here
        assert len(sklad) == len(urls)
