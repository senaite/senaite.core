from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions
from bika.lims.permissions import ManageSupplyOrders

def ObjectModifiedEventHandler(obj, event):
    """ Various types need automation on edit.
    """
    if not hasattr(obj, 'portal_type'):
        return

    if obj.portal_type == 'Calculation':
        pr = getToolByName(obj, 'portal_repository')
        uc = getToolByName(obj, 'uid_catalog')
        obj = uc(UID=obj.UID())[0].getObject()
        version_id = obj.version_id if hasattr(obj, 'version_id') else 0

        backrefs = obj.getBackReferences('AnalysisServiceCalculation')
        for i, target in enumerate(backrefs):
            target = uc(UID=target.UID())[0].getObject()
            pr.save(obj=target, comment="Calculation updated to version %s" %
                (version_id + 1,))
            reference_versions = getattr(target, 'reference_versions', {})
            reference_versions[obj.UID()] = version_id + 1
            target.reference_versions = reference_versions

        backrefs = obj.getBackReferences('MethodCalculation')
        for i, target in enumerate(backrefs):
            target = uc(UID=target.UID())[0].getObject()
            pr.save(obj=target, comment="Calculation updated to version %s" %
                (version_id + 1,))
            reference_versions = getattr(target, 'reference_versions', {})
            reference_versions[obj.UID()] = version_id + 1
            target.reference_versions = reference_versions

    elif obj.portal_type == 'Client':
        mp = obj.manage_permission
        mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler', 'Preserver', 'Owner'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk',  'Analyst', 'Sampler', 'Preserver', 'Owner'], 0)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'Owner'], 0)
        mp(ManageSupplyOrders, ['Manager', 'LabManager', 'Owner', 'LabClerk'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'Member', 'LabClerk', 'Analyst', 'Sampler', 'Preserver', 'Owner'], 0)

    elif obj.portal_type == 'Contact':
        mp = obj.manage_permission
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Owner', 'Analyst', 'Sampler', 'Preserver'], 0)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'Owner'], 0)
    elif obj.portal_type == 'AnalysisCategory':
        for analysis in obj.getBackReferences('AnalysisServiceAnalysisCategory'):
            analysis.reindexObject(idxs=["getCategoryTitle", "getCategoryUID", ])
