import os
import asyncio
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import aiohttp

from .spiders.zoodmall import ZoodMallSpider


class ZoodmallPipeline:
    items: list[dict]

    def __init__(self, *args, **kwargs):
        self.items = []
        self.pages_crawled = 0
        self.data_file = None

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signal=signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        if not os.path.exists("data"):
            os.makedirs("data")

        data_file_path = "data/data.txt"
        if os.path.exists(data_file_path):
            os.remove(data_file_path)

        self.data_file = open(data_file_path, "a")

    def spider_closed(self, spider: ZoodMallSpider):
        self.data_file.close()

    def save_products(self):
        lines = []
        for item in self.items:
            line = f'{item["title"]}|{item["price"]}|{item["sku"]}|{item["photo"]}|{item["url"]}\n'
            lines.append(line)
        self.data_file.write(''.join(lines))
        self.items.clear()

    def process_item(self, item, spider):
        self.items.append(item)
        self.pages_crawled += 1
        if len(self.items) >= 100:
            self.save_products()
        return item


async def run_spider():
    process = CrawlerProcess(get_project_settings())
    spider = ZoodMallSpider()
    await process.crawl(spider)
    await process.join()


async def main():
    pipeline = ZoodmallPipeline()
    tasks = []

    async with aiohttp.ClientSession() as session:
        for _ in range(30):  # Run 30 concurrent tasks
            task = asyncio.create_task(run_spider())
            tasks.append(task)

        await asyncio.gather(*tasks)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
