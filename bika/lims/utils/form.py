from bika.lims import logger
from bika.lims.utils import t
from Products.Archetypes import PloneMessageFactory as PMF


def ajax_form_error(errors, field=None, arnum=None, msg=None):
    if not msg:
        msg = t(PMF('Input is required but no input given.'))
    if (arnum is not None and field):
        error_key = ' %s.%s' % (int(arnum) + 1, field or '')
    elif (field):
        error_key = ' %s' % field
    else:
        error_key = 'Form Error'
    logger.info("ajax_form_error: %s, arnum=%s: %s" % (error_key, arnum, msg))
    errors[error_key] = msg
