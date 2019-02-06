
from flask import request
from api.endpoints.shared.BaseEndpoint import BaseEndpoint

class Search_Rule(BaseEndpoint):
    """ Search_Rule.py """

    # --------------------------------------------------------------------------
    def get(self):

        # search for a report (either by a search query, exact ID, or return all of them);
        res = []
        if "s" in request.args:
            res = self._db.searchRule(term=request.args["s"])
        elif "id" in request.args:
            res = self._db.searchRule(id=request.args["id"])
        else:
            res = self._db.searchRule()
        if not res: return self.returnError("GET", "Could not find any actions.")

        # redact the returned fields (prevent stealing the rule definition);
        ret = []
        for rule in res:
            ret.append({
                "rule_id": rule["rule_id"], 
                "name": rule["name"], 
                "description": rule["description"],
                "variables": rule["variables"]
            })

        return self.returnResult("GET", ret, add={
            "s": "" if "s" not in request.args else request.args["s"]
        })
