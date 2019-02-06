
from flask import request, jsonify
from flask_restful import Resource

class BaseEndpoint(Resource):
    """ BaseEndpoint.py """

    # --------------------------------------------------------------------------
    def __init__(self, logger, db, crypto, workers, request_string):
        
        self._db = db
        self._logger = logger
        self._crypto = crypto
        self._workers = workers
        self._request_string = request_string

    # --------------------------------------------------------------------------
    def returnError(self, method, message, add={}, code=400):

        # returns a normalized error; this ensures that all error messages have
        # the same formatting;
        res = {"type": method+" "+self._request_string, "success": False,
            "message": message, "args": request.args}
        for key in add: res[key] = add[key]
        return res, code

    # --------------------------------------------------------------------------
    def returnResult(self, method, result, add={}, code=200):

        # returns a normalized result; this ensures that all result messages have
        # the same formatting;
        res = {"type": method+" "+self._request_string, "success": True,
            "result": result, "args": request.args}
        return jsonify(res)
