from zope.interface import Interface
from tools import *

class IClient(Interface):
    """Client marker interface"""

class IAnalysisServicesWidgetHelper(Interface):
    """AnalysisServicesWidget helper functions """

    def getAnalysisCategories():
        """ """


class ILims(Interface):
    """Lims marker interface"""

class IBikaLIMSLayer(Interface):
    """ A layer unique to this product.
        Viewlets, etc, are specified for this layer
        if they are modified for or specific to the product 
    """

