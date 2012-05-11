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
    
    meta = { 
        'allow_inheritance': True,
        'abstract': True,
    }

class Webpage(DocumentBase):
    url = URLField(primary_key=True, unique=True)
    headers = DictField()
    html = StringField()
    response = DictField() #cached response
