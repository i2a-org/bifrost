
import unittest
import sys
from os import path
from decimal import *
import requests

sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from lib.DB import DB
import conf

################################################################################
class PatientOrderSystemTest(unittest.TestCase):

    _patient_id = "965ea4ff-4879-4021-aa94-701acb124c37"
    _patient_session = "wsi53kOhZ6UIfZZ6PbYXO8lm0Qe8FyXC64vlo7gRysBNrt/HBt6dLt0aEXaywF/J3i8vZKJPHuPYeYlei07Nag=="
    _base_url = "http://localhost:5000"
    _db = DB("dev", conf._workers)

    # --------------------------------------------------------------------------
    def requestAPI(self, uri, data={}, headers={}, method="POST"):
        headers["Authorization"] = "Bearer " + self._patient_session
        headers["Patient"] = self._patient_id
        if method == "POST": req = requests.post(self._base_url + uri, data=data, headers=headers)
        if method == "GET": req = requests.get(self._base_url + uri, data=data, headers=headers)
        return req.json()

    # --------------------------------------------------------------------------
    def resetPatient(self):

        patient = self._db.getPatient(self._patient_id)
        patient["variables"] = {}
        patient["queue"] = {}
        patient["reports"] = {}
        self._db.savePatient(patient)

    # --------------------------------------------------------------------------
    def getOrders(self):

        return self.requestAPI("/v0/patient/order?todos=true", method="GET")["result"]

    # --------------------------------------------------------------------------
    def orderReport(self, report_id):

        return self.requestAPI("/v0/patient/order", method="POST", data={"id": report_id})

    # --------------------------------------------------------------------------
    def getVariableDetails(self, variable_id):

        return self.requestAPI("/v0/search/variable?id="+variable_id, method="GET")

    # --------------------------------------------------------------------------
    def postVariableValue(self, variable_id, value):

        return self.requestAPI("/v0/patient/variable", method="POST", data={
            "id": variable_id,
            "value": value
        })

    # --------------------------------------------------------------------------
    def fillMissingVariables(self, missing):

        err = False

        for var in missing:
            vv = self.getVariableDetails(var)
            if len(vv["result"]) == 0:
                self.assertEqual("Could not get variable detail.", var)
                err = True
                continue
            #if vv["result"][0]["data_type"] == "select":
            res = self.postVariableValue(var, 1)
            if res["success"] == False:
                self.assertEqual("Could not set variable value.", var)
                err = True
            res = self.postVariableValue(var, 1)
            self.assertEqual(res["success"], False)
            self.assertEqual(res["message"], "The last submission for '"+var+"' is still active.")

    # --------------------------------------------------------------------------
    def processQueue(self):

        return self.requestAPI("/v0/processing/queue", method="POST", data={})

    # --------------------------------------------------------------------------
    def getReportDetails(self, report_id):

        return self.requestAPI("/v0/patient/report?id=" + report_id, method="GET", data={})

    # --------------------------------------------------------------------------
    def testPatientOrderSystem(self):

        print("\n==========================================\n  testPatientOrderSystem")

        self.resetPatient()
        print("  => Resetting patient... done.")

        orders = self.getOrders()
        next_report = orders["todo"][0]
        print("    Using: ", next_report)
        self.assertEqual(orders["todo"][0], "mmse")
        print("  => Getting next steps... done.")

        report_details = self.orderReport(next_report)
        self.assertEqual(report_details["message"], "Additional variables required.")
        missing_variables = report_details["missing"]
        print("    missing: ", missing_variables)
        print("  => Getting missing variables... done.")

        self.fillMissingVariables(missing_variables)
        print("  => Setting missing variable values... done.")

        report_details = self.orderReport(next_report)
        if not report_details["success"]: print("ERR:", report_details)
        self.assertEqual(report_details["success"], True)
        report_id = report_details["result"]
        report_details = self.orderReport(next_report)
        self.assertEqual(report_details["success"], False)
        self.assertEqual(report_details["message"], "Report is already being processed.")
        print("  => Ordering report... done.")

        processed = self.processQueue()
        if not processed["success"]: print("ERR:", processed)
        self.assertEqual(processed["success"], True)
        self.assertEqual(report_id in processed["result"], True)
        print("  => Processing report... done.")

        # TODO: test if report reordering is being blocked, because last report is still valid

        # test the /patient/report endpoint;
        report_values = self.getReportDetails("nonexisting_report")
        self.assertEqual(report_values["success"], False)
        self.assertEqual(report_values["message"], "Report 'nonexisting_report' is not valid.")

        report_values = self.getReportDetails(next_report)
        self.assertEqual(report_values["success"], True)
        self.assertEqual("mmse_total" in report_values["result"]["values"], True)
        self.assertEqual(report_values["result"]["values"]["mmse_total"][0], 11)
        print("  => Getting report values... done.")

        orders = self.getOrders()
        next_report = orders["todo"][0]
        print("    Using: ", next_report)


################################################################################
if __name__ == '__main__':
    unittest.main()
