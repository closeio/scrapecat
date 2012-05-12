import os
import json
import datetime
import requests

from flask.ext.celery import Celery

from scrapecat import app, models, plugins


celery = Celery(app)

def is_webpage_cached(webpage):
    return webpage and webpage.date_updated > (datetime.datetime.now() - datetime.timedelta(days=1)) 

@celery.task(name="scrapecat.scraper.scrape")
def scrape(url, postback_url=None):
    success = False
    webpage = None
    response = {}

    try:
        webpage = models.Webpage.objects.get(url=url)
    except models.Webpage.DoesNotExist:
        print "no cached page"

    if not is_webpage_cached(webpage):
        print "updating the cache for ", url
        response = json.loads(os.popen('python scrapecat/ghost_fetch_url.py %s' % url).read())
    
        # todo do something with a bad resposne
 
        webpage = models.Webpage(url=url, headers=response['headers'], html=response['html'])
        
        from scrapecat import plugins2
        processor = plugins2.PluginProcessor()
        processor.register('contacts', plugins2.ContactPlugin)
        processor.init(webpage) 
        webpage.response = processor.process()
        webpage.save()
        
    else:
        print "using cached page for ", url
    
    success = True
    if postback_url:
        response = requests.post(postback_url, data=webpage.response if success else {"error": "your shit is fucked up, bitch!"})

    return success
    
