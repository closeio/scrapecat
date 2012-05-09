from mongoengine import *


class DocumentBase(Document):
    date_created = DateTimeField()
    date_updated = DateTimeField()

    def save(self, *args, **kwargs):
        if not self.creation_date:
            self.date_created = datetime.datetime.now()
        self.date_updated = datetime.datetime.now()
        return super(DocumentBase, self).save(*args, **kwargs)


class WebPage(DocumentBase):
    url = URLField()
    
