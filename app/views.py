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

@app.route('/test')
def test():
    # Renders author.html.
    p = 'hi'
    return render_template('test.html', p = p)


@app.route('/results/<entered>', methods=['GET', 'POST'])
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
#     from decimal import Decimal
#     locations = [('us-post-office-redwood-city', 'US Post Office', 'Post Offices', '1100 Broadway St, Redwood City, CA 94063', 'http://s3-media4.ak.yelpcdn.com/bphoto/4IWF77Aim-Mv14WqU9-Kvg/ms.jpg', 6503684163, Decimal('3.0'), 'http://s3-media1.ak.yelpcdn.com/assets/2/www/img/e8b5b79d37ed/ico/stars/v1/stars_large_3.png', 'http://www.yelp.com/biz/us-post-office-redwood-city', Decimal('37.486870'), Decimal('-122.213076'), 0.054810246651515813, 143.0), ('cvs-palo-alto', 'CVS', 'Drugstores', '2701 Middlefield Rd, Palo Alto, CA 94306', 'http://s3-media4.ak.yelpcdn.com/bphoto/D7MO0hLgNGbceHG3W8tfNQ/ms.jpg', 6503300128, Decimal('2.5'), 'http://s3-media2.ak.yelpcdn.com/assets/2/www/img/d63e3add9901/ico/stars/v1/stars_large_2_half.png', 'http://www.yelp.com/biz/cvs-palo-alto', Decimal('37.433398'), Decimal('-122.129310'), 0.1498129047645763, 8.0), ('provident-credit-union-redwood-city-3', 'Provident Credit Union', 'Banks & Credit Unions', '210 Redwood Shores Pkwy., Redwood City, CA 94065', 'http://s3-media1.ak.yelpcdn.com/bphoto/Ktx27whU5N3WfPx6VA6hmA/ms.jpg', 6505917845, Decimal('3.0'), 'http://s3-media1.ak.yelpcdn.com/assets/2/www/img/e8b5b79d37ed/ico/stars/v1/stars_large_3.png', 'http://www.yelp.com/biz/provident-credit-union-redwood-city-3', Decimal('37.521574'), Decimal('-122.252761'), 0.01877868432558575, 719.0), ('starbucks-redwood-city', 'Starbucks', 'Coffee & Tea', '264 Redwood Shores Pkwy, Redwood City, CA 94065', 'http://s3-media1.ak.yelpcdn.com/bphoto/zeIMAGeSkaxMndn4f0kZhw/ms.jpg', 6506544037, Decimal('3.0'), 'http://s3-media1.ak.yelpcdn.com/assets/2/www/img/e8b5b79d37ed/ico/stars/v1/stars_large_3.png', 'http://www.yelp.com/biz/starbucks-redwood-city', Decimal('37.521648'), Decimal('-122.252796'), 0.018751088341746994, 1441.0)]
    return render_template('results.html', locations = locations, start = (start_lat,start_long))

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
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
