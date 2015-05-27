from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims.permissions import *
from Products.Archetypes import PloneMessageFactory as _p
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName

import logging


class Empty:
    pass


def upgrade(tool):
    """
    issue #623, #583, ...
    """
    # Hack prevent out-of-date upgrading
    # Related: PR #1484
    # https://github.com/bikalabs/Bika-LIMS/pull/1484
    from bika.lims.upgrade import skip_pre315
    if skip_pre315(aq_parent(aq_inner(tool))):
        return True

    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    typestool = getToolByName(portal, 'portal_types')

    # update affected tools
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'factorytool')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'jsregistry')
    setup.runImportStepFromProfile('profile-bika.lims:default',
                                   'propertiestool')
    setup.runImportStepFromProfile('profile-bika.lims:default',
                                   'plone.app.registry')

    # Changes to the catalogs
    # create lexicon
    wordSplitter = Empty()
    wordSplitter.group = 'Word Splitter'
    wordSplitter.name = 'Unicode Whitespace splitter'
    caseNormalizer = Empty()
    caseNormalizer.group = 'Case Normalizer'
    caseNormalizer.name = 'Unicode Case Normalizer'
    stopWords = Empty()
    stopWords.group = 'Stop Words'
    stopWords.name = 'Remove listed and single char words'
    zc_extras = Empty()
    zc_extras.index_type = 'Okapi BM25 Rank'
    zc_extras.lexicon_id = 'Lexicon'
    # then add indexes
    bc = getToolByName(portal, 'bika_catalog')
    bc.addIndex('getContactTitle', 'FieldIndex', zc_extras)
    bc.addIndex('getClientTitle', 'FieldIndex', zc_extras)
    bc.addIndex('getProfileTitle', 'FieldIndex', zc_extras)
    bc.addIndex('getAnalysisCategory', 'KeywordIndex')
    bc.addIndex('getAnalysisService', 'KeywordIndex')
    bc.addIndex('getAnalysts', 'KeywordIndex')

    bc.clearFindAndRebuild()

    # add new types not to list in nav
    # AnalysisRequestQuery and QueryFolder (listed in portal_tabs already)
    portal_properties = getToolByName(portal, 'portal_properties')
    ntp = getattr(portal_properties, 'navtree_properties')
    types = list(ntp.getProperty('metaTypesNotToList'))
    types.append("AnalysisRequestQuery")
    types.append("QueryFolder")
    ntp.manage_changeProperties(MetaTypesNotToQuery=types)

    # Add /queries folder
    typestool.constructContent(type_name="QueryFolder",
                               container=portal,
                               id='queries',
                               title='Queries')
    obj = portal['queries']
    obj.unmarkCreationFlag()
    obj.reindexObject()

    # /queries folder permissions
    mp = portal.queries.manage_permission
    mp(permissions.ListFolderContents, ['Manager', 'LabManager',
                                        'LabClerk', 'Analyst'], 0)
    mp(permissions.AddPortalContent, ['Manager', 'LabManager',
                                      'LabClerk', 'Analyst'], 0)
    mp(permissions.View, ['Manager', 'LabManager',
                          'LabClerk', 'Analyst'], 0)
    mp('Access contents information', ['Manager', 'LabManager',
                                       'LabClerk', 'Analyst'], 0)
    mp(permissions.DeleteObjects, ['Manager'], 0)
    portal.queries.reindexObject()

    # idserver prefix for AnalysisRequestQuery
    prefixes = portal.bika_setup.getPrefixes()
    if [x for x in prefixes if x['portal_type'] == 'AnalysisRequestQuery']:
        prefixes.append({'portal_type': 'AnalysisRequestQuery',
                         'prefix': 'query-', 'padding': '4'})
        portal.bika_setup.setPrefixes(prefixes)

    return True
