
from flask import request
import time

from api.endpoints.shared.BaseEndpoint import BaseEndpoint

class Patient_Order(BaseEndpoint):
    """ Patient_Order.py """

    # --------------------------------------------------------------------------
    def post(self):

        # check for the required parameters and see if they are valid;
        if "id" not in request.form:
            return self.returnError("POST", "Parameter 'id' required.")

        patient = self._db.getPatient(request.patient_id)
        if not patient: 
            return self.returnError("POST", "Patient could not be found.")

        # check if report is already queued;
        if patient.reportIsQueued(request.form["id"]):
            return self.returnError("POST", "Report is already being processed.")
        print(patient["queue"])
        if "queue" in patient._patient_obj and patient["queue"] != {}:
            return self.returnError("POST", "A report is already being processed.")
        print("done")

        # get the report information;
        report = self._db.searchReport(id=request.form["id"])
        if not report:
            return self.returnError("POST", "Report '"+request.form["id"]+"' is not valid.")
        report = report[0]

        # check if report previously run AND check if the old report is still valid;
        if request.form["id"] in patient["reports"] and ( report["refresh"] == 0 or \
                int(time.time()) - patient["reports"][request.form["id"]] < report["refresh"] ):
            return self.returnError("POST", "Your report is still valid.")

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

        # prepare returned reports
        queue = {} if "queue" not in patient._patient_obj else patient._patient_obj["queue"]
        reports = {} if "reports" not in patient._patient_obj else patient._patient_obj["reports"]
        todos = []

        # get all the reports that can be completed at this time as well;
        if "todos" in request.args and request.args["todos"] == "true":

            # check all reports;
            rr = self._db.searchReport()
            for report in rr:

                # if report is already in other category, skip it;
                if report["report_id"] in queue or report["report_id"] in reports:
                    continue

                # check if the report even has a prerequesite;
                if "prereq" in report:
                    condition = {"conditions": report["prereq"]}
                    condition["actions"] = [{"name": "noop"}]
                    variables = {}
                    # get prerequesite variables, if they are not even present,
                    # skip the report (prereq can't be met to begin with);
                    if "prereq_variables" in report:
                        variables = patient.getMostRecentValues(report["prereq_variables"])
                        stop = False
                        for variable_id, data_type in report["prereq_variables"]:
                            if variable_id not in variables:
                                stop = True
                                break
                        if stop: continue
                    patient["prerequesites_passed"] = False
                    self._workers["rule_based_system"].run(condition, variables, patient)
                    if patient["prerequesites_passed"]: todos.append(report["report_id"])
                # if no prerequesite, add to queue;
                else:
                    todos.append(report["report_id"])

        # return all queued and finalized report;
        return self.returnResult("GET", {
            "queue": queue, 
            "reports": reports,
            "todo": todos
        })
