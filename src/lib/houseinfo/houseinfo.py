from unittest import expectedFailure
import falcon
from falcon import media
import json
import functools

import lib.assemblers as assemblers

# https://falcon.readthedocs.io/en/stable/user/recipes/pretty-json.html
json_handler = media.JSONHandler(
    dumps=functools.partial(json.dumps, indent=4, sort_keys=True),
)



class HouseInfo():
    def __init__(self, connection) -> None:
        self.connection = connection

    def on_get(self, req, resp):
        """
        Handles GET requests
        ---
        description: Gets building information
        responses:
            200:
                description: JSON blob
        """
        # print(req)
        # print(req.params)
        resp.media_handler = json_handler

        # extract and sanitize address parameter
        try:
            address = req.params["address"]
        except KeyError:
            resp.status = falcon.HTTP_400
            resp.media = {
                "error": "address field required."
            }
            return 0

        # extract and sanitize angle parameter
        try:
            angle = req.params["angle"]

            try:
                angle = float(angle)
            except ValueError:
                resp.status = falcon.HTTP_400
                resp.media = {
                    "error": "angle must be numeric."
                }
                return 0

            if angle < 0 or angle > 90:
                resp.status = falcon.HTTP_400
                resp.media = {
                    "error": "angle must be between 0 and 90."
                }
                return 0

        except KeyError:
            angle = None



        # extract and sanitize aspect parameter
        try:
            aspect = req.params["aspect"]
            try:
                aspect = float(aspect)
            except ValueError:
                resp.status = falcon.HTTP_400
                resp.media = {
                    "error": "aspect must be numeric."
                }
                return 0

        except KeyError:
            aspect = None

        output = assemblers.get_house_info(self.connection, address, angle, aspect)

        if output==None:
            resp.status = falcon.HTTP_404
            resp.media = {
                "error": "No data found for this address."
            }
        else:
            resp.media = output
            resp.media_handler = json_handler


if __name__=="__main__":
    pass

