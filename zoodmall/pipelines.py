import os

from scrapy import signals
from scrapy.crawler import Crawler

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

    def spider_opened(self, spider):
        if not os.path.exists("data"):
            os.makedirs("data")

        if os.path.exists("data/data.txt"):
            os.remove("data/data.txt")

    def spider_closed(self, spider: ZoodMallSpider):
        self.save_products()

    def save_products(self):
        with open("data/data.txt", "a", encoding="utf-8") as outfile:
            for i in self.items:
                outfile.write(f'{i["title"]}|{i["price"]}|{i["sku"]}|{i["photo"]}|{i["url"]}\n')
        self.items.clear()

    def process_item(self, item, spider):
        self.items.append(item)
        self.pages_crawled += 1
        if len(self.items) >= 100:
            self.save_products()
        return item
