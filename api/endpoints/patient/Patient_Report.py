

from flask import request
from api.endpoints.shared.BaseEndpoint import BaseEndpoint

class Patient_Report(BaseEndpoint):

    # --------------------------------------------------------------------------
    def get(self):

        # check for the required parameters and see if they are valid;
        if "id" not in request.args:
            return self.returnError("GET", "Parameter 'id' required.")
        
        report = self._db.searchReport(id=request.args["id"])
        if not report:
            return self.returnError("GET", "Report '"+request.args["id"]+"' is not valid.")
        report = report[0]

        patient = self._db.getPatient(request.patient_id)
        if not patient: 
            return self.returnError("GET", "Patient could not be found.")

        # get the most recent values for all the variables that are defined 
        # as required by the given report;
        rep = {
            "report_id": report["report_id"], 
            "name": report["name"], 
            "description": report["description"], 
            "refresh": False if "refresh" not in report else report["refresh"],
            "order": False if "order" not in report else report["order"],
            "values": patient.getMostRecentValues(report["variables"])
        }

        return self.returnResult("GET", rep)
