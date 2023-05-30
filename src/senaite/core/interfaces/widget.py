# -*- coding: utf-8 -*-

from zope.interface import Interface


class IReferenceWidgetDataProvider(Interface):
    """Extract required data for the reference widget
    """

    def to_dict():
        """Provide a dictionary with JSON serializable object information
        """


class IReferenceWidgetVocabulary(Interface):
    """Search adapter for reference/query widget
    """

    def __call__(**kwargs):
        """Call method
        """
