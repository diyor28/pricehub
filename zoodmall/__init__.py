from scrapy import signals
from scrapy.crawler import Crawler

from zoodmall.zoodmall.spiders.zoodmall import ZoodMallSpider


class ZoodmallPipeline:
    items:list[dict]

    def __init__(self, *args, **kwargs):
        self.items = []
        self.pages_crawled = 0

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(pipeline.spider_opened, signal=signals.spider_closed)
        return pipeline

    def spider_opened(self, spider: ZoodMallSpider):
        pass

    def spider_closed(self, spider: ZoodMallSpider):
        self.save_products()

    def save_products(self):
        items, self.items = self.items, []

    def process_item(self, item, spider: ZoodMallSpider):
        self.items.append(item)
        self.pages_crawled += 1
        if len(self.item) >= 100:
            self.save_products()
        return item
