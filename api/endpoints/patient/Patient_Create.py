
from flask import request
from api.endpoints.shared.BaseEndpoint import BaseEndpoint
import uuid

class Patient_Create(BaseEndpoint):

    # --------------------------------------------------------------------------
    def createPatientID(self):

        return str(uuid.uuid4())

    # --------------------------------------------------------------------------
    def post(self):

        # check for the required parameters and see if they are valid;
        form_fields = request.form
        if "hash" not in form_fields:
            return self.returnError("POST", "This is not correct.")

        # create a new patient by a unique ID;
        patient_id = self.createPatientID()
        check = self._db.find("patients", {"patient_id": patient_id})
        while check:
            patient_id = self.createPatientID()
            check = self._db.find("patients", {"patient_id": patient_id})

        # hash the password, and save to table;
        hhash = self._crypto.hashValue(form_fields["hash"])
        check = self._db.createPatient(patient_id, hhash)
        if not check: return self.returnError("POST", "Could not create patient.")
        return self.returnResult("POST", patient_id)
