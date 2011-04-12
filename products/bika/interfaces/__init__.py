from zope.interface import Interface
from controlpanel import *

class IBikaLIMSLayer(Interface):
    """ A layer unique to this product.
        Viewlets, etc, are specified for this layer
        if they are modified for or specific to the product 
    """

class IClient(Interface):
    """Client marker interface"""

class ILims(Interface):
    """Lims marker interface"""

class IAnalysisRequest(Interface):
    """
    """
