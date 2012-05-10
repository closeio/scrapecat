import os
import logging

from scrapecat import app
from flask import request, jsonify, render_template
from scrapecat import plugins
from scrapecat import forms

from plugins import ContactPlugin

logging.basicConfig(level=logging.DEBUG)
@app.route('/')
def index():
    form = forms.ScrapeRequestForm(request.form)
    if request.method == 'POST' and form.validate():
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
        output = os.popen('python scrapecat/plugins.py %s' % url)
        return output.read()
