
import unittest
import sys
from os import path
import requests

sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from lib.DB import DB
import conf

################################################################################
class PatientVariableEndpointTest(unittest.TestCase):

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
    def postVariableValue(self, variable_id, value):

        return self.requestAPI("/v0/patient/variable", method="POST", data={
            "id": variable_id,
            "value": value
        })

    # --------------------------------------------------------------------------
    def getVariableValue(self, variable_id):

        return self.requestAPI("/v0/patient/variable?id="+variable_id, method="GET")

    # --------------------------------------------------------------------------
    def testVariableEndpoint(self):

        print("\n==========================================\n  testVariableEndpoint")

        self.resetPatient()
        print("  => Resetting patient... done.")

        # get a variable that doesn't have a value yet;
        res = self.getVariableValue("mmse_attention_calculation")
        self.assertEqual(res["success"], False)
        self.assertEqual(res["message"], "Patient has no submitted variable 'mmse_attention_calculation'.")
        print("  => Get a not set variable... done.")

        # add a valid value;
        res = self.postVariableValue("mmse_attention_calculation", 1)
        self.assertEqual(res["success"], True)
        print("  => Posting value... done.")

        # double post a value; check spam prevention;
        res = self.postVariableValue("mmse_attention_calculation", 1)
        self.assertEqual(res["success"], False)
        self.assertEqual(res["message"], "The last submission for 'mmse_attention_calculation' is still active.")
        print("  => Double posting value... done.")

        # get the value as expected;
        res = self.getVariableValue("mmse_attention_calculation")
        self.assertEqual(res["success"], True)
        self.assertEqual("values" in res["result"], True)
        self.assertEqual(len(res["result"]["values"]), 1)
        self.assertEqual("value" in res["result"]["values"][0], True)
        self.assertEqual(res["result"]["values"][0]["value"], 1)
        print("  => Get values... done.")

        # get a non existant variable;
        res = self.getVariableValue("mmse_madeup")
        self.assertEqual(res["success"], False)
        self.assertEqual(res["message"], "Variable 'mmse_madeup' is not a valid variable.")
        print("  => Get non existant value... done.")

        # post a non existant variable;
        res = self.postVariableValue("mmse_madeup", 1)
        self.assertEqual(res["success"], False)
        self.assertEqual(res["message"], "Variable 'mmse_madeup' is not a valid variable.")
        print("  => Post to a non existant variable... done.")

        # post a non postable value;
        res = self.postVariableValue("mmse_total", 25)
        self.assertEqual(res["success"], False)
        self.assertEqual(res["message"], "'mmse_total' can only be populated automatically.")
        print("  => Post a logic value... done.")

################################################################################
if __name__ == '__main__':
    unittest.main()
