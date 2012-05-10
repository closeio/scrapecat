from scrapy.spider import BaseSpider
from scrapecat.scraper.scraper import items


class WebpageSpider(BaseSpider):
    name = 'webpage'

    def parse(self, response):
        item = items.Webpage()
        item['url'] = response.url
        item['html'] = response.body_as_unicode()
        item['headers'] = response.headers
        return item
        
