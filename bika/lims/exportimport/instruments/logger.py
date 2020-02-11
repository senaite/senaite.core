# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

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
