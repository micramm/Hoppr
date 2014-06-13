from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, SelectField
from wtforms.validators import Required
 
class LoginForm(Form):
    home = TextField('home', validators = [Required()])
    cat1 = TextField('cat1', validators = [Required()])
    cat2 = TextField('cat2', validators = [Required()])
    cat3 = TextField('cat3', validators = [Required()])
    cat4 = TextField('cat3', validators = [Required()])