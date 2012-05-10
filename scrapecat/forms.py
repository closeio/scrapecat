from flaskext.wtf import Form
from flaskext.wtf.html5 import URLField
from wtforms.validators import url


class ScrapeRequestForm(Form):
    url = URLField(validators=[url()])    
