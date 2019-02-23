
import unittest
import sys
from os import path
import requests

sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from lib.DB import DB
import conf

################################################################################
class PatientObjTest(unittest.TestCase):

    _patient = None
    _patient_id = "965ea4ff-4879-4021-aa94-701acb124c37"
    _patient_session = "wsi53kOhZ6UIfZZ6PbYXO8lm0Qe8FyXC64vlo7gRysBNrt/HBt6dLt0aEXaywF/J3i8vZKJPHuPYeYlei07Nag=="
    _base_url = "http://localhost:5000"
    _db = DB("dev", conf._workers)

    # --------------------------------------------------------------------------
    def resetPatient(self):

        self._patient = self._db.getPatient(self._patient_id)
        self._patient["variables"] = {}
        del self._patient["queue"]
        del self._patient["reports"]
        self._db.savePatient(self._patient)

    # --------------------------------------------------------------------------
    def addValue(self, variable_id, value, data_type="string"):

        self._patient.addValue(variable_id, value, data_type)

    # --------------------------------------------------------------------------
    def testPatientObj(self):

        print("\n==========================================\n  testPatientOrderSystem")

        self.resetPatient()
        print("  => Resetting patient... done.")

        values = [{
            "numeric_test": [100, "numeric"],
            "string_test": ["this is a test", "string"],
            "select_test": [["a","b","c","d"], "select"]
        },{
            "numeric_test": [-1, "numeric"],
            "string_test": ["this is another test", "string"],
            "select_test": [["w","x","y","z"], "select"]
        },{
            "numeric_test": [500, "numeric"],
            "string_test": ["test number 3", "string"],
            "select_test": [[0,1,2,3,4], "select"]
        }]

        # testing addValue() and getMostRecentValue();
        keys = {}
        for stack in values:
            for key in stack:
                self.addValue(key, stack[key][0], data_type=stack[key][1])
                keys[key] = stack[key][1]
            for key in stack:
                value, _, _ = self._patient.getMostRecentValue(key)
                self.assertEqual(value, stack[key][0])
        print("  => Creating and checking values... done.")

        # testing getMostRecentValues();
        val = []
        for key in keys: val.append([key, keys[key]])
        values_first = self._patient.getMostRecentValues(keys)
        values_second = self._patient.getMostRecentValues(val)
        self.assertEqual(values_first, values_second)
        print("  => Getting values as batch... done.")
        for key in values[-1]:
            self.assertEqual(values_first[key][0], values[-1][key][0])
            self.assertEqual(values_second[key][0], values[-1][key][0])
        print("  => Checking values as batch... done.")

        # testing assignment of object attributes;
        try:
            self._patient["test_arg"] = True
            self.assertEqual(self._patient["test_arg"], True)
        except:
            self.assertEqual("Obj setting", "Not working")
        print("  => Object assignments... done.")

        # extend a selection variable;
        values_to_add = [10,11,12,13]
        for val in values_to_add:
            self._patient.addSelectionToLast("select_test_two", val)
        values_to_add = [14,15,16,17]
        self._patient.addSelectionToLast("select_test_two", values_to_add)
        val, _, _ = self._patient.getMostRecentValue("select_test_two")
        self.assertEqual(len(self._patient["variables"]["select_test_two"]), 1)
        self.assertEqual(val, [10, 11, 12, 13, 14, 15, 16, 17])
        print("  => Extending a selection... done.")

        # test queueing;
        self.assertEqual(self._patient["queue"], False)
        self.assertEqual(self._patient.reportIsQueued("reportid"), False)
        self._patient.addQueuedReport("reportid", "queueid")
        self.assertEqual("reportid" in self._patient["queue"], True)
        self.assertEqual(self._patient["queue"]["reportid"], "queueid")
        self.assertEqual(self._patient.reportIsQueued("reportid"), True)
        self._patient.finalizeReport("reportid")
        self.assertEqual("reportid" in self._patient["queue"], False)
        self.assertEqual(self._patient.reportIsQueued("reportid"), False)
        self.assertEqual("reportid" in self._patient["reports"], True)
        print("  => Report queue... done.")

################################################################################
if __name__ == '__main__':
    unittest.main()
