import datetime
import ghost
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
        g = ghost.Ghost(wait_timeout=60)
        print "start ghost open url"
        page, resources = g.open(url)
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
    
