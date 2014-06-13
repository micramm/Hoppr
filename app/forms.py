from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, SelectField
from wtforms.validators import Required, Optional, Length

from access_keys import access_keys
 
class LoginForm(Form):
    home = TextField('home', validators = [Required()], default = access_keys.home_address)
    cat1 = TextField('cat1', validators = [Required()], default = 'cafes')
    cat2 = TextField('cat2', validators = [Required()], default = 'hair')
    cat3 = TextField('cat3', validators = [Required()], default = 'grocery')
    cat4 = TextField('cat4', validators = [Required()], default = 'lounges')
    yelp = SelectField('yelp', choices = [(str(1 + .5*i),str(1 + .5*i)) for i in range(8)])