import datetime
from mongoengine import *

class DocumentBase(Document):
    date_created = DateTimeField()
    date_updated = DateTimeField()

    def save(self, *args, **kwargs):
        if not self.date_created:
            self.date_created = datetime.datetime.now()
        self.date_updated = datetime.datetime.now()
        return super(DocumentBase, self).save(*args, **kwargs)

class Webpage(DocumentBase):
    url = URLField()
    headers = DictField()
    html = StringField()
