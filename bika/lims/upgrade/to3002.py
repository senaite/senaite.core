from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from bika.lims.permissions import AddAttachment


def upgrade(tool):
    # Hack prevent out-of-date upgrading
    # Related: PR #1484
    # https://github.com/bikalabs/Bika-LIMS/pull/1484
    from bika.lims.upgrade import skip_pre315
    if skip_pre315(aq_parent(aq_inner(tool))):
        return True

    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    # Add new Client role
    role = "Client"
    if role not in portal.acl_users.portal_role_manager.listRoleIds():
        portal.acl_users.portal_role_manager.addRole(role)
        portal._addRole(role)

    # Add the role Client role to Clients group
    portal.portal_groups.editGroup('Clients', roles=['Member',
                                                     'Authenticated',
                                                     'Client'])

    # Add all Client contacts to Clients group
    for client in portal.clients.values():
        for contact in client.getContacts():
            user = portal.portal_membership.getMemberById(contact.getUsername())
            if user is not None:
                portal.portal_groups.addPrincipalToGroup(user.getUserName(),
                                                         "Clients")

    # Add AddAttachment permission to Clients
    mp = portal.manage_permission
    mp(AddAttachment, ['Manager', 'LabManager', 'Owner' 'Analyst', 'LabClerk', 'Client', 'Sampler'], 0)

    # Add Analysis Services View permission to Clients
    mp = portal.bika_setup.bika_analysisservices.manage_permission
    mp('Access contents information', ['Authenticated', 'Analyst', 'Client'], 1)
    mp(permissions.View, ['Authenticated', 'Analyst', 'Client'], 1)
    portal.bika_setup.bika_analysisservices.reindexObject()
    for obj in portal.bika_setup.bika_analysisservices.objectValues():
        mp = obj.manage_permission
        mp(permissions.View, ['Manager', 'LabManager', 'Analyst', 'Client'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'Member', 'LabClerk', 'Analyst', 'Client', 'Sampler', 'Preserver', 'Owner'], 0)
        obj.reindexObject()

    # Grant AttachmentType view access to Clients
    mp = portal.bika_setup.bika_attachmenttypes.manage_permission
    mp('Access contents information', ['Authenticated', 'Analyst', 'Client'], 1)
    mp(permissions.View, ['Authenticated', 'Analyst', 'Client'], 1)
    portal.bika_setup.bika_attachmenttypes.reindexObject()


    wf = getToolByName(portal, 'portal_workflow')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow-csv')
    wf.updateRoleMappings()

    return True
