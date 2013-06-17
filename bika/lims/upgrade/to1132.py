from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims.permissions import *
from Products.CMFCore.utils import getToolByName


def upgrade(tool):
    """ Populate ReferenceAnalysesGroupIDs for ReferenceAnalyses
        https://github.com/bikalabs/Bika-LIMS/issues/931
    """
    portal = aq_parent(aq_inner(tool))
    bc = getToolByName(portal, 'bika_catalog')
    wss = bc(portal_type='Worksheet')
    for ws in wss:
        ws = ws.getObject()
        wsangroups = {}
        codes = {}

        # Reference Analyses (not duplicates)
        refanalyses = [an for an in ws.getAnalyses() \
                       if an.portal_type == 'ReferenceAnalysis' \
                        or an.portal_type == 'DuplicateAnalysis']
        layout = ws.getLayout()
        for lay in layout:
            for an in refanalyses:
                if lay['analysis_uid'] == an.UID():
                    position = lay['position']
                    if  position not in wsangroups.keys():
                        wsangroups[position] = []
                    wsangroups[position].append(an)

        for position, wsgroup in wsangroups.iteritems():
            analysis = wsgroup[0]
            if analysis.portal_type == 'ReferenceAnalysis':
                refsampleid = wsgroup[0].aq_parent.id
            else:
                # Duplicate
                refsampleid = wsgroup[0].getSamplePartition().id
            codre = refsampleid
            codws = '%s_%s' % (refsampleid, ws.UID())
            codgr = '%s_%s_%s' % (refsampleid, ws.UID(), position)
            if codgr in codes.keys():
                postfix = codes[codgr]
            elif codws in codes.keys():
                postfix = codes[codws]
                codes[codgr] = postfix
                codes[codws] = postfix + 1
            elif codre in codes.keys():
                postfix = codes[codre]
                codes[codgr] = postfix
                codes[codws] = postfix + 1
                codes[codre] = postfix + 1
            else:
                postfix = 1
                codes[codre] = postfix + 1

            for an in wsgroup:
                if an.portal_type == 'DuplicateAnalysis':
                    postfix = str(postfix).zfill(int(2))
                    refgid = '%s-D%s' % (refsampleid, postfix)
                else:
                    postfix = str(postfix).zfill(int(3))
                    refgid = '%s-%s' % (refsampleid, postfix)
                an.setReferenceAnalysesGroupID(refgid)

    return True
