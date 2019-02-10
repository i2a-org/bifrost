
from business_rules.variables import *
from business_rules.actions import *
from business_rules.fields import *
from business_rules import run_all

from workers.shared.BaseWorker import BaseWorker
from workers.shared.Variables import Variables
from workers.shared.Actions import Actions

################################################################################
class SetWorker(BaseWorker):

    # --------------------------------------------------------------------------
    def __init__(self):

        return

    # --------------------------------------------------------------------------
    def transformSet(self, arr):

        # create a set from an array;
        return set(arr)

    # --------------------------------------------------------------------------
    def process(self, rule, variables, patient, v, a):

        # create both sets (set defined by the rule, and set given by patient);
        set_a = self.transformSet(getattr(v, rule["setop"]["name"])())
        set_b = self.transformSet(rule["setop"]["value"])
        
        # run the set operations as defined in the rule;
        res = None
        if rule["setop"]["operator"] == "intersect": res = set_a.intersection(set_b)
        elif rule["setop"]["operator"] == "union": res = set_a.union(set_b)

        # run all the actions that were defined in the rule;
        for action in rule["actions"]:
            params = {}
            for key in action["params"]:
                params[key] = action["params"][key]
            params["values"] = list(res)
            getattr(a, action["name"])(**params)

    # --------------------------------------------------------------------------
    def run(self, rules, variables, patient):

        # load variables and actions for rule;
        v = Variables(variables)
        a = Actions(patient)

        # if rule is a list, work them off progressively;
        if isinstance(rules, list):
            for rule in rules: self.process(rule, variables, patient, v, a)
        else:
            self.process(rules, variables, patient, v, a)

        return a._patient
