from zope.interface import Interface
from controlpanel import *

class IBikaLIMSLayer(Interface):
    """ A layer unique to this product.
        Viewlets, etc, are specified for this layer
        if they are modified for or specific to the product 
    """

class IClientFolder(Interface):
    """Mark client folder"""

class IClient(Interface):
    """Client marker interface"""

class IAnalysisRequest(Interface):
    """Analysis Request marker interface"""

class ISample(Interface):
    """Sample marker interface"""

class IHaveNoByline(Interface):
    """Items which do not have a byline"""

class IIdServer(Interface):
    """ Interface for ID server """

    def generate_id(self, portal_type, batch_size = None):
        """ Generate a new id for 'portal_type' """
