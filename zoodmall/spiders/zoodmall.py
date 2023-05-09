import json
import re

from scrapy.http import HtmlResponse
from scrapy.spiders import SitemapSpider

from pricehub.products import timeit


class ZoodMallSpider(SitemapSpider):
    name = "zoodmall"
    allowed_domains = ["zoodmall.uz"]
    sitemap_urls = ["https://www.zoodmall.uz/sitemaps/sitemap_product.xml"]

    def start_requests(self):
        for request in super().start_requests():
            yield request

    def parse(self, response: HtmlResponse):
        price_str: str = response.xpath("//div[@class='price__un_sale']/text()").get()
        digits = re.findall(r'\d', price_str)
        ld_json = response.xpath("//script[@type='application/ld+json'][contains(text(), 'sku')]/text()").get()
        ld_dict = json.loads(ld_json)
        price = int(''.join(digits))
        title = response.xpath("//h1/text()").get()
        sku = ld_dict['sku']
        photo_url = response.xpath("//meta[@property='og:image']/@content").get()
        return dict(price=price, title=title, sku=sku, photo_url=photo_url)
