from bika.lims.utils import t
from Products.Archetypes import PloneMessageFactory as PMF


def ajax_form_error(errors, field=None, column=None, message=None):
    if not message:
        message = t(PMF('Input is required but no input given.'))
    if (column and field):
        error_key = ' %s.%s' % (int(column) + 1, field or '')
    elif (field):
        error_key = ' %s' % field
    else:
        error_key = 'Form Error'
    errors[error_key] = message
