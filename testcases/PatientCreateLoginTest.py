
import unittest
import sys
from os import path
import requests

sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from lib.DB import DB
import conf

################################################################################
class PatientCreateLoginTest(unittest.TestCase):

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
    def requestFaultyAPI(self, uri, data={}, headers={}, method="POST"):
        if method == "POST": req = requests.post(self._base_url + uri, data=data, headers=headers)
        if method == "GET": req = requests.get(self._base_url + uri, data=data, headers=headers)
        return req.json()

    # --------------------------------------------------------------------------
    def createPatient(self, hhash):

        return self.requestAPI("/v0/patient/create", method="POST", data={
            "hash": hhash
        })

    # --------------------------------------------------------------------------
    def loginPatient(self, hhash, patient_id):

        return self.requestAPI("/v0/patient/login", method="POST", data={
            "hash": hhash,
            "patient_id": patient_id
        })

    # --------------------------------------------------------------------------
    def postVariableValue(self, variable_id, value):

        return self.requestAPI("/v0/patient/variable", method="POST", data={
            "id": variable_id,
            "value": value
        })

    # --------------------------------------------------------------------------
    def postVariableValueFaulty(self, variable_id, value, headers={}):

        return self.requestFaultyAPI("/v0/patient/variable", method="POST", data={
            "id": variable_id,
            "value": value
        }, headers=headers)

    # --------------------------------------------------------------------------
    def testPatientCreateLogin(self):

        print("\n==========================================\n  testPatientCreateLogin")

        # create a new patient;
        patient = self.createPatient("testhash")
        self.assertEqual(patient["success"], True)
        self._patient_id = patient["result"]
        print("  => Creating new patient ("+self._patient_id+")... done.")

        # check if patient in DB;
        loaded_patient = self._db.getPatient(self._patient_id)
        self.assertNotEqual(loaded_patient, False)
        print("  => Checking if patient in DB... done.")

        # login wrong patient;
        session = self.loginPatient("testhash", "test_id_that_doesnt_exist")
        self.assertEqual(session["success"], False)
        self.assertEqual(session["message"], "Credentials not correct.")
        print("  => Creating faulty session (1)... done.")

        # login wrong patient;
        session = self.loginPatient("not_the_right_hash", self._patient_id)
        self.assertEqual(session["success"], False)
        self.assertEqual(session["message"], "Credentials not correct.")
        print("  => Creating faulty session (2)... done.")

        # login patient;
        session = self.loginPatient("testhash", self._patient_id)
        self.assertEqual(session["success"], True)
        self._patient_session = session["result"]
        print("  => Creating patient session... done.")

        # test faulty authentications;
        res = self.postVariableValueFaulty("mmse_attention_calculation", 1)
        self.assertEqual(res["success"], False)
        self.assertEqual(res["message"], "Invalid header. Request registered.")
        res = self.postVariableValueFaulty("mmse_attention_calculation", 1, headers={
            "Authorization": self._patient_session
        })
        self.assertEqual(res["success"], False)
        self.assertEqual(res["message"], "Invalid authentication. Request registered.")
        res = self.postVariableValueFaulty("mmse_attention_calculation", 1, headers={
            "Authorization": "Code "+self._patient_session
        })
        self.assertEqual(res["success"], False)
        self.assertEqual(res["message"], "Invalid authentication. Request registered.")
        res = self.postVariableValueFaulty("mmse_attention_calculation", 1, headers={
            "Authorization": "Bearer " + self._patient_session
        })
        self.assertEqual(res["success"], False)
        self.assertEqual(res["message"], "Invalid authentication. Request registered.")
        res = self.postVariableValueFaulty("mmse_attention_calculation", 1, headers={
            "Authorization": "Bearer ",
            "Patient": ""
        })
        self.assertEqual(res["success"], False)
        self.assertEqual(res["message"], "Invalid authentication. Request registered.")
        res = self.postVariableValueFaulty("mmse_attention_calculation", 1, headers={
            "Authorization": "Bearer wsi53kOhZ6UIfZZ6PbYXO8lm0Qe8FyXC64vlo7gRysBNrt/HBt6dLt0aEXaywF/J3i8vZKJPHuPYeYlei07Nag==",
            "Patient": self._patient_id
        })
        self.assertEqual(res["success"], False)
        self.assertEqual(res["message"], "Invalid authentication. Request registered.")
        res = self.postVariableValueFaulty("mmse_attention_calculation", 1, headers={
            "Authorization": "Bearer wsi53kOhZ6UIfZZ6PbYXO8lm0Qe8FyXC64vlo7gRysBNrt/HBt6dLt0aEXaywF/J3i8vZKJPHuPYeYlei07Nag==",
            "Patient": self._patient_id
        })
        self.assertEqual(res["success"], False)
        self.assertEqual(res["message"], "Invalid authentication. Request registered.")
        print("  => Posting faulty value... done.")

        # test posting to a variable;
        res = self.postVariableValueFaulty("mmse_attention_calculation", 1, headers={
            "Authorization": "Bearer " + self._patient_session,
            "Patient": self._patient_id
        })
        self.assertEqual(res["success"], True)
        print("  => Posting value... done.")

        # delete patient from DB;
        self._db.delete("sessions", {"session_id": self._patient_session})
        self._db.delete("patients", {"patient_id": self._patient_id})
        print("  => Cleanup changes... done.")

################################################################################
if __name__ == '__main__':
    unittest.main()
