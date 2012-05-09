""" Bika setup handlers. """

from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.config import *
from bika.lims.permissions import *
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

        obj = portal._getOb('front-page')
        alsoProvides(obj, IHaveNoBreadCrumbs)

        # remove undesired content objects
##        del_ids = []
##        for obj_id in ['Members', 'front-page', 'news', 'events']:
##            if obj_id in portal.objectIds():
##                del_ids.append(obj_id)
##        if del_ids:
##            portal.manage_delObjects(ids = del_ids)

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
                       'bika_containers',
                       'bika_containertypes',
                       'bika_preservations',
                       'bika_instruments',
                       'bika_analysisspecs',
                       'bika_arprofiles',
                       'bika_artemplates',
                       'bika_labcontacts',
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
        obj = portal._getOb('bika_methods')
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

        if 'Preservers' not in portal_groups.listGroupIds():
            portal_groups.addGroup('Preservers', title = "Preservers",
                roles = ['Preserver'])

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

        # Root permissions
        mp = portal.manage_permission

        mp(permissions.AddPortalContent, ['Manager', 'Owner', 'LabManager'], 1)
        mp(AddClientFolder, ['Manager'], 1)
        mp(AddClient, ['Manager', 'Owner', 'LabManager'], 1)
        mp(AddAnalysisRequest, ['Manager', 'Owner', 'LabManager', 'LabClerk', 'Sampler'], 1)
        mp(AddSample, ['Manager', 'Owner', 'LabManager', 'LabClerk', 'Sampler'], 1)
        mp(AddAnalysis, ['Manager', 'Owner', 'LabManager', 'LabClerk', 'Sampler'], 1)
        mp(AddARProfile, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)
        mp(AddARTemplate, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)
        mp(AddMethod, ['Manager', 'LabManager'], 1)

        mp(permissions.ListFolderContents, ['Manager', 'Owner'], 1)
        mp(permissions.FTPAccess, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
        mp(permissions.DeleteObjects, ['Manager', 'LabManager', 'LabClerk', 'Owner'], 1)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner'], 1)
        mp(permissions.ManageUsers, ['Manager', 'LabManager', ], 1)

        mp(ApplyVersionControl, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner'], 1)
        mp(SaveNewVersion, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner'], 1)
        mp(AccessPreviousVersions, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner'], )

        mp(ManageBika, ['Manager', 'LabManager'], 1)
        mp(ManageClients, ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(ManageWorksheets, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
        mp(ManageOrders, ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(ManageAnalysisRequests, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler', 'Preserver', 'Owner'], 1)
        mp(ManageSamples, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler', 'Preserver', 'Owner'], 1)
        mp(ManageReferenceSuppliers, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
        mp(ManageReference, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
        mp(ManagePricelists, ['Manager', 'LabManager', 'Owner'], 1)
        mp(ManageARImport, ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(DispatchOrder, ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(PostInvoiceBatch, ['Manager', 'LabManager', 'Owner'], 1)

        mp(CancelAndReinstate, ['Manager', 'LabManager'], 0)

        mp(VerifyOwnResults, ['Manager', ], 1)

        mp(SampleSample, ['Manager', 'LabManager', 'Sampler'], 0)
        mp(PreserveSample, ['Manager', 'LabManager', 'Preserver'], 0)
        mp(ReceiveSample, ['Manager', 'LabManager', 'LabClerk', 'Sampler'], 1)
        mp(ExpireSample, ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(DisposeSample, ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(ImportAnalysis, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
        mp(RejectWorksheet, ['Manager', 'LabManager', 'Verifier'], 1)
        mp(Retract, ['Manager', 'LabManager', 'Verifier'], 1)
        mp(Verify, ['Manager', 'LabManager', 'Verifier'], 1)
        mp(Publish, ['Manager', 'LabManager', 'Publisher'], 1)
        mp(EditSample, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler'], 1)
        mp(EditAR, ['Manager', 'LabManager', 'LabClerk', 'Sampler'], 1)
        mp(EditWorksheet, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
        mp(ResultsNotRequested, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
        mp(ManageInvoices, ['Manager', 'LabManager', 'Owner'], 1)
        mp(ViewResults, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler'], 1)
        mp(EditResults, ['Manager', 'LabManager', 'Analyst'], 1)
        mp(EditFieldResults, ['Manager', 'LabManager', 'Sampler'], 1)
        mp(CancelAndReinstate, ['Manager', 'LabManager', 'Owner'], 1)

        # /clients folder permissions
        mp = portal.clients.manage_permission
        mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'Member', 'LabClerk', 'Analyst', 'Sampler', 'Preserver'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Member', 'Analyst', 'Sampler', 'Preserver'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'Member', 'LabClerk', 'Analyst', 'Sampler', 'Preserver', 'Owner'], 0)
        mp(ManageClients, ['Manager', 'LabManager', 'LabClerk', 'Owner'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'LabClerk', 'Owner'], 0)
        portal.clients.reindexObject()

        # /worksheets folder permissions
        mp = portal.worksheets.manage_permission
        mp(CancelAndReinstate, ['Manager', 'LabManager', 'LabClerk'], 0)
        mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
        mp(permissions.DeleteObjects, ['Manager', 'LabManager', 'Owner'], 0)
        portal.worksheets.reindexObject()

        # /analysisrequests folder permissions
        mp = portal.analysisrequests.manage_permission
        mp(CancelAndReinstate, ['Manager', 'LabManager', 'LabClerk'], 0)
        mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler'], 0)
        mp(permissions.DeleteObjects, ['Manager', 'LabManager', 'Owner'], 0)
        portal.analysisrequests.reindexObject()

        # /referencesamples folder permissions
        mp = portal.referencesamples.manage_permission
        mp(CancelAndReinstate, ['Manager', 'LabManager', 'LabClerk'], 0)
        mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
        mp(permissions.DeleteObjects, ['Manager', 'LabManager', 'Owner'], 0)
        portal.referencesamples.reindexObject()

        # /samples folder permissions
        mp = portal.samples.manage_permission
        mp(CancelAndReinstate, ['Manager', 'LabManager', 'LabClerk'], 0)
        mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler', 'Preserver'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler', 'Preserver'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'LabClerk', 'Analyst','Sampler', 'Preserver'], 0)
        mp(permissions.DeleteObjects, ['Manager', 'LabManager', 'Owner'], 0)
        portal.samples.reindexObject()

        # /reports folder permissions
        mp = portal.reports.manage_permission
        mp(permissions.ListFolderContents, ['Manager', 'Member', ], 0)
        mp(permissions.View, ['Manager', 'Member', ], 0)
        mp(permissions.AddPortalContent, ['Manager', 'Member', ], 0)
        mp('Access contents information', ['Manager', 'Member',], 0)
        mp(permissions.DeleteObjects, ['Manager', 'LabManager', 'Owner'], 0)
        mp('ATContentTypes: Add Image', ['Manager', 'Member',], 0)
        mp('ATContentTypes: Add File', ['Manager', 'Member',], 0)
        portal.reports.reindexObject()

        # /invoices folder permissions
        mp = portal.invoices.manage_permission
        mp(CancelAndReinstate, ['Manager', 'LabManager', 'LabClerk'], 0)
        mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'Owner'], 0)
        mp(permissions.DeleteObjects, ['Manager', 'LabManager', 'Owner'], 0)
        mp(permissions.View, ['Manager', 'LabManager'], 0)
        portal.invoices.reindexObject()

        # /pricelists folder permissions
        mp = portal.pricelists.manage_permission
        mp(CancelAndReinstate, ['Manager', 'LabManager', 'LabClerk'], 0)
        mp(permissions.ListFolderContents, ['Member'], 1)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'Owner'], 0)
        mp(permissions.DeleteObjects, ['Manager', 'LabManager', 'Owner'], 0)
        mp(permissions.View, ['Manager', 'LabManager'], 0)
        portal.pricelists.reindexObject()

    def setupVersioning(self, portal):
        portal_repository = getToolByName(portal, 'portal_repository')
        versionable_types = list(portal_repository.getVersionableContentTypes())

        for type_id in VERSIONABLE_TYPES:
            if type_id not in versionable_types:
                versionable_types.append(type_id)
                # Add default versioning policies to the versioned type
                for policy_id in DEFAULT_POLICIES:
                    portal_repository.addPolicyForContentType(type_id, policy_id)
        portal_repository.setVersionableContentTypes(versionable_types)

    def setupCatalogs(self, portal):
        # an item should belong to only one catalog.
        # that way looking it up means first looking up *the* catalog
        # in which it is indexed, as well as making it cheaper to index.

        bac = getToolByName(portal, 'bika_analysis_catalog', None)
        if bac == None:
            logger.warning('Could not find the bika_analysis_catalog tool.')
            return

        at = getToolByName(portal, 'archetype_tool')
        at.setCatalogsByType('Analysis', ['bika_analysis_catalog', ])
        at.setCatalogsByType('ReferenceAnalysis', ['bika_analysis_catalog', ])
        at.setCatalogsByType('DuplicateAnalysis', ['bika_analysis_catalog', ])

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
        bac.manage_addProduct['ZCTextIndex'].manage_addLexicon('Lexicon', 'Lexicon', elem)
        zc_extras = Empty()
        zc_extras.index_type = 'Okapi BM25 Rank'
        zc_extras.lexicon_id = 'Lexicon'

        bac.addIndex('path', 'ExtendedPathIndex', ('getPhysicalPath'))
        bac.addIndex('allowedRolesAndUsers', 'KeywordIndex')
        bac.addIndex('UID', 'FieldIndex')
        bac.addIndex('Title', 'FieldIndex')
        bac.addIndex('Description', 'ZCTextIndex', zc_extras)
        bac.addIndex('id', 'FieldIndex')
        bac.addIndex('Type', 'FieldIndex')
        bac.addIndex('portal_type', 'FieldIndex')
        bac.addIndex('created', 'DateIndex')
        bac.addIndex('getObjPositionInParent', 'GopipIndex')
        bac.addIndex('title', 'FieldIndex', 'Title')
        bac.addIndex('sortable_title', 'FieldIndex')
        bac.addIndex('description', 'FieldIndex', 'Description')
        bac.addIndex('review_state', 'FieldIndex')
        bac.addIndex('worksheetanalysis_review_state', 'FieldIndex')
        bac.addIndex('cancellation_state', 'FieldIndex')

        bac.addIndex('getDateAnalysisPublished', 'DateIndex')
        bac.addIndex('getDueDate', 'DateIndex')

        bac.addIndex('getClientUID', 'FieldIndex')
        bac.addIndex('getAnalyst', 'FieldIndex')
        bac.addIndex('getClientTitle', 'FieldIndex')
        bac.addIndex('getRequestID', 'FieldIndex')
        bac.addIndex('getClientOrderNumber', 'FieldIndex')
        bac.addIndex('getKeyword', 'FieldIndex')
        bac.addIndex('getServiceTitle', 'FieldIndex')
        bac.addIndex('getServiceUID', 'FieldIndex')
        bac.addIndex('getCategoryUID', 'FieldIndex')
        bac.addIndex('getCategoryTitle', 'FieldIndex')
        bac.addIndex('getPointOfCapture', 'FieldIndex')
        bac.addIndex('getDateReceived', 'DateIndex')

        bc = getToolByName(portal, 'bika_catalog', None)
        if bc == None:
            logger.warning('Could not find the bika_catalog tool.')
            return

        at = getToolByName(portal, 'archetype_tool')
        at.setCatalogsByType('AnalysisRequest', ['bika_catalog', ])
        at.setCatalogsByType('Sample', ['bika_catalog', ])
        at.setCatalogsByType('SamplePartition', ['bika_catalog', ])
        at.setCatalogsByType('ReferenceSample', ['bika_catalog', ])

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
        bc.manage_addProduct['ZCTextIndex'].manage_addLexicon('Lexicon', 'Lexicon', elem)
        zc_extras = Empty()
        zc_extras.index_type = 'Okapi BM25 Rank'
        zc_extras.lexicon_id = 'Lexicon'

        bc.addIndex('path', 'ExtendedPathIndex', ('getPhysicalPath'))
        bc.addIndex('allowedRolesAndUsers', 'KeywordIndex')
        bc.addIndex('UID', 'FieldIndex')
        bc.addIndex('SearchableText', 'ZCTextIndex', zc_extras)
        bc.addIndex('Title', 'ZCTextIndex', zc_extras)
        bc.addIndex('Description', 'ZCTextIndex', zc_extras)
        bc.addIndex('id', 'FieldIndex')
        bc.addIndex('getId', 'FieldIndex')
        bc.addIndex('Type', 'FieldIndex')
        bc.addIndex('portal_type', 'FieldIndex')
        bc.addIndex('created', 'DateIndex')
        bc.addIndex('getObjPositionInParent', 'GopipIndex')
        bc.addIndex('title', 'FieldIndex', 'Title')
        bc.addIndex('sortable_title', 'FieldIndex')
        bc.addIndex('description', 'FieldIndex', 'Description')
        bc.addIndex('review_state', 'FieldIndex')
        bc.addIndex('inactive_state', 'FieldIndex')
        bc.addIndex('cancellation_state', 'FieldIndex')

        bc.addIndex('getSampleID', 'FieldIndex')
        bc.addIndex('getSampleUID', 'FieldIndex')
        bc.addIndex('getRequestID', 'FieldIndex')
        bc.addIndex('getClientReference', 'FieldIndex')
        bc.addIndex('getClientOrderNumber', 'FieldIndex')
        bc.addIndex('getClientSampleID', 'FieldIndex')
        bc.addIndex('getServiceTitle', 'FieldIndex')
        bc.addIndex('getSamplePointTitle', 'FieldIndex')
        bc.addIndex('getSampleTypeTitle', 'FieldIndex')
        bc.addIndex('getDueDate', 'DateIndex')
        bc.addIndex('getSamplingDate', 'DateIndex')
        bc.addIndex('getDateSampled', 'DateIndex')
        bc.addIndex('getDateReceived', 'DateIndex')
        bc.addIndex('getDatePublished', 'DateIndex')
        bc.addIndex('getDateExpired', 'DateIndex')
        bc.addIndex('getDisposalDate', 'DateIndex')
        bc.addIndex('getDateDisposed', 'DateIndex')
        bc.addIndex('getDateOpened', 'DateIndex')
        bc.addIndex('getExpiryDate', 'DateIndex')
        bc.addIndex('getClientUID', 'FieldIndex')
        bc.addIndex('getSamplePointUID', 'FieldIndex')
        bc.addIndex('getSampleTypeUID', 'FieldIndex')
        bc.addIndex('getReferenceDefinitionUID', 'FieldIndex')
        bc.addIndex('getPreserver', 'FieldIndex')
        bc.addIndex('getSampler', 'FieldIndex')
        bc.addIndex('getWorksheetTemplateTitle', 'FieldIndex')
        bc.addIndex('getAnalyst', 'FieldIndex')

        bsc = getToolByName(portal, 'bika_setup_catalog', None)
        if bsc == None:
            logger.warning('Could not find the setup catalog tool.')
            return

        at = getToolByName(portal, 'archetype_tool')
        at.setCatalogsByType('Department', ['bika_setup_catalog', ])
        at.setCatalogsByType('Container', ['bika_setup_catalog', ])
        at.setCatalogsByType('ContainerType', ['bika_setup_catalog', ])
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
        at.setCatalogsByType('ARTemplate', ['bika_setup_catalog', ])
        at.setCatalogsByType('LabProduct', ['bika_setup_catalog', ])
        at.setCatalogsByType('LabContact', ['bika_setup_catalog', ])
        at.setCatalogsByType('Preservation', ['bika_setup_catalog', ])
        at.setCatalogsByType('ReferenceManufacturer', ['bika_setup_catalog', ])
        at.setCatalogsByType('ReferenceSupplier', ['bika_setup_catalog', ])
        at.setCatalogsByType('ReferenceDefinition', ['bika_setup_catalog', ])
        at.setCatalogsByType('Unit', ['bika_setup_catalog', ])
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
    try:
        from Products.CMFEditions.setuphandlers import DEFAULT_POLICIES
        # we're on plone < 4.1, configure versionable types manually
        gen.setupVersioning(site)
    except ImportError:
        # repositorytool.xml will be used
        pass
    gen.setupCatalogs(site)


