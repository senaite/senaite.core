from Products.CMFCore.utils import getToolByName


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
