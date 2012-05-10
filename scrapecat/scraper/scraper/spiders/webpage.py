from scrapy.spider import BaseSpider
from scrapecat import models


class WebpageSpider(BaseSpider):
    name = 'webpage'

    def parse(self, response):
        item = models.Webpage()
