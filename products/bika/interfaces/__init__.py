from zope.interface import Interface

from client import IClient

class IBikaLIMSLayer(Interface):
    """ A layer unique to this product.
        Viewlets, etc, are specified for this layer
        if they are modified for or specific to the product 
    """


class IClientFolder(Interface):
    """Client Folder marker interface"""

