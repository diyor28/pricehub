import re

from scrapy import Selector
from scrapy.http import HtmlResponse
from scrapy.spiders import SitemapSpider


class ZoodMallSpider(SitemapSpider):
    name = "zoodmall"
    allowed_domains = ["zoodmall.uz"]
    sitemap_urls = ["https://www.zoodmall.uz/sitemaps/sitemap_product.xml"]

    def start_requests(self):
        for request in super().start_requests():
            yield request

    def parse(self, response: HtmlResponse):
        selector: Selector = response.xpath("//div[@class='price__un_sale']/text()")[0]
        price_str = selector.get()
        digits = re.findall(r'\d', price_str)
        price = int(''.join(digits))
