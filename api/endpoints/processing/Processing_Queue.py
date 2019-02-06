
from flask import request
from api.endpoints.shared.BaseEndpoint import BaseEndpoint

################################################################################
class QueueLoader:

    _db = None
    _loaded_patients = {}
    _loaded_rules = {}

    # --------------------------------------------------------------------------
    def __init__(self, db):

        self._db = db

    # --------------------------------------------------------------------------
    def getPatient(self, patient_id):

        #if patient_id not in self._loaded_patients:
        self._loaded_patients[patient_id] = self._db.getPatient(patient_id)
        return self._loaded_patients[patient_id]

    # --------------------------------------------------------------------------
    def getRule(self, rule_id):

        #if rule_id not in self._loaded_rules:
        self._loaded_rules[rule_id] = self._db.getRule(rule_id)
        return self._loaded_rules[rule_id]

    # --------------------------------------------------------------------------
    def setPatient(self, patient_id, patient):

        self._loaded_patients[patient_id] = patient

################################################################################
class Processing_Queue(BaseEndpoint):

    # --------------------------------------------------------------------------
    def post(self):

        # process all elements in the queue;
        ql = QueueLoader(self._db)

        # get all elements and keep track of processed items;
        queue = self._db.getQueue()
        processed = []

        for q in queue: # loop through each element in queue;

            # get the patient that requested the operation; if it wasn't found,
            # quit;
            queue_error = False
            patient = ql.getPatient(q["patient_id"])
            if not patient:
                #print("PATIENT ID", q["patient_id"])
                queue_error = True
                continue

            for report_id in q["process"]: # the queue accepts a multitude of reports
                                           # in one go, so process all of them;

                # get the report that was requested; if it wasn't found, quit;
                report = self._db.searchReport(id=report_id)
                if not report:
                    #print("REPORT ID", report_id)
                    queue_error = True
                    continue
                report = report[0]

                for rule_id in report["rules"]: # a report consists of multiple rules,
                                                # process all of them;

                    # get the rule that was requested; if it wasn't found, quit;
                    rule = ql.getRule(rule_id)
                    if not rule:
                        #print("RULE ID", rule_id)
                        queue_error = True
                        continue

                    # detect if some of the values are missing; since the refresh
                    # threshold can be set freely, we have to ignore it, otherwise
                    # this item may be stuck in the queue;
                    inverr, missing = rule.detectMissingValues(patient, use_refresh=False)
                    if not inverr: # if values are missing, quit;
                        #print("ERR")
                        queue_error = True
                        continue

                    # resolve the rule;
                    check = rule.resolveRule(patient)
                    if not check:
                        #print("NORESOLVE")
                        #queue_error = True
                        continue
                    patient = check

            # if there was no administrative error in processing, mark the item
            # as done, and allow patient to view the report;
            if not queue_error:
                patient.finalizeReport(report_id)
                ql.setPatient(q["patient_id"], patient)
                self._db.removeQueue(q["queue_id"])
                processed.append(q["queue_id"])

        # save all modified patients;
        for patient in ql._loaded_patients:
            self._db.savePatient(ql._loaded_patients[patient])
        del ql

        return self.returnResult("POST", processed)
