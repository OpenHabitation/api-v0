import falcon
from falcon import media
import json
import functools

# https://falcon.readthedocs.io/en/stable/user/recipes/pretty-json.html
json_handler = media.JSONHandler(
    dumps=functools.partial(json.dumps, indent=4, sort_keys=True),
)



class AddressSearch():
    """
    Providing address suggestions based on pattern matching
    """

    def __init__(self, connection):
        self.connection = connection # database connection object

    def on_get(self, req, resp):

        try:
            pattern = req.params["term"]+"%%"
        except KeyError:
            resp.status = falcon.HTTP_400
            resp.text = "400 Bad Request"
            resp.content_type = falcon.MEDIA_TEXT
            return 0

        suggestions = getAddressSuggestions(self.connection, pattern, 15)
        # resp.content_type = falcon.MEDIA_JSON # not required
        resp.media = suggestions
        resp.media_handler = json_handler




def getAddressSuggestions(connection, pattern, limit):
    """Fetching address suggestions for a given search pattern

    Parameters
    ----------
    connection : psygopg2.connection
        psycopg2 connection object
    pattern : str
        search pattern
    limit : int
        maximum number of suggestions to return

    Returns
    -------
    list
        list of suggestions
    """

    cursor = connection.cursor()
    cursor.execute("select \"CompleteAddress\" from gwr where \"CompleteAddress\" ilike %(ilike)s order by \"CompleteAddress\" limit %(limit)s" , {"ilike":pattern, "limit":limit})
    suggestions = cursor.fetchall()
    suggestions = [i[0] for i in suggestions]

    return suggestions




if __name__=="__main__":
    pass