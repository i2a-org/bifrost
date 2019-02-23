
import unittest
import sys
from os import path
from decimal import Decimal

sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from workers.MathWorker import MathWorker
from lib.Patient import Patient

################################################################################
class MathWorkerTest(unittest.TestCase):

    _worker = MathWorker()

    # --------------------------------------------------------------------------
    def testEasy(self):

        print("\n==========================================\n  testEasy")
        rule = {
            "variables": {
                "val1": "numeric", "val2": "numeric", "val3": "numeric"
            },
            "setop": {
                "add": [ "val1", "val2", "val3" ]
            },
            "actions": [ {
                "params": {
                    "variable_id": "mmse_total"
                },
                "name": "accept_numeric_variable"
            } ]
        }
        values = {
            "val1": [1, "numeric"],
            "val2": [1, "numeric"],
            "val3": [1, "numeric"]
        }
        patient = Patient({"variables": {}})
        self._worker.run(rule, values, patient)
        value, _, _ = patient.getMostRecentValue("mmse_total")
        print(" ", value, "=", Decimal(3))
        self.assertEqual(value, Decimal(3))

    # --------------------------------------------------------------------------
    def testMedium(self):

        print("\n==========================================\n  testMedium")
        rule = {
            "variables": {
                "val1": "numeric", "val2": "numeric", "val3": "numeric"
            },
            "setop": {
                "add": [
                    { "length": ["val1"] },
                    { "mult": {
                        "length": ["val2"],
                        "const": 2
                    } },
                    { "mult": {
                        "length": ["val3"],
                        "const": 3
                    } }
                ]
            },
            "actions": [ {
                "params": {
                    "variable_id": "mmse_total"
                },
                "name": "accept_numeric_variable"
            } ]
        }
        values = {
            "val1": [["a", "b", "c"], "select"],
            "val2": [["a"], "select"],
            "val3": [["a", "b"], "select"]
        }
        patient = Patient({"variables": {}})
        self._worker.run(rule, values, patient)
        value, _, _ = patient.getMostRecentValue("mmse_total")
        print(" ", value, "=", Decimal(11))
        self.assertEqual(value, Decimal(11))

################################################################################
if __name__ == '__main__':
    unittest.main()
