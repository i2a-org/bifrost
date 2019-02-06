
from flask import request
from api.endpoints.shared.BaseEndpoint import BaseEndpoint

class Search_Action(BaseEndpoint):
    """ Search_Action.py """

    # --------------------------------------------------------------------------
    def get(self): 

        # search for an action (either by a search query, or return all of them);
        res = []
        if "s" not in request.args:
            res = self._db.searchAction()
        else:
            res = self._db.searchAction(request.args["s"])

        if not res: return self.returnError("GET", "Could not find any actions.")
        return self.returnResult("GET", res, add={
            "s": "" if "s" not in request.args else request.args["s"]
        })
