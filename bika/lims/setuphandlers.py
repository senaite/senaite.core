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

class Empty: pass

class BikaGenerator:

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
                       'reports',
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
                       'bika_worksheettemplates'):
            obj = bika_setup._getOb(obj_id)
            obj.unmarkCreationFlag()
            obj.reindexObject()

        lab = bika_setup.laboratory
        lab.edit(title = _('Laboratory'))
        lab.unmarkCreationFlag()
        lab.reindexObject()

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
                     'Sampler',
                     'Preserver',
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

        if 'Samplers' not in portal_groups.listGroupIds():
            portal_groups.addGroup('Samplers', title = "Samplers",
                roles = ['Sampler'])

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

        mp = portal.manage_permission

        mp(permissions.ListFolderContents, ['Manager', ], 1)
        mp(permissions.AddPortalContent, ['Manager', 'Owner', 'LabManager'], 0)
        mp(permissions.FTPAccess, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
        mp(permissions.DeleteObjects, ['Manager', 'LabManager', 'LabClerk', 'Owner'], 1)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner'], 1)
        mp(permissions.ManageUsers, ['Manager', 'LabManager', ], 1)

        mp(ApplyVersionControl, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner'], 0)
        mp(SaveNewVersion, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner'], 0)
        mp(AccessPreviousVersions, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner'], 0)

        mp(ManageBika, ['Manager', 'LabManager'], 1)
        mp(ManageClients, ['Manager', 'LabManager', 'LabClerk', 'Sampler', 'Preserver'], 1)
        mp(ManageWorksheets, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
        mp(ManageOrders, ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(ManageAnalysisRequests, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler', 'Preserver'], 1)
        mp(ManageSample, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler', 'Preserver'], 1)
        mp(ManageReferenceSuppliers, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
        mp(ManageReference, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
        mp(ManagePricelists, ['Manager', 'LabManager', 'Owner'], 1)
        mp(ManageARImport, ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(DispatchOrder, ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(PostInvoiceBatch, ['Manager', 'LabManager', 'Owner'], 1)

        mp(ReceiveSample, ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(ExpireSample, ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(DisposeSample, ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(ImportAnalysis, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
        mp(RejectWorksheet, ['Manager', 'LabManager', 'Verifier'], 1)
        mp(Retract, ['Manager', 'LabManager', 'Verifier'], 1)
        mp(Verify, ['Manager', 'LabManager', 'Verifier'], 1)
        mp(VerifyOwnResults, ['Manager', ], 1)
        mp(Publish, ['Manager', 'LabManager', 'Publisher'], 1)
        mp(EditSample, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
        mp(EditAR, ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(EditWorksheet, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
        mp(ManageResults, ['Manager', 'LabManager', 'Analyst'], 1)
        mp(ResultsNotRequested, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
        mp(ManageInvoices, ['Manager', 'LabManager', 'Owner'], 1)
        mp(ViewResults, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
        mp(EditResults, ['Manager', 'LabManager', 'Analyst'], 1)
        mp(CancelAndReinstate, ['Manager', 'LabManager', 'Owner'], 1)

        mp = portal.clients.manage_permission
        mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Member', 'Sampler', 'Preserver'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'Sampler', 'Preserver'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'LabClerk', 'Member', 'Analyst', 'Sampler', 'Preserver'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'LabClerk', 'Owner'], 0)
        portal.clients.reindexObject()

        mp = portal.worksheets.manage_permission
        mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
        mp(permissions.DeleteObjects, ['Manager', 'LabManager', 'Owner'], 0)
        portal.worksheets.reindexObject()

        mp = portal.analysisrequests.manage_permission
        mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
        mp(permissions.DeleteObjects, ['Manager', 'LabManager', 'Owner'], 0)
        portal.analysisrequests.reindexObject()

        mp = portal.referencesamples.manage_permission
        mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
        mp(permissions.DeleteObjects, ['Manager', 'LabManager', 'Owner'], 0)
        portal.referencesamples.reindexObject()

        mp = portal.samples.manage_permission
        mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler', 'Preserver'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler', 'Preserver'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'LabClerk', 'Analyst','Sampler', 'Preserver'], 0)
        mp(permissions.DeleteObjects, ['Manager', 'LabManager', 'Owner'], 0)
        portal.samples.reindexObject()

        mp = portal.invoices.manage_permission
        mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'Owner'], 0)
        mp(permissions.DeleteObjects, ['Manager', 'LabManager', 'Owner'], 0)
        mp(permissions.View, ['Manager', 'LabManager'], 0)
        portal.invoices.reindexObject()

        mp = portal.pricelists.manage_permission
        mp(permissions.ListFolderContents, ['Member'], 1)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'Owner'], 0)
        mp(permissions.DeleteObjects, ['Manager', 'LabManager', 'Owner'], 0)
        mp(permissions.View, ['Manager', 'LabManager'], 0)
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

        # an item should belong to only one catalog.
        # that way looking it up means first looking up *the* catalog
        # in which it is indexed, as well as making it cheaper to index.

        at = getToolByName(portal, 'archetype_tool')
        at.setCatalogsByType('Department', ['bika_setup_catalog', ])
        at.setCatalogsByType('Container', ['bika_setup_catalog', ])
        at.setCatalogsByType('AnalysisCategory', ['bika_setup_catalog', ])
        at.setCatalogsByType('AnalysisService', ['bika_setup_catalog', ])
        at.setCatalogsByType('AnalysisSpec', ['bika_setup_catalog', ])
        at.setCatalogsByType('SampleType', ['bika_setup_catalog', ])
        at.setCatalogsByType('SamplePoint', ['bika_setup_catalog', ])
        at.setCatalogsByType('Instrument', ['bika_setup_catalog', ])
        at.setCatalogsByType('Method', ['bika_setup_catalog', ])
        at.setCatalogsByType('AttachmentType', ['bika_setup_catalog', ])
        at.setCatalogsByType('Calculation', ['bika_setup_catalog', ])
        at.setCatalogsByType('ARProfile', ['bika_setup_catalog', ])
        at.setCatalogsByType('LabProduct', ['bika_setup_catalog', ])
        at.setCatalogsByType('LabContact', ['bika_setup_catalog', ])
        at.setCatalogsByType('Preservation', ['bika_setup_catalog', ])
        at.setCatalogsByType('ReferenceManufacturer', ['bika_setup_catalog', ])
        at.setCatalogsByType('ReferenceSupplier', ['bika_setup_catalog', ])
        at.setCatalogsByType('ReferenceDefinition', ['bika_setup_catalog', ])
        at.setCatalogsByType('WorksheetTemplate', ['bika_setup_catalog', ])

        # create lexicon
        wordSplitter = Empty()
        wordSplitter.group = 'Word Splitter'
        wordSplitter.name = 'Unicode Whitespace splitter'
        caseNormalizer = Empty()
        caseNormalizer.group = 'Case Normalizer'
        caseNormalizer.name = 'Unicode Case Normalizer'
        stopWords = Empty()
        stopWords.group = 'Stop Words'
        stopWords.name = 'Remove listed and single char words'
        elem = [wordSplitter, caseNormalizer, stopWords]
        bsc.manage_addProduct['ZCTextIndex'].manage_addLexicon('Lexicon', 'Lexicon', elem)
        zc_extras = Empty()
        zc_extras.index_type = 'Okapi BM25 Rank'
        zc_extras.lexicon_id = 'Lexicon'

        bsc.addIndex('path', 'ExtendedPathIndex', ('getPhysicalPath'))
        bsc.addIndex('allowedRolesAndUsers', 'KeywordIndex')
        bsc.addIndex('UID', 'FieldIndex')
        bsc.addIndex('SearchableText', 'ZCTextIndex', zc_extras)
        bsc.addIndex('Title', 'ZCTextIndex', zc_extras)
        bsc.addIndex('Description', 'ZCTextIndex', zc_extras)
        bsc.addIndex('id', 'FieldIndex')
        bsc.addIndex('getId', 'FieldIndex')
        bsc.addIndex('Type', 'FieldIndex')
        bsc.addIndex('portal_type', 'FieldIndex')
        bsc.addIndex('created', 'DateIndex')
        bsc.addIndex('getObjPositionInParent', 'GopipIndex')

        bsc.addIndex('title', 'FieldIndex', 'Title')
        bsc.addIndex('sortable_title', 'FieldIndex')
        bsc.addIndex('description', 'FieldIndex', 'Description')

        bsc.addIndex('review_state', 'FieldIndex')
        bsc.addIndex('inactive_state', 'FieldIndex')
        bsc.addIndex('cancellation_state', 'FieldIndex')

        bsc.addIndex('getAccredited', 'FieldIndex')
        bsc.addIndex('getAnalyst', 'FieldIndex')
        bsc.addIndex('getType', 'FieldIndex')
        bsc.addIndex('getBlank', 'FieldIndex')
        bsc.addIndex('getBrand', 'FieldIndex')
        bsc.addIndex('getCalculationTitle', 'FieldIndex')
        bsc.addIndex('getCalculationUID', 'FieldIndex')
        bsc.addIndex('getCalibrationExpiryDate', 'FieldIndex')
        bsc.addIndex('getCategoryTitle', 'FieldIndex')
        bsc.addIndex('getCategoryUID', 'FieldIndex')
        bsc.addIndex('getClientUID', 'FieldIndex')
        bsc.addIndex('getDepartmentTitle', 'FieldIndex')
        bsc.addIndex('getDuplicateVariation', 'FieldIndex')
        bsc.addIndex('getFormula', 'FieldIndex')
        bsc.addIndex('getFullname', 'FieldIndex')
        bsc.addIndex('getHazardous', 'FieldIndex')
        bsc.addIndex('getInstrumentTitle', 'FieldIndex')
        bsc.addIndex('getKeyword', 'FieldIndex')
        bsc.addIndex('getManagerName', 'FieldIndex')
        bsc.addIndex('getManagerPhone', 'FieldIndex')
        bsc.addIndex('getManagerEmail', 'FieldIndex')
        bsc.addIndex('getMaxTimeAllowed', 'FieldIndex')
        bsc.addIndex('getModel', 'FieldIndex')
        bsc.addIndex('getName', 'FieldIndex')
        bsc.addIndex('getPointOfCapture', 'FieldIndex')
        bsc.addIndex('getPrice', 'FieldIndex')
        bsc.addIndex('getProfileKey', 'FieldIndex')
        bsc.addIndex('getRetentionPeriod', 'FieldIndex')
        bsc.addIndex('getSamplePointTitle', 'FieldIndex')
        bsc.addIndex('getSampleTypeTitle', 'FieldIndex')
        bsc.addIndex('getSamplePointUID', 'FieldIndex')
        bsc.addIndex('getSampleTypeUID', 'FieldIndex')
        bsc.addIndex('getServiceTitle', 'FieldIndex')
        bsc.addIndex('getServiceUID', 'FieldIndex')
        bsc.addIndex('getTotalPrice', 'FieldIndex')
        bsc.addIndex('getUnit', 'FieldIndex')
        bsc.addIndex('getVATAmount', 'FieldIndex')
        bsc.addIndex('getVolume', 'FieldIndex')

        bsc.addColumn('path')
        bsc.addColumn('UID')
        bsc.addColumn('id')
        bsc.addColumn('getId')
        bsc.addColumn('Type')
        bsc.addColumn('portal_type')
        bsc.addColumn('getObjPositionInParent')

        bsc.addColumn('Title')
        bsc.addColumn('Description')
        bsc.addColumn('title')
        bsc.addColumn('sortable_title')
        bsc.addColumn('description')

        bsc.addColumn('review_state')
        bsc.addColumn('inactive_state')
        bsc.addColumn('cancellation_state')

        bsc.addColumn('getAccredited')
        bsc.addColumn('getType')
        bsc.addColumn('getBlank')
        bsc.addColumn('getBrand')
        bsc.addColumn('getCalculationTitle')
        bsc.addColumn('getCalculationUID')
        bsc.addColumn('getCalibrationExpiryDate')
        bsc.addColumn('getCategoryTitle')
        bsc.addColumn('getCategoryUID')
        bsc.addColumn('getClientUID')
        bsc.addColumn('getDepartmentTitle')
        bsc.addColumn('getDuplicateVariation')
        bsc.addColumn('getFormula')
        bsc.addColumn('getFullname')
        bsc.addColumn('getHazardous')
        bsc.addColumn('getInstrumentTitle')
        bsc.addColumn('getKeyword')
        bsc.addColumn('getManagerName')
        bsc.addColumn('getManagerPhone')
        bsc.addColumn('getManagerEmail')
        bsc.addColumn('getMaxTimeAllowed')
        bsc.addColumn('getModel')
        bsc.addColumn('getName')
        bsc.addColumn('getPointOfCapture')
        bsc.addColumn('getPrice')
        bsc.addColumn('getProfileKey')
        bsc.addColumn('getRetentionPeriod')
        bsc.addColumn('getSamplePointTitle')
        bsc.addColumn('getSampleTypeTitle')
        bsc.addColumn('getSamplePointUID')
        bsc.addColumn('getSampleTypeUID')
        bsc.addColumn('getServiceTitle')
        bsc.addColumn('getServiceUID')
        bsc.addColumn('getTotalPrice')
        bsc.addColumn('getUnit')
        bsc.addColumn('getVATAmount')
        bsc.addColumn('getVolume')

def setupVarious(context):
    """
    Final Bika import steps.
    """
    if context.readDataFile('bika.lims_various.txt') is None:
        return

    site = context.getSite()
    gen = BikaGenerator()
    gen.setupGroupsAndRoles(site)
    gen.setupPortalContent(site)
    gen.setupPermissions(site)
    gen.setupVersioning(site)
    gen.setupCatalogs(site)
