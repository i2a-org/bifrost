
from flask import request
from api.endpoints.shared.BaseEndpoint import BaseEndpoint
import base64, M2Crypto

class Patient_Login(BaseEndpoint):

    # --------------------------------------------------------------------------
    def generateSession(self):

        return base64.b64encode(M2Crypto.m2.rand_bytes(64)).decode("utf8")

    # --------------------------------------------------------------------------
    def post(self):

        # check for the required parameters and see if they are valid;
        form_fields = request.form
        if "hash" not in form_fields or "patient_id" not in form_fields:
            return self.returnError("POST", "This is not correct.")

        patient = self._db.getPatient(form_fields["patient_id"])
        if not patient: return self.returnError("POST", "Credentials not correct.")

        hhash = self._crypto.hashValue(form_fields["hash"])
        if hhash != patient["hash"]: return self.returnError("POST", "Credentials not correct.")

        # generate a new session and save it in table;
        session_id = self.generateSession()
        check = self._db.addSession(session_id, patient["patient_id"])

        # return result;
        if not check: return self.returnError("POST", "Could not create session.")
        return self.returnResult("POST", session_id)
