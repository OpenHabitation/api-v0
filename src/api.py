from email.headerregistry import Address
import falcon
import os
import psycopg2 as pg
import dotenv

from lib.addresssearch.addressearch import AddressSearch
from lib.houseinfo.houseinfo import HouseInfo



dotenv.load_dotenv()


# create database connection
# -----------------------------------------------------------------------------------------------------
if True: # make code collapsable

    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    username = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    database = "openhabitation"

    connection = pg.connect(database=database, user=username, password=password, host=host, port=port)
# -----------------------------------------------------------------------------------------------------




app = application = falcon.App()


AddressSearchResource = AddressSearch(connection)
app.add_route("/api/v0/addresssearch", AddressSearchResource)

HouseInfoResource = HouseInfo(connection)
app.add_route("/api/v0/houseinfo", HouseInfoResource)





if __name__ == '__main__':

    from wsgiref.simple_server import make_server

    with make_server('', 8000, application) as httpd:
        print('Serving on http://localhost:8000')
        httpd.serve_forever()