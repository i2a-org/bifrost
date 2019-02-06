
from flask import request
from api.endpoints.shared.BaseEndpoint import BaseEndpoint

class Search_Report(BaseEndpoint):
    """ Search_Report.py """

    # --------------------------------------------------------------------------
    def get(self):

        # search for a report (either by a search query, or return all of them);
        res = []
        if "s" not in request.args:
            res = self._db.searchReport()
        else:
            res = self._db.searchReport(request.args["s"])

        if not res: return self.returnError("GET", "Could not find any actions.")

        # redact the returned fields (prevent stealing the report definition);
        ret = []
        for report in res:
            ret.append({"report_id": report["report_id"], "name": report["name"], "description": report["description"]})

        return self.returnResult("GET", ret, add={
            "s": "" if "s" not in request.args else request.args["s"]
        })
