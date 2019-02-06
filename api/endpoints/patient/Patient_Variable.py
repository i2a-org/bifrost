

from flask import request
from api.endpoints.shared.BaseEndpoint import BaseEndpoint
import uuid
import time

class Patient_Variable(BaseEndpoint):

    # --------------------------------------------------------------------------
    def post(self):

        # check for the required parameters and see if they are valid;
        if "id" not in request.form or "value" not in request.form:
            return self.returnError("POST", "Parameters 'id' and 'value' are required.")

        variable = self._db.getVariable(request.form["id"])
        if not variable: 
            return self.returnError("POST", "Variable '"+request.form["id"]+"' is not a valid variable.")

        patient = self._db.getPatient(request.patient_id)
        if not patient: 
            return self.returnError("POST", "Patient could not be found.")

        # if all checks pass, add the value to the patient and save updates in DB;
        check, message = patient.addValue(request.form["id"], request.form["value"], variable["data_type"])
        if not check: return self.returnError("POST", message)
        val = patient["variables"][request.form["id"]]
        #check = self._db.addVariable(request.patient_id, request.form["id"], val)
        check = self._db.savePatient(patient)

        if not check: return self.returnError("POST", "Variable '"+request.form["id"]+"' could not be saved.")
        return self.returnResult("POST", val)

    # --------------------------------------------------------------------------
    def get(self):

        # check for the required parameters and see if they are valid;
        if "id" not in request.args: return self.returnError("GET", "Parameter 'id' required.")
        
        variable = self._db.getVariable(request.args["id"])
        if not variable: 
            return self.returnError("GET", "Variable '"+request.args["id"]+"' is not a valid variable.")

        patient = self._db.getPatient(request.patient_id)
        if not patient: 
            return self.returnError("GET", "Patient could not be found.")

        # if the variable has not been submitted, return error message;
        if request.args["id"] not in patient["variables"]:
            return self.returnError("GET", "Patient has not submitted variable '"+request.args["id"]+"'.")

        # otherwise, return all the values that have been submitted for variable;
        return self.returnResult("GET", {
            "data_type": variable["data_type"],
            "values": patient["variables"][request.args["id"]]
        })
