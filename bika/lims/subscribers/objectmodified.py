from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions
from bika.lims.permissions import AddClient, EditClient


def ObjectModifiedEventHandler(obj, event):
    """ Various types need automation on edit.
    """
    if not hasattr(obj, 'portal_type'):
        return

    if obj.portal_type == 'Calculation':
        pr = getToolByName(obj, 'portal_repository')
        uc = getToolByName(obj, 'uid_catalog')
        obj = uc(UID=obj.UID())[0].getObject()
        backrefs = obj.getBackReferences('AnalysisServiceCalculation')
        for i, service in enumerate(backrefs):
            service = uc(UID=service.UID())[0].getObject()
            pr.save(obj=service, comment="Calculation updated to version %s" %
                (obj.version_id + 1,))
            service.reference_versions[obj.UID()] = obj.version_id + 1

    elif obj.portal_type == 'Client':
        # When modifying these values, keep in sync with setuphandlers.py
        mp = obj.manage_permission
        mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'Member', 'LabClerk', 'Analyst', 'Sampler', 'Preserver'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Member', 'Analyst', 'Sampler', 'Preserver'], 0)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'LabClerk', 'Owner'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'Member', 'LabClerk', 'Analyst', 'Sampler', 'Preserver', 'Owner'], 0)

    elif obj.portal_type == 'BikaSetup':
        allow = obj.Schema().getField('AllowClerksToEditClients').get(obj)
        portal = getToolByName(obj, 'portal_url').getPortalObject()
        mp = portal.manage_permission
        if allow:
            mp(AddClient, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)
            mp(EditClient, ['Manager', 'Owner', 'LabManger', 'LabClerk'], 1)
        else:
            mp(AddClient, ['Manager', 'Owner', 'LabManager'], 1)
            mp(EditClient, ['Manager', 'Owner', 'LabManger'], 1)
