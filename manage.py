from flask.ext.script import Manager
from flask.ext.celery import install_commands as install_celery_commands

from scrapecat import app

manager = Manager(app)
install_celery_commands(manager)

if __name__ == "__main__":
    manager.run()
