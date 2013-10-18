from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims.permissions import *
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest

class Empty:
    pass


def upgrade(tool):
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

    # Add the QueryFolder at /queries
    try:
        typestool.constructContent(type_name="QueryFolder",
                               container=portal,
                               id='queries',
                               title='Queries')
        obj = portal['queries']
        obj.unmarkCreationFlag()
        obj.reindexObject()
    except BadRequest:
        # folder already exists
        pass

    # /queries folder permissions
    mp = portal.queries.manage_permission
    mp(permissions.ListFolderContents, [
       'Manager', 'LabManager', 'Member', 'LabClerk', ], 0)
    mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Member'], 0)
    mp('Access contents information', [
       'Manager', 'LabManager', 'Member', 'LabClerk', 'Owner'], 0)
    mp(permissions.AddPortalContent, [
       'Manager', 'LabManager', 'LabClerk', 'Owner', 'Member'], 0)
    mp('ATContentTypes: Add Image', [
       'Manager', 'Labmanager', 'LabClerk', 'Member', ], 0)
    mp('ATContentTypes: Add File', [
       'Manager', 'Labmanager', 'LabClerk', 'Member', ], 0)
    mp(AddQuery, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 0)
    portal.queries.reindexObject()

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
    if 'getContactTitle' not in bc.indexes():
        bc.addIndex('getContactTitle', 'FieldIndex')
    if 'getClientTitle' not in bc.indexes():
        bc.addIndex('getClientTitle', 'FieldIndex')
    if 'getProfileTitle' not in bc.indexes():
        bc.addIndex('getProfileTitle', 'FieldIndex')
    if 'getAnalysisCategory' not in bc.indexes():
        bc.addIndex('getAnalysisCategory', 'KeywordIndex')
    if 'getAnalysisService' not in bc.indexes():
        bc.addIndex('getAnalysisService', 'KeywordIndex')
    if 'getAnalysts' not in bc.indexes():
        bc.addIndex('getAnalysts', 'KeywordIndex')
    bc.addColumn('created')
    bc.addColumn('Creator')
    bc.addColumn('getAnalysts')
    bc.addColumn('getSampleID')
    bc.addColumn('getRequestID')
    bc.addColumn('getContactTitle')
    bc.addColumn('getClientTitle')
    bc.addColumn('getProfileTitle')
    bc.addColumn('getAnalysisCategory')
    bc.addColumn('getAnalysisService')
    bc.addColumn('getSamplePointTitle')
    bc.addColumn('getSampleTypeTitle')
    bc.addColumn('getDatePublished')
    bc.addColumn('getDateReceived')
    bc.addColumn('getDateSampled')
    bc.clearFindAndRebuild()

    # AnalysisRequestQuery and QueryFolder (listed in portal_tabs already)
    portal_properties = getToolByName(portal, 'portal_properties')
    ntp = getattr(portal_properties, 'navtree_properties')
    types = list(ntp.getProperty('metaTypesNotToList'))
    types.append("AnalysisRequestQuery")
    types.append("QueryFolder")
    ntp.manage_changeProperties(MetaTypesNotToQuery=types)

    return True
