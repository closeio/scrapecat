from scrapy.item import Item, Field


class Webpage(Item):
    url = Field()
    headers = Field()
    html = Field()
