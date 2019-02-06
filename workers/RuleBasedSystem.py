
from business_rules.variables import *
from business_rules.actions import *
from business_rules.fields import *
from business_rules import run_all

from workers.shared.BaseWorker import BaseWorker
from workers.shared.Variables import Variables
from workers.shared.Actions import Actions

################################################################################
class RuleBasedSystem(BaseWorker):

    # --------------------------------------------------------------------------
    def __init__(self):

        return

    # --------------------------------------------------------------------------
    def run(self, rules, variables, patient):

        # load variables and actions for rule;
        v = Variables(variables)
        a = Actions(patient)

        # if rule is not a list, wrap the rule in list;
        if isinstance(rules, dict):
            rules = [rules]

        # run all the rules given progressively;
        check = run_all(rule_list=rules, defined_variables=v, defined_actions=a, 
                stop_on_first_trigger=False)
        
        return a._patient
