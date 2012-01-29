from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner
from Acquisition import aq_parent
from App.class_init import InitializeClass
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import safe_callable
from Products.ZCatalog.ZCatalog import ZCatalog
from bika.lims.interfaces import IBikaSetupCatalog
from zope.component import getUtility
from zope.interface import Interface, implements

def getCatalog(instance, field = 'UID'):
    """ Return the catalog which indexes objects of instance's type.
        If an object is indexed by more than one catalog, the first match
        will be returned.

        Set AutoIndex=True on the object to prevent spurious catalog reindexing
        Remember to set it False again after your edit is complete.

    """
    if (hasattr(self, 'AutoIndex', False) and self.AutoIndex == False) or  \
       ('workflow_skiplist' in self.REQUEST and self.UID() in self.REQUEST['workflow_skiplist']):
        return None
    else:
        catalogs = [getToolByName(instance, 'portal_catalog'),
                    getToolByName(instance, 'bika_setup_catalog')]
        field = instance.getField(field)
        for catalog in catalogs:
            for index in catalog.index_objects():
                if field.accessor in index.getIndexSourceNames():
                    return catalog


class BikaSetupCatalog(CatalogTool):
    """ Catalog for all bika_setup objects
    """
    implements(IBikaSetupCatalog)

    security = ClassSecurityInfo()
    _properties = ({'id':'title', 'type': 'string', 'mode':'w'},)

    title = 'Bika Setup Catalog'
    id = 'bika_setup_catalog'
    portal_type = meta_type = 'BikaSetupCatalog'
    plone_tool = 1

    def __init__(self):
        ZCatalog.__init__(self, self.id)

    security.declareProtected(ManagePortal, 'clearFindAndRebuild')
    def clearFindAndRebuild(self):
        """
        """

        def indexObject(obj, path):
            self.reindexObject(obj)

        self.manage_catalogClear()
        portal = getToolByName(self, 'portal_url').getPortalObject()
        portal.ZopeFindAndApply(portal,
                                obj_metatypes = ('Container',
                                                 'ContainerType',
                                                 'Preservation',
                                                 'Department',
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
                                                 'LabContact',
                                                 'LabProduct',
                                                 'ReferenceManufacturer',
                                                 'ReferenceSupplier',
                                                 'ReferenceDefinition',
                                                 'WorksheetTemplate'),
                                search_sub = True,
                                apply_func = indexObject)

InitializeClass(BikaSetupCatalog)
