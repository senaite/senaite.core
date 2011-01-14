"""BikaSetup is a tool containing lookup lists and configuration data.

$Id: BikaSetup.py 319 2006-11-05 20:27:14Z anneline $
"""
from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from ZODB.POSException import ConflictError
from OFS.Folder import Folder
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore import permissions

class BikaSetup(UniqueObject, Folder):

    security = ClassSecurityInfo()
    
    id = 'bika_setup'
    title = ('The setup folder holds the configuration data '
             'for the lab information system')
    meta_type = 'Bika Setup'


InitializeClass(BikaSetup)
