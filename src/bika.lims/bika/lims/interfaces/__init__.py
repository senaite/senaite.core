from zope.interface import Interface

class IBikaLIMSLayer(Interface):
    """ A layer unique to this product.
        Viewlets, etc, are specified for this layer
        if they are modified for or specific to the product 
    """

# -*- extra stuff goes here -*-
from analysisrequest import IAnalysisRequest
from analysisservice import IAnalysisService
from sample import ISample
from analysis import IAnalysis
from result import IResult
from clientfolder import IClientFolder
from client import IClient
from contact import IContact

