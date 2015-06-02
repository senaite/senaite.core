from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName


def upgrade(tool):
    """ Convert analysis specs to AR specs in AR.ResultsRange.
    """
    # Hack prevent out-of-date upgrading
    # Related: PR #1484
    # https://github.com/bikalabs/Bika-LIMS/pull/1484
    from bika.lims.upgrade import skip_pre315
    if skip_pre315(aq_parent(aq_inner(tool))):
        return True

    portal = aq_parent(aq_inner(tool))
    bc = getToolByName(portal, 'bika_catalog', None)
    bsc = getToolByName(portal, 'bika_setup_catalog', None)

    # for each AR
    proxies = bc(portal_type="AnalysisRequest")
    for proxy in proxies:
        ar = proxy.getObject()

        # get the AR.Specification
        arspec = ar.getSpecification()
        rr = arspec.getResultsRange() if arspec else []

        # Get analysis specifications
        specs = []
        for analysis in ar.getAnalyses(full_objects=True):
            spec = getattr(analysis, 'specification', False)
            if spec:
                spec['keyword'] = analysis.getService().getKeyword()
                spec['uid'] = analysis.UID()
                specs.append(spec)

        # mix in the analysis spec values
        for s in specs:
            s_in_rr = False
            for i, r in enumerate(rr):
                if s['keyword'] == r['keyword']:
                    rr[i].update(s)
                    s_in_rr = True
            if not s_in_rr:
                rr.append(s)

        # set AR.ResultsRange
        ar.setResultsRange(rr)

    return True
