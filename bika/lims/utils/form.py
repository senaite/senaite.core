from bika.lims.utils import t
from Products.Archetypes import PloneMessageFactory as PMF


def ajax_form_error(errors, field=None, arnum=None, message=None):
    print '>>>>>>>>>>>ajax_form_error: field = %s, arnum = %s' % (field, arnum)
    if not message:
        message = t(PMF('Input is required but no input given.'))
    if (arnum is not None and field):
        error_key = ' %s.%s' % (int(arnum) + 1, field or '')
    elif (field):
        error_key = ' %s' % field
    else:
        error_key = 'Form Error'
    errors[error_key] = message
