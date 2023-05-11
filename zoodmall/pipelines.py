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
        pass

    def spider_closed(self, spider: ZoodMallSpider):
        self.save_products()

    @timeit
    def save_products(self):
        with open("../data/data.json", "w") as outfile:
            outfile.write(json.dumps(self.items))


    def process_item(self, item: dict, spider: ZoodMallSpider):
        self.items.append(item)
        self.pages_crawled += 1
        return item
