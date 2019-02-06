
from flask import request
from api.endpoints.shared.BaseEndpoint import BaseEndpoint

class Patient_Rule(BaseEndpoint):

    # --------------------------------------------------------------------------
    def runRule(self, patient_id, rule_id):

        # check for the required parameters and see if they are valid;
        patient = self._db.getPatient(patient_id)
        if not patient: 
            return self.returnError("GET", "Patient could not be found.")

        rule = self._db.getRule(rule_id)
        if not rule:
            return self.returnError("POST", "Rule '"+rule_id+"' could not be found.")

        # check if (and which) variables are missing;
        check, missing = rule.detectMissingValues(patient)
        if not check:
            return self.returnError("POST", "Additional variables required.", {"missing": missing})

        # resolve the rule and report result;
        if rule.resolveRule(patient):
            return self.returnResult("POST", True)
        return self.returnResult("POST", False)

    # --------------------------------------------------------------------------
    def post(self):

        # check for the required parameters and see if they are valid;
        if "id" not in request.form:
            return self.returnError("POST", "Parameter 'id' required.")

        return self.runRule(request.patient_id, request.form["id"])
