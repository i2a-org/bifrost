
from api.endpoints.shared.BaseEndpoint import BaseEndpoint

class Ping(BaseEndpoint):
    """ Ping.py """

    # --------------------------------------------------------------------------
    def get(self):
        """ The PING GET request hook

        Being called when a GET request was made to the endpoint. Returns a
        simple JSON response.

        Returns
        -------
        dict
            the dict with the custom JSON response
        """

        return self.returnResult("GET", "success")
