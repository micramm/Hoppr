from flask import render_template, redirect
from app import app
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

@app.route('/slides')
def about():
    # Renders slides.html.
    return render_template('slides.html')

@app.route('/author')
def contact():
    # Renders author.html.
    return redirect("http://www.michael-ramm.com", code=302) 

@app.route('/results/<entered>')
def results(entered):
    entered = json.loads(entered)
    start_address, categories, yelp_perc  = sanitize_input(entered)
    start_lat,start_long = hopper.get_coordinates(start_address)
    if not hopper.in_bay_area(start_lat, start_long):
        raise InvalidUsage("Starting Location Not in Bay Area")
    try:
        locations = hopper.get_path(start_lat, start_long, yelp_perc, categories)
    except Exception as e:
        raise InvalidUsage(e)
    else:
        print locations
    return ''

def sanitize_input(entered):
    start = entered.get("start", None)
    if start is None or start == "":
        raise InvalidUsage("No Starting Location")
    yelp_rating = entered.get("yelp_rating", None)
    if yelp_rating is None:
        raise InvalidUsage("No Yelp Rating")
    #extracts the percentage from the string
    try:
        yelp_rating = int(yelp_rating[-3:-1])
    except ValueError:
        yelp_rating = 100
    #append all categories that may be listed under keys '0' through '3'
    categories = []
    for i in range(4):
        dest = entered.get(str(i), None)
        if dest is not None:
            categories.append(dest)
    if len(categories) == 0:
        raise InvalidUsage("No destinations")
    return start, categories, yelp_rating 


#         
#         print 'got locations!'
#         loc1,loc2,loc3,loc4 = locations
#         url = 'https://www.google.com/maps/dir/' + home_addr +'/' + loc1[3] + '/' + loc2[3] + '/' + loc3[3] + '/' + loc4[3] + '/' + home_addr
#         return render_template('results.html', loc0 = home_addr, loc1 = loc1[1:4], loc2 = loc2[1:4], loc3=loc3[1:4], loc4=loc4[1:4], url = url)

class InvalidUsage(Exception):
    """Class for handling excpetions"""
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv
    
@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = error.to_dict()
    message = response.get('message', '')
    return render_template('error.html', message = message)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
