import os
import logging

from scrapecat import app
from flask import request, jsonify
from plugins import ContactPlugin

logging.basicConfig(level=logging.DEBUG)
@app.route('/')
def index():
    return "ScrapeCat!"

@app.route('/scrape')
def scrape():
    if not request.args.get('url', False):
        jsonify(success=False, error='No URL supplied')
    else:
        url = str(request.args.get('url'))
        output = os.popen('python scrapecat/plugins.py %s' % url)
        return output.read()
