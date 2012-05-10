from scrapecat import app
from flask import request, jsonify
from plugins import BasePlugin

@app.route('/')
def index():
    return "ScrapeCat!"

@app.route('/scrape')
def scrape():
    if not request.args.get('url', False):
        jsonify(success=False, error='No URL supplied')
    else:
        p = BasePlugin(url=request.args.get('url'))
        return jsonify(**p.process)
