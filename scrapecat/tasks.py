import datetime
import ghost
import requests
from scrapecat import app, models
from flask.ext.celery import Celery
from celery import signals


celery = Celery(app)

global _ghost

"""
def _init_ghosts(sender=None, conf=None, **kwargs):
    _ghost = ghost.Ghost()
    print "init_ghosts" 
 
signals.worker_ready.connect(_init_ghosts)
"""


@celery.task(name="scrapecat.scraper.scrape")
def scrape(url, postback_url=None):
    try:
        _ghost
    except NameError:
        _ghost = ghost.Ghost()

    success = False
    webpage = None
    try:
        webpage = models.Webpage.objects.get(url=url)
    except models.Webpage.DoesNotExist:
        print "no cached page"

    if not webpage or (webpage and webpage.date_created < (datetime.datetime.now() - datetime.timedelta(days=1))):
        print "refresh a cached page"
        print "start ghost open url"
        page, resources = _ghost.open(url)
        print "done opening url in ghost"
        if response.status_code != 200 and not webpage:
            print "status != 200 and no previously cached page"
            success = False    
        if response.status_code == 200:
            print "status == 200 and saving webpage"
            webpage = models.Webpage(url=page.url, headers=page.headers, html=ghost.main_frame.toHtml())
            webpage.save()
    else:
        print "using cached page!"
    
    #process the plugins

    success = True
    if postback_url:
        response = requests.post(postback_url, data=webpage if success else {"error": "your shit is fucked up, bitch!"})
    return success
    

