from flask import Flask
from flaskext.mongoengine import MongoEngine


class ScrapeCatApp(Flask):
    def __init__(self, *args, **kwargs):
        settings = kwargs.pop('settings', 'scrapecat.config')
        super(ScrapeCatApp, self).__init__(__name__, *args, **kwargs)
        self.config.from_object(settings)
        self.db = MongoEngine(self)


app = ScrapeCatApp()

import scrapecat.views
