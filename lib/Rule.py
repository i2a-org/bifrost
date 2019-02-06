
import time

class Rule:

    _rule_obj = None
    _workers = None
    _db = None

    # --------------------------------------------------------------------------
    def __init__(self, rule_obj, workers, db):

        self._rule_obj = rule_obj
        self._workers = workers
        self._db = db

    # --------------------------------------------------------------------------
    def __getitem__(self, index):

        return self._rule_obj[index]

    # --------------------------------------------------------------------------
    def detectMissingValues(self, patient, use_refresh=True):

        # get all the variables that are required for rule;
        variables = self._rule_obj["variables"]

        # (1) go through all the required variables, and check if the patient has
        #     that variable set;
        # (2) variable is also considered missing, if the refresh threshold is
        #     passed (value is considered outdated and user will have to provide it
        #     again); 
        missing = {}
        for var in variables:
            val, date, date_index = patient.getMostRecentValue(var)
            variable = self._db.getVariable(var)
            if "refresh" not in variable: variable["refresh"] = 1000000000
            #print(val == False, val, int(time.time()) - date, variable["refresh"])
            #print((use_refresh and int(time.time()) - date >= variable["refresh"]))
            if val == False or not variable or (use_refresh and int(time.time()) - date >= variable["refresh"]):
                missing[var] = variables[var]

        if len(missing) > 0: return False, missing
        return True, missing

    # --------------------------------------------------------------------------
    def resolveRule(self, patient):

        try:
            # run the rule, as implemented by the according "worker";
            params = patient.getMostRecentValues(self._rule_obj["variables"])
            worker = ""
            if self._rule_obj["type"] == "logic": worker = "rule_based_system"   
            elif self._rule_obj["type"] == "set": worker = "set_worker"
            if worker == "": return False
            return self._workers[worker].run(self._rule_obj, params, patient)
        except:
            return False
