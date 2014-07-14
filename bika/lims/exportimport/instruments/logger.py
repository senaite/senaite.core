from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t

class Logger:

    def __init__(self):
        self._errors = []
        self._warns = []
        self._logs = []

    def err(self, msg, numline=None, line=None, mapping={}):
        self.msg(self._errors, msg, numline, line, mapping)
#        self.msg(self._logs, _("[ERROR] ") + msg, numline, line)

    def warn(self, msg, numline=None, line=None, mapping={}):
        self.msg(self._warns, msg, numline, line, mapping)
#        self.msg(self._logs, _("[WARN] ") + msg, numline, line)

    def log(self, msg, numline=None, line=None, mapping={}):
        self.msg(self._logs, msg, numline, line, mapping)

    def msg(self, array, msg, numline=None, line=None, mapping={}):
        prefix = ''
        suffix = ''
        msg = t(_(safe_unicode(msg), mapping=mapping))
        if numline:
            prefix = "[%s] " % numline
        if line:
            suffix = ": %s" % line
        array.append(prefix + msg + suffix)

    @property
    def errors(self):
        """ Return an array with the errors thrown during the file processing
        """
        return self._errors

    @property
    def logs(self):
        """ Return an array with logs generated during the file processing
        """
        return self._logs

    @property
    def warns(self):
        """ Return an array with warns generated during the file processing
        """
        return self._warns
