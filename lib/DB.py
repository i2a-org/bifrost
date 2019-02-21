
import boto3
from boto3.dynamodb.conditions import Key
import datetime
import time
from decimal import *
import json
import uuid

from .Patient import Patient
from .Rule import Rule

################################################################################
class DB:

    _client = None
    _db = None
    _env = None
    _app = "org.i2a"
    _workers = None

    # --------------------------------------------------------------------------
    def __init__(self, env, workers):

        try:
            # initialize DynamoDB client for specific environment;
            # dev is hosted locally to prevent unneccessary traffic;
            if env == "dev":
                print("[DB] Running DynamoDB local.")
                self._client = boto3.resource("dynamodb", endpoint_url="http://localhost:8000/")
            else:
                print("[DB] Using DynamoDB.")
                self._client = boto3.resource("dynamodb", region_name="us-west-2")
            self._env = env
            self._workers = workers
        except:
            print("[ERROR] Could not connect to DB.")

    # --------------------------------------------------------------------------
    def insert(self, collection, val):

        try:
            # get table, insert item and evaluate errors;
            table = self._client.Table(self._env + "." + self._app + "." + collection)
            res = table.put_item( Item=val )
            if res["ResponseMetadata"]["HTTPStatusCode"] != 200: return False
            else: return True
        except Exception as e:
            if self._env == "dev": print("ERROR", e)
            return False

    # --------------------------------------------------------------------------
    def delete(self, collection, val):

        try:
            # get table, delete item and evaluate errors;
            table = self._client.Table(self._env + "." + self._app + "." + collection)
            res = table.delete_item( Key=val )
            if res["ResponseMetadata"]["HTTPStatusCode"] != 200: return False
            else: return True
        except Exception as e:
            if self._env == "dev": print("ERROR", e)
            return False

    # --------------------------------------------------------------------------
    def find(self, collection, val):

        try:
            # get table, get item and evaluate errors;
            table = self._client.Table(self._env + "." + self._app + "." + collection)
            res = table.get_item( Key=val )
            if res["ResponseMetadata"]["HTTPStatusCode"] != 200: return False
            else: return res["Item"]
        except Exception as e:
            if self._env == "dev": print("ERROR", e)
            return False

    # --------------------------------------------------------------------------
    def query(self, collection, index, query, ftype="eq", high=None):

        try:
            # get table;
            table = self._client.Table(self._env + "." + self._app + "." + collection)

            # find the according filter to be used;
            bfilter = None
            if ftype == "eq": bfilter = Key(index).eq(query)
            elif ftype == "gt": bfilter = Key(index).gt(query)
            elif ftype == "gte": bfilter = Key(index).gte(query)
            elif ftype == "lt": bfilter = Key(index).lt(query)
            elif ftype == "lte": bfilter = Key(index).lte(query)
            elif ftype == "bw": bfilter = Key(index).begins_with(query)
            elif ftype == "bt" and high != None: bfilter = Key(index).between(query, high)
            # if invalid, quit;
            if bfilter == None: return False

            # get items and evaluate errors;
            res = table.scan(
                FilterExpression=bfilter
            )
            if res["ResponseMetadata"]["HTTPStatusCode"] != 200: return False
            else: return res["Items"]
        except Exception as e:
            if self._env == "dev": print("ERROR", e)
            return False

    # --------------------------------------------------------------------------
    def scan(self, collection):

        try:
            # get table, get all items and evaluate errors;
            table = self._client.Table(self._env + "." + self._app + "." + collection)
            res = table.scan()
            if res["ResponseMetadata"]["HTTPStatusCode"] != 200: return False
            else: return res["Items"]
        except Exception as e:
            if self._env == "dev": print("ERROR", e)
            return False

    # --------------------------------------------------------------------------
    def update(self, collection, fil, expression, attributes, values):

        try:
            # get table, update item and evaluate errors;
            table = self._client.Table(self._env + "." + self._app + "." + collection)
            return table.update_item(Key=fil, 
                UpdateExpression=expression,
                ExpressionAttributeNames=attributes,
                ExpressionAttributeValues=values
            )
        except Exception as e:
            if self._env == "dev": print("ERROR", e)
            return False

    # --------------------------------------------------------------------------
    def searchAction(self, term=""):

        # search for a defined action;
        if term == "": return self.scan("actions")
        return self.query("actions", "name", term, "bw")

    # --------------------------------------------------------------------------
    def searchVariable(self, term="", id=""):

        # search for a define variable;
        if term != "": return self.query("variables", "name", term, "bw")
        elif id != "":
            res = self.find("variables", {"variable_id": id})
            if res: return [res]
            return False
        return self.scan("variables")
        

    # --------------------------------------------------------------------------
    def searchRule(self, term="", id=""):

        # search for a defined rule;
        res = {}
        if term != "": return self.query("rules", "name", term, "bw")
        elif id != "":
            res = self.find("rules", {"rule_id": id})
            if res: return [res]
            return False
        else: return self.scan("rules")

    # --------------------------------------------------------------------------
    def searchReport(self, term="", id=""):

        # search for a defined report;
        res = {}
        if term != "": return self.query("reports", "name", term, "bw")
        elif id != "":
            res = self.find("reports", {"report_id": id})
            if res: return [res]
            return False
        else: return self.scan("reports")

    # --------------------------------------------------------------------------
    def getRule(self, rule_id):

        # get a specific rule;
        rule = self.find("rules", {"rule_id": rule_id})
        if not rule: return False
        return Rule(rule, self._workers, self)

    # --------------------------------------------------------------------------
    def createPatient(self, patient_id, hhash):

        # create a new patient;
        return self.insert("patients", {
            "patient_id": patient_id,
            "hash": hhash,
            "variables": {},
            "queue": {},
            "reports": {}
        })

    # --------------------------------------------------------------------------
    def getPatient(self, patient_id):

        # get a specific patient;
        patient = self.find("patients", {"patient_id": patient_id})
        if not patient: return False
        return Patient(patient)

    # --------------------------------------------------------------------------
    def savePatient(self, patient):

        # save a specific patient from a Patient object;
        return self.insert("patients", patient._patient_obj)

    # --------------------------------------------------------------------------
    def addSession(self, session_id, patient_id):

        # create a new session;
        return self.insert("sessions", {
            "session_id": session_id,
            "patient_id": patient_id,
            "timestamp": int(time.time())
        })

    # --------------------------------------------------------------------------
    def getSession(self, session_id):

        # get a specific session;
        return self.find("sessions", {"session_id": session_id})

    # --------------------------------------------------------------------------
    def getVariable(self, variable_id):

        # get a specific variable;
        return self.find("variables", {"variable_id": variable_id})

    # --------------------------------------------------------------------------
    def addVariable(self, patient_id, variable_id, value):

        # add a new variable to patient;
        return self.update("patients", {"patient_id": patient_id}, "SET #VALUE.#FIELD = :value",
            {"#VALUE":"variables", "#FIELD":variable_id}, {":value":value})

    # --------------------------------------------------------------------------
    def addQueue(self, patient_id, report_id):

        # add a new operation to the queue;
        queue_id = str(uuid.uuid4())
        return self.insert("queue", {
            "queue_id": queue_id,
            "patient_id": patient_id,
            "process": [report_id],
            "status": "queued"
        }), queue_id

    # --------------------------------------------------------------------------
    def getQueue(self):

        # get the entire queue;
        return self.scan("queue")

    # --------------------------------------------------------------------------
    def removeQueue(self, queue_id):

        # remove element from queue;
        return self.delete("queue", {"queue_id": queue_id})
