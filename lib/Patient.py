
import datetime
import time
from decimal import *
import json
import copy

################################################################################
class Patient:

    _patient_obj = None

    # --------------------------------------------------------------------------
    def __init__(self, patient_obj):

        self._patient_obj = patient_obj

    # --------------------------------------------------------------------------
    def __getitem__(self, index):

        if index in self._patient_obj: return self._patient_obj[index]
        return False

    # --------------------------------------------------------------------------
    def __delitem__(self, index):

        if index in self._patient_obj: del self._patient_obj[index]

    # --------------------------------------------------------------------------
    def __setitem__(self, index, value):

        self._patient_obj[index] = value

    # --------------------------------------------------------------------------
    def getMostRecentValue(self, key):

        # get t he most recent value of a given variable;
        date = 0
        date_index = -1
        available = self._patient_obj["variables"]
        if key not in available: return False, -1, -1

        # compare available dates with each other;
        for it in range(len(available[key])):
            if available[key][it]["timestamp"] > date:
                date = available[key][it]["timestamp"]
                date_index = it

        # deepcopy to prevent overwrite problems;
        return copy.deepcopy(available[key][it]["value"]), date, date_index

    # --------------------------------------------------------------------------
    def getMostRecentValues(self, variables):

        # get the most recent values of a list of variables;
        res = {}

        # iterate variables given in list;
        for elem in variables:
            if isinstance(variables, list):
                key, data_type = elem
            else:
                key = elem
                data_type = variables[elem]
            val, _, _ = self.getMostRecentValue(key)
            if val == False: continue
            if data_type == "numeric": val = float(val)
            res[key] = [val, data_type]

        return res

    # --------------------------------------------------------------------------
    def addValue(self, key, value, data_type="string"):

        # add a new value to a patient variable;
        try:
            # convert value to datatype (if given);
            if data_type == "numeric": value = Decimal(value)
            elif data_type == "select" or data_type == "select_multiple":
                if isinstance(value, str): value = json.loads(value.replace("; ", "\",\""))
                if not isinstance(value, list): value = [value]
            elif data_type == "boolean":
                value = True if value == "true" else False
        except:
            return False, "Value contained invalid data type."

        # append value and add modification to patient object;
        val = []
        if key in self._patient_obj["variables"]:
            val = self._patient_obj["variables"][key]
        val.append({"value": value, "timestamp": int(time.time())})
        self._patient_obj["variables"][key] = val

        return True, ""

    # --------------------------------------------------------------------------
    def addSelectionToLast(self, key, value, data_type="string"):

        # add a value to the last inserted value;
        # transforming that value into a selection field; "a" -> ["a","b"]
        try:
            if data_type == "numeric": value = Decimal(value)
            elif data_type == "boolean": value = True if value == "true" else False
        except:
            return False, "Value contained invalid data type."

        # get the most recent value;
        val, _, idx = self.getMostRecentValue(key)
        # if it could not be found, create it;
        if not val:
            self.addValue(key, [value], data_type="select")
        # otherwise add it to the selection;
        else:
            if isinstance(value, list):
                self._patient_obj["variables"][key][idx]["value"].extend(value)
            else:
                self._patient_obj["variables"][key][idx]["value"].append(value)

        return True, ""

    # --------------------------------------------------------------------------
    def addQueuedReport(self, report_id, queue_id):

        # mark the report as being processed;
        if "queue" not in self._patient_obj: self._patient_obj["queue"] = {}
        self._patient_obj["queue"][report_id] = queue_id

    # --------------------------------------------------------------------------
    def reportIsQueued(self, report_id):

        # check if the report is already queued;
        if "queue" not in self._patient_obj or report_id not in self._patient_obj["queue"]:
            return False
        return True

    # --------------------------------------------------------------------------
    def finalizeReport(self, report_id):

        # if not queued, quit;
        if "queue" not in self._patient_obj or report_id not in self._patient_obj["queue"]:
            return False, "No such report is queue."

        # otherwise, remove the report from "queue" object, ad mark it as a
        # finalized report (ready for viewing);
        if "reports" not in self._patient_obj: self._patient_obj["reports"] = {}
        self._patient_obj["reports"][report_id] = int(time.time())
        del self._patient_obj["queue"][report_id]
