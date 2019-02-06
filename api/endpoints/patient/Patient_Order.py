
from flask import request
from api.endpoints.shared.BaseEndpoint import BaseEndpoint

class Patient_Order(BaseEndpoint):

    # --------------------------------------------------------------------------
    def post(self):

        # check for the required parameters and see if they are valid;
        if "id" not in request.form:
            return self.returnError("POST", "Parameter 'id' required.")

        report = self._db.searchReport(id=request.form["id"])
        if not report:
            return self.returnError("POST", "Report '"+request.form["id"]+"' is not valid.")
        report = report[0]

        patient = self._db.getPatient(request.patient_id)
        if not patient: 
            return self.returnError("POST", "Patient could not be found.")

        # check if report is already queued;
        if patient.reportIsQueued(request.form["id"]):
            return self.returnError("POST", "Report is already being processed.")

        # go through all the rules in the report and determine all the missing values;
        missing_fields = []
        error_detected = False
        for rule_id in report["rules"]:

            rule = self._db.getRule(rule_id)
            if not rule:
                return self.returnError("POST", "Rule '"+rule_id+"' could not be found.")

            check, missing = rule.detectMissingValues(patient)
            if not check: error_detected = True
            for var in missing:
                if var not in missing_fields: missing_fields.append(var)

        # if values are missing, report;
        if error_detected: return self.returnError("POST", "Additional variables required.", {"missing": missing_fields})

        # otherwise, add report to the queue; handle errors;
        queue, queue_id = self._db.addQueue(request.patient_id, request.form["id"])
        if not queue: return self.returnError("POST", "Could not add report to queue.")
        patient.addQueuedReport(request.form["id"], queue_id)
        self._db.savePatient(patient)

        return self.returnResult("POST", queue_id)

    # --------------------------------------------------------------------------
    def get(self):

        # check for the required parameters and see if they are valid;
        patient = self._db.getPatient(request.patient_id)
        if not patient: 
            return self.returnError("POST", "Patient could not be found.")

        # return all queued and finalized report;
        return self.returnResult("GET", {
            "queue": ([] if "queue" not in patient._patient_obj else patient._patient_obj["queue"]), 
            "reports": ([] if "reports" not in patient._patient_obj else patient._patient_obj["reports"])
        })
