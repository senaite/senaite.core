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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import senaiteMessageFactory as _
from z3c.form.error import ErrorViewSnippet
from zope.component import adapter
from senaite.core.interfaces import ISenaiteFormLayer


@adapter(ValueError, ISenaiteFormLayer, None, None, None, None)
class ValueErrorViewSnippet(ErrorViewSnippet):
    """An error view for ValueError.
    """

    defaultMessage = _("Validation failed.")

    def createMessage(self):
        message = self.error.message
        return message or self.defaultMessage
