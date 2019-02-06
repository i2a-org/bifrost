
import hashlib
import base64
import os

class Crypto:

    # --------------------------------------------------------------------------
    def hashValue(self, value):

        # hash a given value;
        return hashlib.sha1(bytes(value, "utf8")).hexdigest()
