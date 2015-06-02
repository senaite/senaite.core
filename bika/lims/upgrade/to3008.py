from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.config import REFERENCE_CATALOG

def upgrade(tool):
    """Added bika.lims.analysisservice.edit.js
    """
    # Hack prevent out-of-date upgrading
    # Related: PR #1484
    # https://github.com/bikalabs/Bika-LIMS/pull/1484
    from bika.lims.upgrade import skip_pre315
    if skip_pre315(aq_parent(aq_inner(tool))):
        return True

    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    # update affected tools
    setup.runImportStepFromProfile('profile-bika.lims:default', 'jsregistry')

    # apply new method/calculation data to old Analysis Services
    portal = aq_parent(aq_inner(tool))
    pc = getToolByName(portal, 'portal_catalog')
    bsc = getToolByName(portal, 'bika_setup_catalog')
    rc=getToolByName(portal, REFERENCE_CATALOG)
    proxies = pc(portal_type="AnalysisService")
    for proxy in proxies:
        an = proxy.getObject()
        rels = an.at_references.objectValues()
        oldmethod = None
        oldinstrument = None
        oldcalc = None
        for rel in rels:
            if rel.relationship == 'AnalysisServiceCalculation':
                oldcalc=rc.lookupObject(rel.targetUID)
            elif rel.relationship == 'AnalysisServiceInstrument':
                oldinstrument=rc.lookupObject(rel.targetUID)
            elif rel.relationship == 'AnalysisServiceMethod':
                oldmethod=rc.lookupObject(rel.targetUID)
            if oldmethod and oldcalc and oldinstrument:
                break

        # Reset the method, instrument and calculations
        if oldmethod:
            an.Schema().getField('Methods').set(an, [oldmethod.UID(),])
            an.Schema().getField('_Method').set(an, oldmethod.UID())
        if oldinstrument:
            an.Schema().getField('Instruments').set(an, [oldinstrument.UID(),])
            an.Schema().getField('Instrument').set(an, oldinstrument.UID())
        if oldcalc:
            an.setUseDefaultCalculation(False);
            an.Schema().getField('DeferredCalculation').set(an, oldcalc.UID())

    return True
