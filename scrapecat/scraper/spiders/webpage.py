from scrapy.spider import BaseSpider
from scrapy.contrib.spiders import Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapecat.scraper import items


class WebpageSpider(BaseSpider):
    name = 'webpage'

    """
    rules = (
        Rule(SgmlLinkExtractor(deny=('*', ))),
    )
    """

    def parse(self, response):
        item = items.Webpage()
        item['url'] = response.url
        item['html'] = response.body_as_unicode()
        item['headers'] = response.headers
        return item
        
