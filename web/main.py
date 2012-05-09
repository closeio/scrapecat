from flask import Flask
from flaskext.mongoengine import MongoEngine


app = Flask(__name__)
app.config.from_object('config')
db = MongoEngine(app)

@app.route('/')
def index():
    return "ScrapeCat!"

if __name__ == '__main__':
    app.run()



