from ckan.logic import validators
import ckan.lib.navl.dictization_functions as df
from ckan.common import _


def is_positive_integer(value, context):
    value = validators.int_validator(value, context)

    if value < 1:
        raise df.Invalid(_('Must be a positive integer'))

    return value
