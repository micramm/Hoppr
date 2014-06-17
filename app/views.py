from flask import render_template, redirect, url_for
from forms import LoginForm
from app import app, host, port, user, passwd, db
from app.helpers.database import con_db
#functionality-related packages
from hopper import hopper
hopper = hopper()

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
        yelp = form.yelp.data
        return redirect(url_for('results',home_addr=home_addr, cat1=cat1, cat2=cat2, cat3=cat3, cat4=cat4,yelp_rating=yelp))
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
    return render_template('map.html')

@app.route('/results/<home_addr>_<cat1>_<cat2>_<cat3>_<cat4>_<yelp_rating>')
def results(home_addr, cat1, cat2, cat3, cat4, yelp_rating):
    start_lat,start_long = hopper.get_coordinates(home_addr)
    categories = [cat1, cat2, cat3, cat4]
    print 'getting locations'
    locations = hopper.get_path(start_lat, start_long, yelp_rating, categories)
    print 'got locations!'
    loc1,loc2,loc3,loc4 = locations
    url = 'https://www.google.com/maps/dir/' + home_addr +'/' + loc1[3] + '/' + loc2[3] + '/' + loc3[3] + '/' + loc4[3] + '/' + home_addr
    return render_template('results.html', loc0 = home_addr, loc1 = loc1[1:4], loc2 = loc2[1:4], loc3=loc3[1:4], loc4=loc4[1:4], url = url)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
