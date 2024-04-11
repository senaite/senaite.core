# -*- coding: utf-8 -*-

from zope import deprecation

# BBB
from .analysisprofile_services_widget import AnalysisProfileServicesWidget


class AnalysisProfilesWidget(AnalysisProfileServicesWidget):
    pass


deprecation.deprecated("AnalysisProfilesWidget",
                       "Moved to senaite.core.browser.widgets.analysisprofile_services_widget.AnalysisProfileServicesWidget")  # noqa E501
