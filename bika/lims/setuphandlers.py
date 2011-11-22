""" Bika setup handlers. """

from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.config import *
from bika.lims.interfaces import IHaveNoBreadCrumbs
from zope.event import notify
from zope.interface import alsoProvides
from Products.CMFEditions.Permissions import ApplyVersionControl
from Products.CMFEditions.Permissions import SaveNewVersion
from Products.CMFEditions.Permissions import AccessPreviousVersions

class BikaGenerator:

    def setupPropertiesTool(self, portal):
        ptool = getToolByName(portal, 'portal_properties')
        if not getattr(ptool, 'bika_properties', None):
            ptool.addPropertySheet('bika_properties', 'Bika Properties')
            ps = getattr(ptool, 'bika_properties')
            ps._properties = ps._properties + ({'id':'country_names', 'type':'lines', 'mode':'w'},)
            ps._updateProperty('country_names', COUNTRY_NAMES)

    def setupDependencies(self, portal):
        """Install required products"""

        pq = getToolByName(portal, 'portal_quickinstaller')
        for product in DEPENDENCIES:
            if not pq.isProductInstalled(product):
                if pq.isProductInstallable(product):
                    pq.installProduct(product)
                else:
                    raise "Product %s not installable" % product

    def setupPortalContent(self, portal):
        """ Setup Bika site structure """

        wf = getToolByName(portal, 'portal_workflow')

        obj = portal._getOb('index_html')
        alsoProvides(obj, IHaveNoBreadCrumbs)

        # remove undesired content objects
        del_ids = []
        for obj_id in ['Members', 'front-page', 'news', 'events']:
            if obj_id in portal.objectIds():
                del_ids.append(obj_id)
        if del_ids:
            portal.manage_delObjects(ids = del_ids)

        # index objects - importing through GenericSetup doesn't
        for obj_id in ('clients',
                       'invoices',
                       'pricelists',
                       'bika_setup',
                       'analysisrequests',
                       'referencesamples',
                       'samples',
                       'worksheets',
                       ):
            obj = portal._getOb(obj_id)
            obj.unmarkCreationFlag()
            obj.reindexObject()

        bika_setup = portal._getOb('bika_setup')
        for obj_id in ('bika_analysiscategories',
                       'bika_analysisservices',
                       'bika_attachmenttypes',
                       'bika_calculations',
                       'bika_departments',
                       'bika_instruments',
                       'bika_analysisspecs',
                       'bika_arprofiles',
                       'bika_labcontacts',
                       'bika_methods',
                       'bika_labproducts',
                       'bika_samplepoints',
                       'bika_sampletypes',
                       'bika_referencedefinitions',
                       'bika_referencemanufacturers',
                       'bika_referencesuppliers',
                       'bika_worksheettemplates',
                       'laboratory'):
            obj = bika_setup._getOb(obj_id)
            obj.unmarkCreationFlag()
            obj.reindexObject()

        # Move calendar and user action to bika
##        for action in portal.portal_controlpanel.listActions():
##            if action.id in ('UsersGroups', 'UsersGroups2', 'bika_calendar_tool'):
##                action.permissions = (ManageBika,)

    def setupGroupsAndRoles(self, portal):
        # add roles
        for role in ('LabManager',
                     'LabClerk',
                     'Analyst',
                     'Verifier',
                     'Publisher',
                     'Member',
                     'Reviewer'):
            if role not in portal.acl_users.portal_role_manager.listRoleIds():
                portal.acl_users.portal_role_manager.addRole(role)
            # add roles to the portal
            portal._addRole(role)

        # Create groups
        portal_groups = portal.portal_groups

        if 'LabManagers' not in portal_groups.listGroupIds():
            try:
                portal_groups.addGroup('LabManagers', title = "Lab Managers",
                       roles = ['Member', 'LabManager', 'Site Administrator'])
            except KeyError:
                portal_groups.addGroup('LabManagers', title = "Lab Managers",
                       roles = ['Member', 'LabManager', 'Manager'])# Plone < 4.1

        if 'LabClerks' not in portal_groups.listGroupIds():
            portal_groups.addGroup('LabClerks', title = "Lab Clerks",
                roles = ['Member', 'LabClerk'])

        if 'Analysts' not in portal_groups.listGroupIds():
            portal_groups.addGroup('Analysts', title = "Lab Technicians",
                roles = ['Member', 'Analyst'])

        if 'Verifiers' not in portal_groups.listGroupIds():
            portal_groups.addGroup('Verifiers', title = "Verifiers",
                roles = ['Verifier'])

        if 'Publishers' not in portal_groups.listGroupIds():
            portal_groups.addGroup('Publishers', title = "Publishers",
                roles = ['Publisher'])

        if 'Clients' not in portal_groups.listGroupIds():
            portal_groups.addGroup('Clients', title = "Clients",
                roles = ['Member', ])

        if 'ReferenceSuppliers' not in portal_groups.listGroupIds():
            portal_groups.addGroup('ReferenceSuppliers', title = "",
                roles = ['Member', ])

    def setupPermissions(self, portal):
        """ Set up some suggested role to permission mappings.
        """
        # XXX: All these permission can be set in
        # profiles/default/structure

        mp = portal.manage_permission

        mp(permissions.ListFolderContents,
           ['Manager', ], 1)
        mp(permissions.AddPortalContent,
           ['Manager', 'Owner', 'LabManager'], 0)
        mp(permissions.FTPAccess,
           ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
        mp(permissions.DeleteObjects,
           ['Manager', 'LabManager', 'LabClerk', 'Owner'], 1)
        mp(permissions.ModifyPortalContent,
           ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner'], 1)
        mp(permissions.ManageUsers,
           ['Manager', 'LabManager', ], 1)

        mp(ApplyVersionControl,
           ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner'], 0)
        mp(SaveNewVersion,
           ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner'], 0)
        mp(AccessPreviousVersions,
           ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner'], 0)
           #['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'Anonymous'], 0)

        # Start of old stuff
        mp(ManageBika,
            ['Manager', 'LabManager'], 1)
        mp(ManageClients,
            ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(ManageWorksheets,
            ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
        mp(ManageOrders,
            ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(ManageAnalysisRequests,
            ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
        mp(ManageSample,
            ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
        mp(ManageReferenceSuppliers,
            ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
        mp(ManageReference,
            ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
        mp(ManagePricelists,
            ['Manager', 'LabManager', 'Owner'], 1)
        mp(ManageARImport,
            ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(DispatchOrder,
            ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(PostInvoiceBatch,
            ['Manager', 'LabManager', 'Owner'], 1)

        # Start of interesting stuff
        mp(ReceiveSample,
            ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(ExpireSample,
            ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(DisposeSample,
            ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(ImportAnalysis,
            ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
        mp(RejectWorksheet,
            ['Manager', 'LabManager', 'Verifier'], 1)
        mp(Retract,
            ['Manager', 'LabManager', 'Verifier'], 1)
        mp(Verify,
            ['Manager', 'LabManager', 'Verifier'], 1)
        mp(VerifyOwnResults,
            ['Manager', ], 1)
        mp(Publish,
            ['Manager', 'LabManager', 'Publisher'], 1)
        mp(EditSample,
            ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
        mp(EditAR,
            ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(EditWorksheet,
            ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
        mp(ManageResults,
            ['Manager', 'LabManager', 'Analyst'], 1)
        mp(ResultsNotRequested,
            ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
        mp(ManageInvoices,
            ['Manager', 'LabManager', 'Owner'], 1)
        mp(ViewResults,
            ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
        mp(EditResults,
            ['Manager', 'LabManager', 'Analyst'], 1)
        mp(CancelAndReinstate,
            ['Manager', 'LabManager', 'Owner'], 1)

        # End of interesting stuff

        mp = portal.clients.manage_permission
        mp(permissions.ListFolderContents,
            ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Member'], 0)
            #['Manager', 'LabManager','LabClerk','Analyst','Member', 'Anonymous'], 0)
        mp(permissions.View,
           ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner'], 0)
           #['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'Anonymous'], 0)
        mp('Access contents information',
            ['Manager', 'LabManager', 'LabClerk', 'Member', 'Analyst'], 0)
            #['Manager', 'LabManager','LabClerk','Member','Analyst', 'Anonymous'], 0)
        mp(permissions.AddPortalContent,
           ['Manager', 'LabManager', 'LabClerk', 'Owner', ], 0)
        portal.clients.reindexObject()

        mp = portal.worksheets.manage_permission
        mp(permissions.ListFolderContents,
            ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
            #['Manager', 'LabManager','LabClerk','Analyst', 'Anonymous'], 0)
        mp(permissions.AddPortalContent,
            ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
            #['Manager', 'LabManager','LabClerk','Analyst', 'Anonymous'], 0)
        mp(permissions.View,
            ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
            #['Manager', 'LabManager','LabClerk','Analyst', 'Anonymous'], 0)
        mp('Access contents information',
            ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
            #['Manager', 'LabManager','LabClerk','Analyst', 'Anonymous'], 0)
        mp(permissions.DeleteObjects,
            ['Manager', 'LabManager', 'Owner'], 0)
        portal.worksheets.reindexObject()

        mp = portal.analysisrequests.manage_permission
        mp(permissions.ListFolderContents,
            ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
            #['Manager', 'LabManager','LabClerk','Analyst', 'Anonymous'], 0)
        mp(permissions.AddPortalContent,
            ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
            #['Manager', 'LabManager','LabClerk','Analyst', 'Anonymous'], 0)
        mp(permissions.View,
            ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
            #['Manager', 'LabManager','LabClerk','Analyst', 'Anonymous'], 0)
        mp('Access contents information',
            ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
            #['Manager', 'LabManager','LabClerk','Analyst', 'Anonymous'], 0)
        mp(permissions.DeleteObjects,
            ['Manager', 'LabManager', 'Owner'], 0)
        portal.analysisrequests.reindexObject()

        mp = portal.referencesamples.manage_permission
        mp(permissions.ListFolderContents,
            ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
            #['Manager', 'LabManager','LabClerk','Analyst', 'Anonymous'], 0)
        mp(permissions.AddPortalContent,
            ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
            #['Manager', 'LabManager','LabClerk','Analyst', 'Anonymous'], 0)
        mp(permissions.View,
            ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
            #['Manager', 'LabManager','LabClerk','Analyst', 'Anonymous'], 0)
        mp('Access contents information',
            ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
            #['Manager', 'LabManager','LabClerk','Analyst', 'Anonymous'], 0)
        mp(permissions.DeleteObjects,
            ['Manager', 'LabManager', 'Owner'], 0)
        portal.referencesamples.reindexObject()

        mp = portal.samples.manage_permission
        mp(permissions.ListFolderContents,
            ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
            #['Manager', 'LabManager','LabClerk','Analyst', 'Anonymous'], 0)
        mp(permissions.AddPortalContent,
            ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
            #['Manager', 'LabManager','LabClerk','Analyst', 'Anonymous'], 0)
        mp(permissions.View,
            ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
            #['Manager', 'LabManager','LabClerk','Analyst', 'Anonymous'], 0)
        mp('Access contents information',
            ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
            #['Manager', 'LabManager','LabClerk','Analyst', 'Anonymous'], 0)
        mp(permissions.DeleteObjects,
            ['Manager', 'LabManager', 'Owner'], 0)
        portal.samples.reindexObject()

        mp = portal.invoices.manage_permission
        mp(permissions.ListFolderContents,
            ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
        mp(permissions.AddPortalContent,
            ['Manager', 'LabManager', 'Owner'], 0)
        mp(permissions.DeleteObjects,
            ['Manager', 'LabManager', 'Owner'], 0)
        mp(permissions.View,
            ['Manager', 'LabManager'], 0)
        portal.invoices.reindexObject()

        mp = portal.pricelists.manage_permission
        mp(permissions.ListFolderContents, ['Member'], 1)
        mp(permissions.AddPortalContent,
            ['Manager', 'LabManager', 'Owner'], 0)
        mp(permissions.DeleteObjects,
            ['Manager', 'LabManager', 'Owner'], 0)
        mp(permissions.View,
            ['Manager', 'LabManager'], 0)
        portal.pricelists.reindexObject()

    def setupVersioning(self, portal):
        pr = getToolByName(portal, 'portal_repository')
        versionable_types = list(pr.getVersionableContentTypes())
        for type_id in TYPES_TO_VERSION:
            if type_id not in versionable_types:
                versionable_types.append(type_id)
                pr.addPolicyForContentType(type_id, 'version_on_revert')
                if type_id in AUTO_VERSION:
                    pr.addPolicyForContentType(type_id, 'at_edit_autoversion')
        pr.setVersionableContentTypes(versionable_types)

    def setupCatalogs(self, portal):
        bsc = getToolByName(portal, 'bika_setup_catalog', None)
        if bsc == None:
            logger.warning('Could not find the setup catalog tool.')
            return

        at = getToolByName(portal, 'archetype_tool')
        at.setCatalogsByType('Department', ['portal_catalog','bika_setup_catalog',])
        at.setCatalogsByType('AnalysisCategory', ['portal_catalog','bika_setup_catalog',])
        at.setCatalogsByType('AnalysisService', ['portal_catalog','bika_setup_catalog',])
        at.setCatalogsByType('AnalysisSpec', ['portal_catalog','bika_setup_catalog',])
        at.setCatalogsByType('SampleType', ['portal_catalog','bika_setup_catalog',])
        at.setCatalogsByType('SamplePoint', ['portal_catalog','bika_setup_catalog',])
        at.setCatalogsByType('Instrument', ['portal_catalog','bika_setup_catalog',])
        at.setCatalogsByType('Method', ['portal_catalog','bika_setup_catalog',])
        at.setCatalogsByType('AttachmentType', ['portal_catalog','bika_setup_catalog',])
        at.setCatalogsByType('Calculation', ['portal_catalog','bika_setup_catalog',])
        at.setCatalogsByType('ARProfile', ['portal_catalog','bika_setup_catalog',])
        at.setCatalogsByType('LabProduct', ['portal_catalog','bika_setup_catalog',])
        at.setCatalogsByType('ReferenceManufacturer', ['portal_catalog','bika_setup_catalog',])
        at.setCatalogsByType('ReferenceSupplier', ['portal_catalog','bika_setup_catalog',])
        at.setCatalogsByType('ReferenceDefinition', ['portal_catalog','bika_setup_catalog',])
        at.setCatalogsByType('WorksheetTemplate', ['portal_catalog','bika_setup_catalog',])

        bsc.addIndex('UID', 'FieldIndex')
        bsc.addIndex('id', 'FieldIndex')
        bsc.addIndex('path', 'ExtendedPathIndex', ('getPhysicalPath'))
        bsc.addIndex('getDescription', 'FieldIndex', ('description'))
        bsc.addIndex('sortable_title', 'FieldIndex')
        bsc.addIndex('Title', 'FieldIndex', 'title')
        bsc.addIndex('getCanonicalPath', 'ExtendedPathIndex')
        bsc.addIndex('portal_type', 'FieldIndex')
        bsc.addIndex('review_state', 'FieldIndex')
        bsc.addIndex('inactive_state', 'FieldIndex')
        bsc.addIndex('cancellation_state', 'FieldIndex')
        bsc.addIndex('getType', 'FieldIndex')
        bsc.addIndex('getBlank', 'FieldIndex')
        bsc.addIndex('getBrand', 'FieldIndex')
        bsc.addIndex('getBusinessPhone', 'FieldIndex')
        bsc.addIndex('getCalculationTitle', 'FieldIndex')
        bsc.addIndex('getCalibrationExpiryDate', 'FieldIndex')
        bsc.addIndex('getCategoryTitle', 'FieldIndex')
        bsc.addIndex('getCategoryUID', 'FieldIndex')
        bsc.addIndex('getClientUID', 'FieldIndex')
        bsc.addIndex('getDepartmentTitle', 'FieldIndex')
        bsc.addIndex('getDuplicateVariation', 'FieldIndex')
        bsc.addIndex('getEmailAddress', 'FieldIndex')
        bsc.addIndex('getFax', 'FieldIndex')
        bsc.addIndex('getFormula', 'FieldIndex')
        bsc.addIndex('getFullname', 'FieldIndex')
        bsc.addIndex('getHazardous', 'FieldIndex')
        bsc.addIndex('getInstrumentTitle', 'FieldIndex')
        bsc.addIndex('getKeyword', 'FieldIndex')
        bsc.addIndex('getManager', 'FieldIndex')
        bsc.addIndex('getManagerPhone', 'FieldIndex')
        bsc.addIndex('getManagerEmail', 'FieldIndex')
        bsc.addIndex('getMaxTimeAllowed', 'FieldIndex')
        bsc.addIndex('getMobilePhone', 'FieldIndex')
        bsc.addIndex('getModel', 'FieldIndex')
        bsc.addIndex('getName', 'FieldIndex')
        bsc.addIndex('getPhone', 'FieldIndex')
        bsc.addIndex('getPointOfCapture', 'FieldIndex')
        bsc.addIndex('getPrice', 'FieldIndex')
        bsc.addIndex('getProfileKey', 'FieldIndex')
        bsc.addIndex('getRetentionPeriod', 'FieldIndex')
        bsc.addIndex('getSamplePointTitle', 'FieldIndex')
        bsc.addIndex('getSampleTypeTitle', 'FieldIndex')
        bsc.addIndex('getServiceTitle', 'FieldIndex')
        bsc.addIndex('getServiceUID', 'FieldIndex')
        bsc.addIndex('getTotalPrice', 'FieldIndex')
        bsc.addIndex('getUnit', 'FieldIndex')
        bsc.addIndex('getVATAmount', 'FieldIndex')
        bsc.addIndex('getVolume', 'FieldIndex')

def setupVarious(context):
    """
    Final Bika import steps.
    """
    if context.readDataFile('bika.lims_various.txt') is None:
        return

    site = context.getSite()
    gen = BikaGenerator()
    gen.setupPropertiesTool(site)
    gen.setupDependencies(site)
    gen.setupGroupsAndRoles(site)
    gen.setupPortalContent(site)
    gen.setupPermissions(site)
    gen.setupVersioning(site)
    gen.setupCatalogs(site)
