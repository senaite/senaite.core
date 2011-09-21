from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Five.browser import BrowserView
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolderSchema, ATFolder
from zope.interface.declarations import implements

class BikaSetupData(BrowserView):

    template = "bika_setup_data.pt"

    def __init__(self, context, request):
        BrowserView.__init(self, context, request)

    def __call__(self):
        return template()
