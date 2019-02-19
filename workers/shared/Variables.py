
from business_rules.variables import *
from business_rules.actions import *
from business_rules.fields import *

################################################################################
class Variable:

    field_type = None
    is_rule_variable = True
    label = None
    options = []
    value = None

    def __init__(self, value, field_type, label=None):

        self.value = value
        self.field_type = field_type
        self.label = label

    def __call__(self):

        return self.value

################################################################################
class Variables(BaseVariables):

    _vt = {
        "numeric": NumericType,
        "string": StringType,
        "boolean": BooleanType,
        "select": SelectType,
        "select_multiple": SelectMultipleType
    }

    def __init__(self, var):

        for key in var:
            new = Variable(var[key][0], self._vt[var[key][1]])
            setattr(self, key, new)
            