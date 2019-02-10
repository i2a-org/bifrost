 
from business_rules.variables import *
from business_rules.actions import *
from business_rules.fields import *

################################################################################
class Actions(BaseActions):

    _patient = None

    # --------------------------------------------------------------------------
    def __init__(self, patient):

        self._patient = patient

    # --------------------------------------------------------------------------
    @rule_action(params={"variable_id": FIELD_TEXT, "variable_value": FIELD_TEXT})
    def fill_numeric_variable(self, variable_id, variable_value):

        self._patient.addValue(variable_id, int(variable_value), "numeric")

    # --------------------------------------------------------------------------
    @rule_action(params={"variable_id": FIELD_TEXT, "value": FIELD_NUMERIC})
    def accept_numeric_variable(self, variable_id, value):

        self._patient.addValue(variable_id, value, "numeric")

    # --------------------------------------------------------------------------
    @rule_action(params={"variable_id": FIELD_TEXT, "increment": FIELD_NUMERIC})
    def increment_variable(self, variable_id, increment):

        val = int(self._patient.getMostRecentValue(variable_id))
        if not val: val = 0
        val += int(increment)
        self._patient.addValue(variable_id, val, "numeric")

    # --------------------------------------------------------------------------
    @rule_action(params={"variable_id": FIELD_TEXT, "values": FIELD_SELECT})
    def accept_set_values(self, variable_id, values):

        self._patient.addValue(variable_id, values, "select")
