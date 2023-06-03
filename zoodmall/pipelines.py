import os

from scrapy import signals
from scrapy.crawler import Crawler
from numba import jit

from pricehub.products import timeit
from .spiders.zoodmall import ZoodMallSpider


class ZoodmallPipeline:
    items: list[dict]

    def __init__(self, *args, **kwargs):
        self.items = []
        self.pages_crawled = 0

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signal=signals.spider_closed)
        return pipeline

    def spider_opened(self, spider: ZoodMallSpider):
        if not os.path.exists("data"):
            os.makedirs("data")

        if os.path.exists("data/data.txt"):
            os.remove("data/data.txt")

    def spider_closed(self, spider: ZoodMallSpider):
        self.save_products()
        let = os.system('scrapy crawl zoodmall')
        print(let)

    @timeit
    def save_products(self):
        with open("data/data.txt", "a") as outfile:
            for i in self.items:
                outfile.writelines(f'{i["title"]} | {i["price"]} | {i["sku"]} | {i["photo"]} | {i["url"]}\n\n')
        self.items = []

    @timeit
    def process_item(self, item: dict, spider: ZoodMallSpider):
        self.items.append(item)
        self.save_products()
        self.pages_crawled += 1
        return item
