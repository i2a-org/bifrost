
import datetime
import time
import random

class Logger:

    _loggers = {}
    _db = None
    _env = None

    # --------------------------------------------------------------------------
    def __init__(self, db, env):

        self._db = db
        self._env = env

    # --------------------------------------------------------------------------
    def log(self, name, message, status="NORMAL"):

        # insert log into DB
        self._db.insert("logs", {
            "timestamp": int((time.time()+random.uniform(0, 1))*1000000000),
            "name": name,
            "status": status,
            "log": message
        })
        return True
