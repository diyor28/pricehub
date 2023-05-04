from scrapy.spiders import Spider
from scrapy.spiders import SitemapSpider

class ZoodMallSpider(SitemapSpider):
    name = "zoodmall"
    allowed_domains = ["zoodmall.uz"]
    sitemap_urls = ["https://www.zoodmall.uz/sitemaps/sitemap_product.xml"]

    def start_requests(self):
        for request in super().start_requests():
            yield request

    def parse(self, response):
        print(response.url)
