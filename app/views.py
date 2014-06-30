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

@app.route('/prefetch/<x>')
def prefetch(x):
    all = hopper.get_categories_and_top()
    return json.dumps(all)

@app.route('/results/<entered>', methods=['GET', 'POST'])
def results(entered):
    entered = json.loads(entered)
    start_address, categories, yelp_perc  = sanitize_input(entered)
    start_lat,start_long = hopper.get_coordinates(start_address)
    if not hopper.in_bay_area(start_lat, start_long):
        raise InvalidUsage("Starting Location Not in Bay Area")
    try:
        locations = hopper.get_path(start_lat, start_long, yelp_perc, tuple(categories))
    except Exception as e:
        raise InvalidUsage(e)
    suggestion = hopper.get_recommended(locations)
    return render_template('results.html', locations = locations, start = (start_lat,start_long), suggestion=suggestion)

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
    return render_template('error.html', message = "Page ge Not Found (404).")

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', message = "An unexpected error has occurred (500).")
