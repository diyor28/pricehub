import os
import json

from scrapy import signals
from scrapy.crawler import Crawler

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

        if os.path.exists("data/data.json"):
            os.remove("data/data.json")

    def spider_closed(self, spider: ZoodMallSpider):
        self.save_products()

    @timeit
    def save_products(self):
        with open("data/data.json", "a") as outfile:
            json.dump(self.items, outfile)

        self.items = []

    def process_item(self, item: dict, spider: ZoodMallSpider):
        self.items.append(item)
        self.pages_crawled += 1
        if len(self.items) > 10:
            self.save_products()
        return item
