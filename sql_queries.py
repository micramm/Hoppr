"""
Class for performing queries on the mysql database
"""
import pymysql
from access_keys import access_keys

database_name = 'Insight' 

class sql(object):
    
    def __init__(self):
        conn = pymysql.connect(host='localhost', user='root')
#         conn = pymysql.connect(host='insight.clzrh9aax7lr.us-east-1.rds.amazonaws.com', user='michaelramm', passwd = access_keys.amazon_rds_password)
        self.cursor = conn.cursor()
        self.cursor.execute("""USE {};""".format(database_name))
        
    def _query_category(self, latitude, longitude, category, yelp_perc, number):
        #returns number i.e 6 closest locations to the given lat/long point for a business in the provided category that is in the top perc of all businesses of that category 
        return """SELECT *
FROM 
(
    SELECT tbl.*, @counter := @counter +1 counter
    FROM (SELECT @counter:=0) initvar, 
                (SELECT categories.id as id, name, full_category, display_address, image_url, phone, rating, rating_image_url_large,                                                             url, latitude, longitude, SQRT(POW((latitude - {latitude}),2) + POW((longitude - {longitude}),2)) as distance
                FROM yelp
                JOIN categories
                on yelp.id = categories.id
                WHERE categories.full_category = "{category}") as tbl
    ORDER BY rating DESC) as X
WHERE counter <= CEILING({yelp_perc}/100 * @counter)
ORDER BY distance
LIMIT 6
""".format(category = category, latitude = latitude, longitude = longitude, number = number, yelp_perc = yelp_perc)

    def _query_name(self, latitude, longitude, name, yelp_perc, number):
        #same as _query_category for porbing business name
        return """SELECT *
FROM 
(
    SELECT tbl.*, @counter := @counter +1 counter
    FROM (SELECT @counter:=0) initvar, 
                (SELECT categories.id as id, name, full_category, display_address, image_url, phone, rating, rating_image_url_large,                                                             url, latitude, longitude, SQRT(POW((latitude - {latitude}),2) + POW((longitude - {longitude}),2)) as distance
                FROM yelp
                JOIN categories
                on yelp.id = categories.id
                WHERE yelp.name = "{name}") as tbl
    ORDER BY rating DESC) as X
WHERE counter <= CEILING({yelp_perc}/100 * @counter)
ORDER BY distance
LIMIT 6
""".format(name = name, latitude = latitude, longitude = longitude, number = number, yelp_perc = yelp_perc)

    def _is_a_category(self, text):
        #returns whether a given text is among categories
        query = """SELECT COUNT(*)
FROM categories 
WHERE categories.full_category = "{}"
""".format(text)
        self.cursor.execute(query)
        count = self.cursor.fetchall()
        count = count[0][0]
        return count > 0

    def get_listings(self, start_lat, start_long, yelp_perc, entries, number = 6):
        """
        Returns the listings of locations closest to the specified location (start_lat, start_long)
        that belong to one of the categories. Number specifies the number of listings to return for
        each category
        """
        results = []
        lengths = []    
        for entry in entries:
            if self._is_a_category(entry):
                query = self._query_category(start_lat, start_long, entry, yelp_perc, number)
            else:
                query = self._query_name(start_lat, start_long, entry, yelp_perc, number)
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            length = len(data)
            if not length:
                raise Exception("No locations found for entry {0}".format(entry))
            results.extend(data)
            lengths.append(length)
        return results, lengths
    
if __name__ == '__main__':
    db = sql()
    start_lat,start_long = 37.524968,-122.2508315
    yelp_rating = 20#top percent
    categories = ['Town','Department Stores','Grocery','Drugstores']
    number = 6
    listings, groups = db.get_listings(start_lat, start_long, yelp_rating, categories, number)
    print listings, groups