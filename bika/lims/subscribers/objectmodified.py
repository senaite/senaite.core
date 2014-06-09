from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions
from bika.lims.permissions import AddSupplyOrder

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
        mp = obj.manage_permission
        mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler', 'Preserver', 'Owner'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk',  'Analyst', 'Sampler', 'Preserver', 'Owner'], 0)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'Owner'], 0)
        mp(AddSupplyOrder, ['Manager', 'LabManager', 'Owner'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'Member', 'LabClerk', 'Analyst', 'Sampler', 'Preserver', 'Owner'], 0)

    elif obj.portal_type == 'Contact':
        mp = obj.manage_permission
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Owner', 'Analyst', 'Sampler', 'Preserver'], 0)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'Owner'], 0)
