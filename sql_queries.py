"""
Class for performing queries on the mysql database
"""
import pymysql
from access_keys import access_keys

database_name = 'Insight' 

class sql(object):
    
    def __init__(self):
#         self.conn = pymysql.connect(host='localhost', user='root')
        self.conn = pymysql.connect(host='insight.clzrh9aax7lr.us-east-1.rds.amazonaws.com', user=access_keys.amazon_rds_user, passwd = access_keys.amazon_rds_password)
        self.cursor = self.conn.cursor()
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
        #reconnect in case of a wait_timeout
        self.conn.ping(reconnect = True)
        self.cursor.execute(query)
        count = self.cursor.fetchall()
        count = count[0][0]
        return count > 0
    
    def _query_recommendations(self, ids):
        ids = tuple(ids)
        return """SELECT selected_yelp.id, name, latitude, longitude, prob, full_category, url
FROM    (SELECT id, name, latitude, longitude, url, prob
        FROM    (SELECT `to_id`, prob
                FROM next_dest
                WHERE from_id IN {ids}) as selected
        JOIN
        yelp ON to_id = yelp.id) as selected_yelp
JOIN categories
ON selected_yelp.id = categories.id
ORDER BY prob DESC""".format(ids = ids)
        

    def get_listings(self, start_lat, start_long, yelp_perc, entries, number = 6):
        """
        Returns the listings of locations closest to the specified location (start_lat, start_long)
        that belong to one of the categories. Number specifies the number of listings to return for
        each category
        """
        results = []
        lengths = []
        #reconnect in case of a wait_timeout
        self.conn.ping(reconnect = True)
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
    
    def get_recommendations(self, ids):
        query = self._query_recommendations(ids)
        #reconnect in case of a wait_timeout
        self.conn.ping(reconnect = True)
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        return data
        
        
    
if __name__ == '__main__':
    db = sql()
#     start_lat,start_long = 37.524968,-122.2508315
#     yelp_rating = 20#top percent
#     categories = ['Town','Department Stores','Grocery','Drugstores']
#     number = 6
#     listings, groups = db.get_listings(start_lat, start_long, yelp_rating, categories, number)
#     print listings, groups
    print db.get_recommendations(('town-san-carlos','100-sweet-cafe-san-francisco'))