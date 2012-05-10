from scrapecat import models


class MongoPipeline(object):
    def __init__(self):
        pass

    def process_item(self, item, spider):
        webpage = models.Webpage(url=item['url'], headers=item['headers'], html=item['html'])
        webpage.save()

