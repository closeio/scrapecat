import os
import logging

from scrapecat import app
from flask import request, jsonify, render_template, Response
from scrapecat import plugins, forms, tasks

from plugins import ContactPlugin



logging.basicConfig(level=logging.DEBUG)
@app.route('/')
def index():
    form = forms.ScrapeRequestForm(request.form)
    return render_template('index.html', form=form)


@app.route('/scrape/')
def scrape():
    if not request.args.get('url', False):
        jsonify(success=False, error='No URL supplied')
    else:
        url = str(request.args.get('url'))
        #tasks.scrape.apply_async((url,))       
        output = os.popen('python scrapecat/plugins.py %s' % url)
        return Response(response=output.read(), content_type='application/json')
