import datetime
import os
import json
import requests
from scrapecat import app, models
from flask.ext.celery import Celery


celery = Celery(app)


@celery.task(name="scrapecat.scraper.scrape")
def scrape(url, postback_url=None):

    success = False
    webpage = None
    try:
        webpage = models.Webpage.objects.get(url=url)
    except models.Webpage.DoesNotExist:
        print "no cached page"

    if not webpage or (webpage and webpage.date_created < (datetime.datetime.now() - datetime.timedelta(days=1))):
        print "refresh a cached page"
        response = json.loads(os.popen('python scrapecat/ghost_fetch_url.py %s' % url).read())
        
        webpage = models.Webpage(url=url, headers=response.headers, html=response.html)
        webpage.save()
    else:
        print "using cached page!"
    
    #process the plugins

    success = True
    if postback_url:
        response = requests.post(postback_url, data=webpage if success else {"error": "your shit is fucked up, bitch!"})
    return success
    

