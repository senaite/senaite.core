from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerField
from Products.Archetypes.event import ObjectInitializedEvent
from Products.Archetypes.public import *
from Products.Archetypes.utils import shasattr
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from decimal import Decimal
from types import ListType, TupleType, DictType
import zope.event

class ARAnalysesField(ObjectField):

    """A field that stores Analyses instances

    get() returns the list of Analyses contained inside the AnalysesRequest
    set() converts a sequence of dictionaries to Analysis instances
    created inside the AnalysisRequest.
    """

    _properties = Field._properties.copy()
    _properties.update({
        'type' : 'analyses',
        'default' : None,
        })

    security = ClassSecurityInfo()

    security.declarePrivate('get')
    def get(self, instance, **kwargs):
        """ get() returns the list of contained analyses
            By default, return a list of catalog brains.
            If you want objects, pass full_objects = True
            other kwargs are passed to portal_catalog
        """
        full_objects = False
        if 'full_objects' in kwargs:
            full_objects = kwargs['full_objects']
            del kwargs['full_objects']
        contentFilter = kwargs
        contentFilter['portal_type'] = "Analysis"
        contentFilter['path'] = {'query':"/".join(instance.getPhysicalPath()),
                                 'depth':1}
        pc = getToolByName(instance, 'portal_catalog')
        analyses = pc(contentFilter)
        if full_objects:
            analyses = [a.getObject() for a in analyses]
        return analyses

    security.declarePrivate('set')
    def set(self, instance, service_uids, prices = None, **kwargs):
        """ service_uids are the services selected on the AR Add/Edit form.
            prices is a service_uid keyed dictionary containing the prices entered on the form.
        """
        if not service_uids:
            return

        assert type(service_uids) in (list, tuple)
   #     assert type(prices) == dict

        workflow = instance.portal_workflow
        # one can only edit Analyses up to a certain state.
        ar_state = workflow.getInfoFor(instance, 'review_state', '')
        assert ar_state in ('sample_due', 'sample_received', 'attachment_due', 'to_be_verified')

        pc = getToolByName(instance, 'portal_catalog')
        services = pc(UID = service_uids)

        for service in services:
            service_uid = service.UID
            service = service.getObject()
            keyword = service.getKeyword()
            price = prices[service_uid]
            vat = Decimal(service.getVAT())

            calc = service.getCalculation()
            interim_fields = calc and calc.getInterimFields() or []

            #create the analysis if it doesn't exist
            if hasattr(instance, keyword):
                analysis = instance._getOb(keyword)
            else:
                instance.invokeFactory(id = keyword,
                                       type_name = 'Analysis')
                analysis = instance._getOb(keyword)
                analysis.edit(Service = service,
                              InterimFields = interim_fields,
                              MaxTimeAllowed = service.getMaxTimeAllowed())
                analysis.unmarkCreationFlag()
                zope.event.notify(ObjectInitializedEvent(analysis))
                # Note: subscriber might retract and/or unassign the AR

        # delete analyses
        delete_ids = []
        for analysis in instance.objectValues('Analysis'):
            service_uid = analysis.Schema()['Service'].getRaw(analysis)
            if service_uid not in service_uids:
                # If it is verified or published, don't delete it.
                if workflow.getInfoFor(analysis, 'review_state') in ('verified', 'published'):
                    continue
                # If it is assigned to a worksheet, unassign it before deletion.
                elif workflow.getInfoFor(analysis, 'worksheetanalysis_review_state') == 'assigned':
                    ws = analysis.getBackReferences("WorksheetAnalysis")[0]
                    ws.removeAnalysis(analysis)
                    # overwrite saved context UID for event subscriber
                    instance.REQUEST['context_uid'] = ws.UID()
                    workflow.doActionFor(analysis, 'unassign')
                    # Note: subscriber might unassign the AR and/or promote the worksheet
                delete_ids.append(analysis.getId())
        instance.manage_delObjects(ids = delete_ids)
        # Note: subscriber might promote the AR

    security.declarePublic('Vocabulary')
    def Vocabulary(self, content_instance = None):
        """ Create a vocabulary from analysis services
        """
        vocab = []
        for service in self.Services():
            vocab.append((service.UID(), service.Title()))
        return vocab

    security.declarePublic('Services')
    def Services(self):
        """ Return analysis services
        """
        if not shasattr(self, '_v_services'):
            self._v_services = [service.getObject() \
                for service in self.portal_catalog(
                portal_type = 'AnalysisService')]
        return self._v_services

registerField(ARAnalysesField,
              title = 'Analyses',
              description = ('Used for Analysis instances')
              )

