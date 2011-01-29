from zope.interface import Interface

from bika_folder_contents import IBikaFolderContentsView

from client import IClient

from clientfolder import IClientFolder, IClientFolderView

class IClientFolder(Interface):
    """Client Folder marker interface"""


class IBikaLIMSLayer(Interface):
    """ A layer unique to this product.
        Viewlets, etc, are specified for this layer
        if they are modified for or specific to the product 
    """


