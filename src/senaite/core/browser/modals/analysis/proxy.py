# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the Free
# Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA.
#
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from senaite.core.api import dtime
from zope.interface import implementer

from .schema import IEditAnalysisSchema


@implementer(IEditAnalysisSchema)
class AnalysisSchemaProxy(object):
    """Proxy wrapping an AT analysis object.

    Implements IEditAnalysisSchema so z3c.form can populate
    widgets via attribute access. Setters are no-ops because
    the form save handler uses IDataManager directly.
    """

    def __init__(self, analysis):
        self._analysis = analysis

    @property
    def result(self):
        return self._analysis.getResult() or u""

    @result.setter
    def result(self, value):
        pass

    @property
    def uncertainty(self):
        return self._analysis.getUncertainty() or u""

    @uncertainty.setter
    def uncertainty(self, value):
        pass

    @property
    def method(self):
        m = self._analysis.getMethod()
        return api.get_uid(m) if m else None

    @method.setter
    def method(self, value):
        pass

    @property
    def instrument(self):
        i = self._analysis.getInstrument()
        return api.get_uid(i) if i else None

    @instrument.setter
    def instrument(self, value):
        pass

    @property
    def analyst(self):
        return self._analysis.getAnalyst() or None

    @analyst.setter
    def analyst(self, value):
        pass

    @property
    def unit(self):
        return self._analysis.getUnit() or None

    @unit.setter
    def unit(self, value):
        pass

    @property
    def detection_limit_operand(self):
        return (
            self._analysis.getDetectionLimitOperand() or None
        )

    @detection_limit_operand.setter
    def detection_limit_operand(self, value):
        pass

    @property
    def hidden(self):
        return self._analysis.getHidden()

    @hidden.setter
    def hidden(self, value):
        pass

    @property
    def remarks(self):
        return self._analysis.getRemarks() or u""

    @remarks.setter
    def remarks(self, value):
        pass

    @property
    def result_capture_date(self):
        capture_date = self._analysis.getResultCaptureDate()
        if not capture_date:
            return None
        return dtime.to_dt(capture_date)

    @result_capture_date.setter
    def result_capture_date(self, value):
        pass
