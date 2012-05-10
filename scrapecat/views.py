import os
import logging

from scrapecat import app
from flask import request, jsonify, render_template, Response
from scrapecat import plugins
from scrapecat import forms

from plugins import ContactPlugin

def scrape_shit(url):
    print "start scrape_shit"
    from scrapecat.scraper import settings as scraper_settings 
    from scrapecat.scraper.spiders.webpage import WebpageSpider
    from scrapy.crawler import CrawlerProcess

    spider = WebpageSpider()
    spider.start_urls = [url]

    crawler = CrawlerProcess(scraper_settings)
    crawler.install()
    crawler.configure()
    crawler.queue.append_spider(spider)
    crawler.start()
    print "end scrape_shit"


logging.basicConfig(level=logging.DEBUG)
@app.route('/')
def index():
    form = forms.ScrapeRequestForm(request.form)
    if form.validate():
        url = form.url
        p = plugins.BasePlugin(url=url)
        return jsonify(**p.process)

    return render_template('index.html', form=form)

@app.route('/scrape/')
def scrape():
    if not request.args.get('url', False):
        jsonify(success=False, error='No URL supplied')
    else:
        url = str(request.args.get('url'))
        #scrape_shit(url)
        output = os.popen('python scrapecat/plugins.py %s' % url)
        return Response(response=output.read(), content_type='application/json')
