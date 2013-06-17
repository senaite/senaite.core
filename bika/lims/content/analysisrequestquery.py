"""Customised Collections for querying Analysis Requests
"""
from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import BCQueryWidget
from bika.lims.browser.fields import QueryField
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IAnalysisRequestQuery
from plone.app.collection import PloneMessageFactory as _p
from plone.app.collection.collection import Collection
from plone.app.collection.collection import CollectionSchema
from Products.Archetypes.atapi import DisplayList
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from Products.CMFCore.permissions import ModifyPortalContent, View
from zope.interface import implements
from Products.Archetypes.atapi import (BooleanField,
                                       BooleanWidget,
                                       IntegerField,
                                       LinesField,
                                       IntegerWidget,
                                       InAndOutWidget,
                                       StringField,
                                       StringWidget)

QuerySchema = CollectionSchema.copy() + atapi.Schema((
    QueryField(
        name='query',
        registry_prefix='bika.lims.analysisrequestquery',
        catalog_name='bika_catalog',
        widget=BCQueryWidget(
            label=_(u"Search terms"),
            description=_(u"Define the search terms for the items you want to "
                          u"list by choosing what to match on. "
                          u"The list of results will be dynamically updated."),
            registry_prefix='bika.lims.analysisrequestquery',
            catalog_name='bika_catalog',
        ),
        validators=('javascriptDisabled', )
    ),

    StringField(
        name='sort_on',
        required=False,
        mode='rw',
        default='sortable_title',
        widget=StringWidget(
            label=_(u'Sort the collection on this index'),
            description='',
            visible=False,
        ),
    ),

    BooleanField(
        name='sort_reversed',
        required=False,
        mode='rw',
        default=False,
        widget=BooleanWidget(
            label=_(u'Sort the results in reversed order'),
            description='',
            visible=False,
        ),
    ),

    IntegerField(
        name='limit',
        required=False,
        mode='rw',
        default=1000,
        widget=IntegerWidget(
            label=_(u'Limit Search Results'),
            description=_(u"Specify the maximum number of items to show.")
        ),
    ),

    LinesField('customViewFields',
               required=False,
               mode='rw',
               default=('Title', 'Creator', 'Type', 'ModificationDate'),
               vocabulary='listMetaDataFields',
               enforceVocabulary=True,
               write_permission=ModifyPortalContent,
               widget=InAndOutWidget(
                   label=_(u'Table Columns'),
                   description=_(
                       u"Select which fields to display when "
                       u"'Tabular view' is selected in the display menu.")
               ),
               ),
))


schemata.finalizeATCTSchema(
    QuerySchema,
    folderish=False,
    moveDiscussion=False)


class AnalysisRequestQuery(Collection):

    """ Query form and results for Analysis Requests
    """

    implements(IAnalysisRequestQuery)
    meta_type = "AnalysisRequestQuery"
    schema = QuerySchema
    security = ClassSecurityInfo()

    security.declareProtected(View, 'listMetaDataFields')

    def listMetaDataFields(self, exclude=True):
        """Return a list of metadata fields from catalog
        """

        return DisplayList((
            ('getRequestID', _('Request ID')),
            ('getClientTitle', _('Client Name')),
            ('getContactTitle', _('Contact Name')),
            ('getProfileTitle', _('Analysis Profile')),
            ('getClientOrderNumber', _('Client Order')),
            ('getInvoiced', _('Invoiced')),
            ('review_state', _p('Review state')),
            ('getAnalysisCategory', _p('Analysis Category')),
            ('getAnalysisService', _p('Analysis Service')),
            ('getAnalyst', _('Analyst')),
            ('getClientReference', _('Client Reference')),
            ('getClientSampleID', _('Client Sample ID')),
            ('getSampleTypeTitle', _('Sample Type')),
            ('getSamplePointTitle', _('Sample Point')),
            ('getDateSampled', _('Date Sampled')),
            ('created', _('Date Created')),
            ('getDateReceived', _('Date Received')),
            ('getDatePublished', _('Date Published')),
            ('Creator', _p('Creator')),
        ))

    security.declareProtected(View, 'results')

    def results(self, batch=True, b_start=0, b_size=None, sort_on=None,
                brains=False, catalog_name='bika_catalog'):
        """Get results"""

        if sort_on is None:
            sort_on = self.getSort_on()
        if b_size is None:
            b_size = self.getLimit()

        return self.getQuery(batch=batch,
                             b_start=b_start,
                             b_size=b_size,
                             sort_on=sort_on,
                             brains=brains,
                             catalog_name='bika_catalog')


atapi.registerType(AnalysisRequestQuery, PROJECTNAME)
