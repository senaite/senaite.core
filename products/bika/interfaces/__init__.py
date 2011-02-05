from zope.interface import Interface

from client import IClient
from tools import *
from clientfolder import IClientFolder, IClientFolderView


class IClientFolder(Interface):
    """Client Folder marker interface"""


class IBikaLIMSLayer(Interface):
    """ A layer unique to this product.
        Viewlets, etc, are specified for this layer
        if they are modified for or specific to the product 
    """


