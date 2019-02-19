
import unittest
import sys
from os import path

sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from testcases.MathWorkerTest import MathWorkerTest
from testcases.PatientCreateLoginTest import PatientCreateLoginTest
from testcases.PatientObjTest import PatientObjTest
from testcases.PatientOrderSystemTest import PatientOrderSystemTest
from testcases.PatientVariableEndpointTest import PatientVariableEndpointTest

tests = []
tests.append(unittest.TestLoader().loadTestsFromTestCase(MathWorkerTest))
tests.append(unittest.TestLoader().loadTestsFromTestCase(PatientCreateLoginTest))
tests.append(unittest.TestLoader().loadTestsFromTestCase(PatientObjTest))
tests.append(unittest.TestLoader().loadTestsFromTestCase(PatientOrderSystemTest))
tests.append(unittest.TestLoader().loadTestsFromTestCase(PatientVariableEndpointTest))

if __name__ == '__main__':
    test_all = unittest.TestSuite(tests)
    unittest.TextTestRunner(verbosity=0).run(test_all)
