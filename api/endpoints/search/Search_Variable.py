
from flask import request
from api.endpoints.shared.BaseEndpoint import BaseEndpoint

class Search_Variable(BaseEndpoint):
    """ Search_Variable.py """

    # --------------------------------------------------------------------------
    def get(self):

        # search for a variable (either by a search query, exact ID, or return all of them);
        res = []
        if "s" in request.args:
            res = self._db.searchVariable(term=request.args["s"])
        elif "id" in request.args:
            res = self._db.searchVariable(id=request.args["id"])
        else:
            res = self._db.searchVariable()

        if not res: return self.returnError("GET", "Could not find any variables.")
        
        return self.returnResult("GET", res, add={
            "s": "" if "s" not in request.args else request.args["s"]
        })
