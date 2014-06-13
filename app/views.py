from flask import render_template, redirect, url_for
from forms import LoginForm
from app import app, host, port, user, passwd, db
from app.helpers.database import con_db


# To create a database connection, add the following
# within your view functions:
# con = con_db(host, port, user, passwd, db)

# ROUTING/VIEW FUNCTIONS
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    # Renders index.html.
    form = LoginForm()
    if form.validate_on_submit():
        home_addr = form.home.data
        cat1 = form.cat1.data
        cat2 = form.cat2.data
        cat3 = form.cat3.data
        cat4 = form.cat4.data
#         print '\n', home_addr, cat1, cat2, cat3, cat4, '\n'
        return redirect(url_for('results',home_addr=home_addr, cat1=cat1, cat2=cat2, cat3=cat3, cat4=cat4))
    return render_template('index.html', form = form)

@app.route('/home')
def home():
    # Renders home.html.
    return render_template('home.html')

@app.route('/slides')
def about():
    # Renders slides.html.
    return render_template('slides.html')

@app.route('/author')
def contact():
    # Renders author.html.
    return render_template('author.html')

@app.route('/results')
def results():
    # Renders author.html.
    return render_template('author.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
