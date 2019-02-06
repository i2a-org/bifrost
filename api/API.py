
import json
from flask import Flask, request, jsonify
from flask.json import JSONEncoder
from flask_restful import Api
from decimal import *

from lib.Logger import Logger
from lib.DB import DB
from lib.Crypto import Crypto

import conf

""" API.py
"""

################################################################################
class API:
    """ The Endpoints class

    Initializes the API portion of Bifrost. Also, takes care of authorizations.

    Attributes
    ----------
    _endpoints : dict
        the endpoint with the associated classes
    _version : str
        current version that the API runs on
    _logger : Logger
        the logger object for keeping track of traffic
    _db : DB
        the DB object for DB interfaces
    """

    _endpoints = conf._endpoints
    _protected = conf._protected
    _workers = conf._workers

    _version = "v0"
    _logger = None
    _db = None
    _crypto = None
    _env = ""

    # --------------------------------------------------------------------------
    def __init__(self, env):
        """
        Parameters
        ----------
        env : str
            the environment that the current instance is running
        """
        print("[ENDPOINTS] Initializing...")
        # initialize libraries
        self._env = env
        self._db = DB(self._env, self._workers)
        self._logger = Logger(self._db, self._env)
        self._crypto = Crypto()
        # initialize Flask
        self._app = Flask(__name__)
        self._app.json_encoder = CustomJSONEncoder
        self._api = Api(self._app)
        self._app.before_request(self.detectAuthorization)
        self._app.after_request(self.finishRequest)
        for url in self._endpoints: self.addResource(self._endpoints[url], url)
        print("[ENDPOINTS] Done.")

    # --------------------------------------------------------------------------
    def getApp(self):
        """ Return Flask app

        AWS requires a Elastic Beanstalk app to be an executable app. As for now
        this works.

        Returns
        -------
        Flask
            the flask application for AWS
        """

        return self._app

    # --------------------------------------------------------------------------
    def logRequests(self, rtype, request):
        """ Prepare log messages

        Prepare the messages that we want and use Logger to save them to disk, or
        send a notification.

        Parameters
        ----------
        rtype : int
            response type
        request : Request
            request object that was generated by Flask
        """

        status = "NORMAL"
        if rtype == 404 or rtype == 500: status = "CRITICAL"
        elif rtype == 401: status = "NOAUTH"

        self._logger.log(
            "endpoints", json.dumps({
                "rtype": str(rtype),
                "path": request.path,
                "data": request.data.decode("utf8"),
                "args": request.args.to_dict(),
                "method": request.method,
                "remote_addr": request.remote_addr,
                "headers": request.headers.to_list()
            }), status=status
        )

    # --------------------------------------------------------------------------
    def sendAuthorizationError(self, message, token):
        """ Create the authorization error message

        Generates a error message that is used multiple times in the code.

        Parameters
        ----------
        message : str
            message to be sent
        token : str
            the token that was used in the request

        Returns
        -------
        str
            the returning JSON response as a string
        int
            HTTP response code
        """

        return (json.dumps({ "error":message }), 401)

    # --------------------------------------------------------------------------
    def isValid(self, session, patient_id):
        """ Check if token is valid

        Uses DB to check if the given token is existing and acive. The `active`
        flag in the DB can hence be used to quickly deactivate a token.

        Parameters
        ----------
        session : str
            the token that was used in the request
        patient_id : str
            the patient ID that was sent with the request

        Returns
        -------
        bool
            IF valid => True, ELSE False
        str
            the patient_id of the user associated with the session
        dict
            the full session dict containing all the information loaded from DB
        """

        # check if token set;
        try:
            if session == "" or patient_id == "":
                return False, "", {}

            session = self._db.getSession(session)
            if session["patient_id"] != patient_id: return False, "", {}
        except:
            return False, "", {}

        return True, session["patient_id"], session

    # --------------------------------------------------------------------------
    def detectAuthorization(self):
        """ Check if authorization is valid

        Uses the Flask request to check the header. The `Bearer` header must be
        present and name a valid session_id. Specifically, the function looks for
        the `Authorization: Bearer [SESSION]` header (note the exact format). Finally,
        the function adds `patient_id` and `session` to the request object, to make this
        information available to the system.
        """
        request_path = request.path[len(self._version)+1:]
        header = request.headers.get("Authorization")

        if request_path in self._protected and request.method in self._protected[request_path]:

            header = request.headers.get("Authorization")
            if not header:
                return self.sendAuthorizationError("Invalid header. Request registered.", "")
            # bearer or token not set;
            outs = header.split()
            if len(outs) != 2:
                return self.sendAuthorizationError("Invalid authentication. Request registered.", "")
            bearer, session = outs
            auth, patient_id, obj = self.isValid(session, request.headers.get("Patient"))
            if bearer != "Bearer" or not auth:
                return self.sendAuthorizationError("Invalid authentication. Request registered.", session)

            request.patient_id = patient_id
            request.session = session
            request.obj = obj

    # --------------------------------------------------------------------------
    def finishRequest(self, response):
        """ Hook for after response has been prepared

        This function logs the response.

        Parameters
        ----------
        response : Response
            Response object for Flask

        Returns
        -------
        response : Response
            Response object for Flask
        """

        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Authorization,Patient"
        self.logRequests(response.status_code, request)
        return response

    # --------------------------------------------------------------------------
    def addResource(self, obj, url):
        """ Add resources to flask_restful

        Injects the API with the endpoints that are given in the `_endpoints`
        attribute.

        Parameters
        ----------
        obj : flask_restful.Resource
            class to inject
        url : str
            Flask formatted endpoint
        """

        print("[ADDED ROUTE]", "/"+self._version+url)
        self._api.add_resource(
            obj, 
            "/"+self._version+url, 
            resource_class_kwargs={
                "logger":self._logger,
                "db":self._db,
                "crypto": self._crypto,
                "workers": self._workers,
                "request_string": "/"+self._version+url
            }
        )

################################################################################
class CustomJSONEncoder(JSONEncoder):
    """ The CustomJSONEncoder class

    Allows for parsing of the Decimal object that is returned from AWS.
    """

    # --------------------------------------------------------------------------
    def default(self, obj):
        """ Add default parser

        Adds capability for parsing Decimal object.

        Parameters
        ----------
        obj : Decimal, or other
            class to convert for json parser
        """
        
        if isinstance(obj, Decimal):
            return float(obj)
        return super(CustomJsonEncoder, self).default(obj)
