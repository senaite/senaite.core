from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner
from Acquisition import aq_parent
from Globals import InitializeClass
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import safe_callable
from Products.ZCatalog.ZCatalog import ZCatalog
from bika.lims.interfaces import IBikaSetupCatalog
from zope.component import getUtility
from zope.interface import Interface, implements

class BikaSetupCatalog(CatalogTool):
   """ Catalog for types in bika_setup
   """
   implements(IBikaSetupCatalog)

   title = 'Bika Setup Catalog'
   id = 'bika_setup_catalog'
   portal_type = meta_type = 'BikaSetupCatalog'
   plone_tool = 1

   security = ClassSecurityInfo()
   _properties=(
      {'id':'title', 'type': 'string', 'mode':'w'},)

   def __init__(self):
       ZCatalog.__init__(self, self.id)

    security.declareProtected(ManagePortal, 'clearFindAndRebuild')
    def clearFindAndRebuild(self):
        """Empties catalog, then finds all contentish objects (i.e. objects
           with an indexObject method), and reindexes them.
           This may take a long time.
        """

        def indexObject(obj, path):
            self.reindexObject(obj)

        self.manage_catalogClear()
        portal = getToolByName(self, 'portal_url').getPortalObject()
        portal.ZopeFindAndApply(portal,
                                obj_metatypes=('Department',
                                               'AnalysisCategory',
                                               'AnalysisService',
                                               'AnalysisSpec',
                                               'SampleType',
                                               'SamplePoint',
                                               'Instrument',
                                               'Method',
                                               'AttachmentType',
                                               'Calculation',
                                               'ARProfile',
                                               'LabProduct',
                                               'ReferenceManufacturer',
                                               'ReferenceSupplier',
                                               'ReferenceDefinition',
                                               'WorksheetTemplate'),
                                search_sub=True,
                                apply_func=indexObject)

InitializeClass(BikaSetupCatalog)
