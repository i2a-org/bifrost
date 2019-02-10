
from workers.shared.BaseWorker import BaseWorker
from workers.shared.Variables import Variables
from workers.shared.Actions import Actions
from functools import reduce

################################################################################
class MathWorker(BaseWorker):

    # --------------------------------------------------------------------------
    def __init__(self):

        return

    # --------------------------------------------------------------------------
    def transformSet(self, arr):

        # create a set from an array;
        return set(arr)

    # --------------------------------------------------------------------------
    def flattenList(self, k):

        result = list()
        for i in k:
            if isinstance(i,list):
                result.extend(self.flattenList(i)) #Recursive call
            else:
                result.append(i)
        return result

    # --------------------------------------------------------------------------
    def parse(self, val, v):

        if isinstance(val, str):

            #print("STR", val)
            return getattr(v, val)()

        elif isinstance(val, dict):

            #print("DICT", val)
            res = []
            for key in val:
                if key == "const":
                    res.append(val[key])
                    continue
                value = self.parse(val[key], v)
                #print("VAL", value)
                if key == "add":
                    #print("SUM", value)
                    res.append(sum(value))
                elif key == "mult":
                    #print("MULT", value)
                    res.append(reduce((lambda x, y: x * y), value))
                elif key == "sub":
                    res.append(reduce((lambda x, y: x - y), value))
                elif key == "div":
                    res.append(reduce((lambda x, y: x / y), value))
                elif key == "length":
                    res.append(len(value))
            return self.flattenList(res)

        elif isinstance(val, list):

            #print("LIST", val)
            res = []
            for var in val: res.append(self.parse(var, v))
            return self.flattenList(res)

    # --------------------------------------------------------------------------
    def process(self, rule, variables, patient, v, a):

        # do calculations;
        #print("MATH WORKER")
        res = self.parse(rule["setop"], v)
        if len(res) == 1: res = res[0]

        # run all the actions that were defined in the rule;
        for action in rule["actions"]:
            params = {}
            for key in action["params"]:
                params[key] = action["params"][key]
            params["value"] = res
            getattr(a, action["name"])(**params)

    # --------------------------------------------------------------------------
    def run(self, rules, variables, patient):

        #print("MATH WORKER")
        # load variables and actions for rule;
        v = Variables(variables)
        a = Actions(patient)

        # if rule is a list, work them off progressively;
        if isinstance(rules, list):
            for rule in rules: self.process(rule, variables, patient, v, a)
        else:
            self.process(rules, variables, patient, v, a)

        return a._patient
