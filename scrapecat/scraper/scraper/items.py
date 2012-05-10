from scrapy.item import Item, Field


class Webpage(Item):
    url = Field()
    source = Field()
