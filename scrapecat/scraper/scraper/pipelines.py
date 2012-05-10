from scrapecat import models


class MongoPipeline(object):

    def process_item(self, item, spider):
        print item
        return item

