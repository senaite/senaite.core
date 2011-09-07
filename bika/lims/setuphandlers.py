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

#from Products.GroupUserFolder.GroupsToolPermissions import ManageGroups

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
                       'referencesuppliers',
                       'invoices',
                       'pricelists',
                       'worksheets',
                       'bika_setup' ):
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
                       'bika_referencemanufacturers',
                       'bika_referencedefinitions',
                       'bika_worksheettemplates' ):
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
                     'LabTechnician',
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

        if 'labmanagers' not in portal_groups.listGroupIds():
            portal_groups.addGroup('labmanagers', title = "Lab Managers",
                roles = ['Member', 'Manager', 'LabManager', 'Reviewer'])

        if 'labclerks' not in portal_groups.listGroupIds():
            portal_groups.addGroup('labclerks', title = "Lab Clerks",
                roles = ['Member', 'LabClerk'])

        if 'labtechnicians' not in portal_groups.listGroupIds():
            portal_groups.addGroup('labtechnicians', title = "Lab Technicians",
                roles = ['Member', 'LabTechnician'])

        if 'verifiers' not in portal_groups.listGroupIds():
            portal_groups.addGroup('verifiers', title = "Verifiers",
                roles = ['Verifier'])

        if 'publishers' not in portal_groups.listGroupIds():
            portal_groups.addGroup('publishers', title = "Publishers",
                roles = ['Publisher'])

        if 'clients' not in portal_groups.listGroupIds():
            portal_groups.addGroup('clients', title = "Clients",
                roles = ['Member', ])

        if 'referencesuppliers' not in portal_groups.listGroupIds():
            portal_groups.addGroup('referencesuppliers', title = "",
                roles = ['Member', ])

    def setupPermissions(self, portal):
        """ Set up some suggested role to permission mappings.
        """
        # XXX: All these permission can be set in
        # profiles/default/structure

        mp = portal.manage_permission

        mp(permissions.ListFolderContents,
           ['Manager'], 1)
        mp(permissions.AddPortalContent,
           ['Manager',
            'Owner',
            'LabManager'], 0)
        mp(permissions.FTPAccess,
           ['Manager',
            'LabManager',
            'LabClerk',
            'LabTechnician'], 1)
        mp(permissions.DeleteObjects,
           ['Manager',
            'LabManager',
            'LabClerk',
            'Owner'], 1)
        mp(permissions.ModifyPortalContent,
           ['Manager',
            'LabManager',
            'LabClerk',
            'LabTechnician',
            'Owner'], 1)

        mp(permissions.ManageUsers,
           ['Manager',
            'LabManager', ], 1)
##        mp(ManageGroups,
##           ['Manager',
##            'LabManager', ], 1)
##        mp(permissions.ManagePortal,
##           ['Manager',
##            'LabManager', ], 1)
        mp(ManageBika,
            ['Manager',
             'LabManager'], 1)

        mp(ManageClients,
            ['Manager',
             'LabManager',
             'LabClerk'], 1)
        mp(ManageWorksheets,
            ['Manager',
             'LabManager',
             'LabClerk',
             'LabTechnician'], 1)
        mp(ManageOrders,
            ['Manager',
             'LabManager',
             'LabClerk'], 1)
        mp(ManageAnalysisRequests,
            ['Manager',
             'LabManager',
             'LabClerk',
             'LabTechnician'], 1)
        mp(ManageSample,
            ['Manager',
             'LabManager',
             'LabClerk',
             'LabTechnician'], 1)
        mp(ManageReferenceSuppliers,
            ['Manager',
             'LabManager',
             'LabClerk',
             'LabTechnician'], 1)
        mp(ManageReference,
            ['Manager',
             'LabManager',
             'LabClerk',
             'LabTechnician'], 1)
        mp(ViewResults,
            ['Manager',
             'LabManager',
             'LabClerk',
             'Owner'], 1)
        mp(ManageInvoices,
            ['Manager',
             'LabManager',
             'Owner'], 1)
        mp(ManagePricelists,
            ['Manager',
             'LabManager',
             'Owner'], 1)
        mp(PostInvoiceBatch,
            ['Manager',
             'LabManager',
             'Owner'], 1)

        # Workflow permissions
        mp(ReceiveSample,
            ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(SubmitSample,
            ['Manager', 'LabManager', 'LabClerk', 'LabTechnician'], 1)
        mp(VerifyResults,
            ['Manager', 'LabManager', 'Reviewer', 'Verifier'], 1)
        mp(PublishSample,
            ['Manager', 'LabManager', 'Reviewer', 'Publisher'], 1)
        mp(RetractSample,
            ['Manager', 'LabManager', 'LabClerk', 'Reviewer', 'Verifier'], 1)
        mp(ImportSample,
            ['Manager', 'LabManager', 'LabClerk', 'LabTechnician'], 1)
        mp(SubmitWorksheet,
            ['Manager', 'LabManager', 'LabClerk', 'LabTechnician'], 1)
        mp(VerifyWorksheet,
            ['Manager', 'LabManager', 'Reviewer', 'Verifier'], 1)
        mp(RetractWorksheet,
            ['Manager', 'LabManager', 'Reviewer', 'Verifier'], 1)
        mp(DispatchOrder,
            ['Manager', 'LabManager', 'LabClerk'], 1)

        # Worksheet permissions
        mp(AssignAnalyses,
            ['Manager', 'LabManager', 'LabClerk', 'LabTechnician'], 1)
        mp(DeleteAnalyses,
            ['Manager', 'LabManager', 'LabClerk', 'LabTechnician'], 1)
        mp(SubmitResults,
            ['Manager', 'LabManager', 'LabClerk', 'LabTechnician'], 1)

        mp = portal.clients.manage_permission
        mp(permissions.ListFolderContents,
            ['Manager', 'LabManager', 'LabClerk', 'LabTechnician'], 1)
        mp(permissions.AddPortalContent,
            ['Manager', 'LabManager', 'LabClerk', 'LabTechnician',
             'Owner'], 0)
        mp(permissions.View,
            ['Manager', 'LabManager', 'LabClerk', 'LabTechnician',
             'Owner'], 0)
        portal.clients.reindexObject()

        mp = portal.referencesuppliers.manage_permission
        mp(permissions.ListFolderContents,
            ['Manager', 'LabManager', 'LabClerk', 'LabTechnician'], 1)
        mp(permissions.AddPortalContent,
            ['Manager', 'LabManager', 'LabClerk', 'LabTechnician',
             'Owner'], 0)
        mp(permissions.View,
            ['Manager', 'LabManager', 'LabClerk', 'LabTechnician',
             'Owner'], 0)
        portal.referencesuppliers.reindexObject()

        mp = portal.worksheets.manage_permission
        mp(permissions.ListFolderContents,
            ['Manager', 'LabManager', 'LabClerk', 'LabTechnician'], 1)
        mp(permissions.AddPortalContent,
            ['Manager', 'LabManager', 'LabClerk', 'LabTechnician'], 0)
        mp(permissions.DeleteObjects,
            ['Manager', 'LabManager', 'Owner'], 0)
        mp(permissions.View,
            ['Manager', 'LabManager', 'LabClerk', 'LabTechnician'], 0)
        portal.worksheets.reindexObject()

        mp = portal.invoices.manage_permission
        mp(permissions.ListFolderContents,
            ['Manager', 'LabManager', 'LabClerk', 'LabTechnician'], 1)
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

    def setupProxyRoles(self, portal):
        """ Set up proxy roles for workflow scripts
        """
        # XXX: Need to figure out how to do this with GenericSetup
        script = portal.portal_workflow.bika_analysis_workflow.scripts.default
        script.manage_proxy(roles = ('Manager',))
        script = portal.portal_workflow.bika_arimport_workflow.scripts.default
        script.manage_proxy(roles = ('Manager',))
        script = portal.portal_workflow.bika_order_workflow.scripts.default
        script.manage_proxy(roles = ('Manager',))
        script = portal.portal_workflow.bika_sample_workflow.scripts.default
        script.manage_proxy(roles = ('Manager',))
        script = portal.portal_workflow.bika_referencesample_workflow.scripts.default
        script.manage_proxy(roles = ('Manager',))
        script = portal.portal_workflow.bika_worksheet_workflow.scripts.default
        script.manage_proxy(roles = ('Manager',))
        script = portal.portal_workflow.bika_worksheetanalysis_workflow.scripts.default
        script.manage_proxy(roles = ('Manager',))
        script = portal.portal_workflow.bika_referenceanalysis_workflow.scripts.default
        script.manage_proxy(roles = ('Manager',))

    def setupVersioning(self, portal):
        DEFAULT_POLICIES = ('at_edit_autoversion', 'version_on_revert')
        pr = getToolByName(portal, 'portal_repository')
        versionable_types = list(pr.getVersionableContentTypes())

        for type_id in TYPES_TO_VERSION:
            if type_id not in versionable_types:
                # use append() to make sure we don't overwrite any
                # content-types which may already be under version control
                versionable_types.append(type_id)
                # Add default versioning policies to the versioned type
                for policy_id in DEFAULT_POLICIES:
                    pr.addPolicyForContentType(type_id, policy_id)
        pr.setVersionableContentTypes(versionable_types)

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
    gen.setupProxyRoles(site)
    gen.setupPortalContent(site)
    gen.setupPermissions(site)
    gen.setupVersioning(site)


#    # install mail templates
#    install_mail_templates(self, portal, templates, out)
#
#    if 'PortalTransport' in portal.objectIds():
#        portal.portal_mailtemplates.manage_delObjects(
#            ids = ['PortalTransport'])
#
#    # import charts
#    if 'charts' not in portal.objectIds():
#        filepath = '%s/charts.zexp' % package_home(GLOBALS)
#        portal._importObjectFromFile(filepath, set_owner = 1)
#
#    # Move checksetup to be first action of Client
#    actions = []
#    indices = []
#    idx = 0
#    for action in self.portal_types['Client'].listActions():
#        if action.id not in ['checkstate', ]:
#            actions.append(action)
#            indices.append(idx)
#        idx += 1
#
#    del_idx = tuple(indices)
#    self.portal_types['Client'].deleteActions(del_idx)
#    for action in actions:
#        self.portal_types['Client'].addAction(
#             action.id,
#             name = action.Title(),
#             action = action.getActionExpression(),
#             condition = action.getCondition(),
#             permission = action.getPermissions(),
#             category = action.getCategory(),
#             visible = action.getVisibility(),
#                        )


#    # Add UID index
#    catalog_indexes = (
#        { 'name'  : 'UID',
#          'type'  : 'FieldIndex'
#          },
#                        )
#    cat = portal.portal_catalog
#    for idx in catalog_indexes:
#        if idx['name'] in cat.indexes():
#            pass
#        else:
#            cat.addIndex(**idx)
#            cat.reindexIndex('UID', portal)

