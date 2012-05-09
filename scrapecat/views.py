from scrapecat import app


@app.route('/')
def index():
    return "ScrapeCat!"

