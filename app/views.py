from flask import render_template, redirect, url_for
from app import app, host, port, user, passwd, db
from app.helpers.database import con_db
#functionality-related packages
from hopper import hopper
import json
hopper = hopper()


# ROUTING/VIEW FUNCTIONS
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    # Renders index.html.
    return render_template('index.html')

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
    return redirect("http://www.michael-ramm.com", code=302) 
#     return render_template('map.html')

@app.route('/results/<entered>')
def results(entered):
    try:
        #extract the entry fields from the passed form
        entered = json.loads(entered)
        yelp_rating = entered['yelp_rating']
        #home address has key '0'
        home_addr = entered['0']
        categories = []
        #append all categories that may be listed under keys '1' through '4'
        for i in range(1,5):
            selection = entered.get(str(i), None)
            if selection is not None:
                categories.append(selection)
    except Exception as e:
        return render_template('500.html'), 500
    else:
        start_lat,start_long = hopper.get_coordinates(home_addr)
        print start_lat, start_long
        print 'NOT GETTING YELP'
        print categories
        yelp_rating = 3.5
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
