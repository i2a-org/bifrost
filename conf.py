
# endpoint includes
from api.endpoints.Ping import Ping

from api.endpoints.search.Search_Variable import Search_Variable
from api.endpoints.search.Search_Action import Search_Action
from api.endpoints.search.Search_Rule import Search_Rule
from api.endpoints.search.Search_Report import Search_Report

from api.endpoints.patient.Patient_Create import Patient_Create
from api.endpoints.patient.Patient_Login import Patient_Login
from api.endpoints.patient.Patient_Variable import Patient_Variable
from api.endpoints.patient.Patient_Rule import Patient_Rule
from api.endpoints.patient.Patient_Order import Patient_Order
from api.endpoints.patient.Patient_Report import Patient_Report

from api.endpoints.processing.Processing_Queue import Processing_Queue

# worker includes
from workers.RuleBasedSystem import RuleBasedSystem
from workers.SetWorker import SetWorker
from workers.MathWorker import MathWorker

#
# Definition of endpoint that Flask is using;
# 
_endpoints = {
    # test endpoints
    "/ping": Ping,
    # search endpoints
    "/search/variable": Search_Variable,
    #"/search/action": Search_Action,
    "/search/report": Search_Report,
    #"/search/rule": Search_Rule,
    # patient endpoints
    "/patient/create": Patient_Create,
    "/patient/login": Patient_Login,
    "/patient/variable": Patient_Variable,
    #"/patient/rule": Patient_Rule,
    "/patient/order": Patient_Order,
    "/patient/report": Patient_Report,
    # processing endpoints
    "/processing/queue": Processing_Queue
}

#
# Definition of endpoints that needs to be called with valid credentials;
#
_protected = {
    "/patient/variable": ["POST", "GET"],
    "/patient/rule": ["POST", "GET"],
    "/patient/order": ["POST", "GET"],
    "/patient/report": ["POST", "GET"]
}

#
# Workers that perform intensive backend calculations;
#
_workers = {
    "rule_based_system": RuleBasedSystem(),
    "set_worker": SetWorker(),
    "math_worker": MathWorker()
}
