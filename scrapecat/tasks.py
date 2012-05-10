import requests
from scrapecat import app, models
from flask.ext.celery import Celery


celery = Celery(app)

@celery.task(name="scrapecat.scraper.scrape")
def scrape(url, postback_url=None):
    success = False
    response = requests.get(url)     
    if response.status_code == 200:
        webpage = models.Webpage(url=response.url, headers=response.headers, html=response.text)
        webpage.save()
        
        #process the plugins

        success = True
    if postback_url:
        response = requests.post(postback_url, data=webpage if success else {"error": "your shit is fucked up, bitch!"})
    return success
    
