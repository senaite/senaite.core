from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.config import REFERENCE_CATALOG

def upgrade(tool):
    """ Migrate all WorksheetInstrument relations from Reference Analyses
        and DuplicateAnalyses to AnalysisInstrument. Assignment of
        Instruments to a Worksheet is no longer used. The assignment
        is performed to each Analysis directly
    """

    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    portal = aq_parent(aq_inner(tool))
    bac = getToolByName(portal, 'bika_analysis_catalog')
    rc=getToolByName(portal, REFERENCE_CATALOG)
    proxies = bac(portal_type=["DuplicateAnalysis", "ReferenceAnalysis"])
    for proxy in proxies:
        an = proxy.getObject()
        if an.getInstrument():
            continue
        instrument = None
        rels = an.at_references.objectValues()
        for rel in rels:
            if rel.relationship == 'WorksheetInstrument':
                oldinstr = rc.lookupObject(rel.targetUID)
                break
        if instrument:
            an.Schema().getField('Instrument').set(an, instrument.UID())
            instrument.addAnalysis(an)

    # Set indexes
    portal = aq_parent(aq_inner(tool))
    bac = getToolByName(portal, 'bika_analysis_catalog')
    addIndexAndColumn(bac, 'getResultCaptureDate', 'DateIndex')
    bac.clearFindAndRebuild()


def addIndexAndColumn(catalog, index, indextype):
    try:
        catalog.addIndex(index, indextype)
    except:
        pass
    try:
        catalog.addColumn(index)
    except:
        pass

    return True
