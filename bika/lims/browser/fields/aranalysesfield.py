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
    set() converts a sequence of UIDS to Analysis instances in the AR
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
            other kwargs are passed to bika_analysis_catalog
        """
        full_objects = False
        if 'full_objects' in kwargs:
            full_objects = kwargs['full_objects']
            del kwargs['full_objects']
        contentFilter = kwargs
        contentFilter['portal_type'] = "Analysis"
        contentFilter['path'] = {'query':"/".join(instance.getPhysicalPath()),
                                 'level':0}
        bac = getToolByName(instance, 'bika_analysis_catalog')
        analyses = bac(contentFilter)
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

        workflow = instance.portal_workflow

        # one can only edit Analyses up to a certain state.
        ar_state = workflow.getInfoFor(instance, 'review_state', '')
        assert ar_state in ('sample_registered', 'sampled',
                            'to_be_sampled', 'to_be_preserved',
                            'sample_due', 'sample_received',
                            'attachment_due', 'to_be_verified')

        bsc = getToolByName(instance, 'bika_setup_catalog')
        services = bsc(UID = service_uids)

        new_analyses = []

        for service in services:
            service_uid = service.UID
            service = service.getObject()
            keyword = service.getKeyword()
            price = prices[service_uid]
            vat = Decimal(service.getVAT())

            # analysis->InterimFields
            calc = service.getCalculation()
            interim_fields = calc and list(calc.getInterimFields()) or []
            # override defaults from service->InterimFields
            service_interims = service.getInterimFields()
            sif = dict([[x['keyword'], x['value']]
                        for x in service_interims])
            for i, i_f in enumerate(interim_fields):
                if i_f['keyword'] in sif:
                    interim_fields[i]['value'] = sif[i_f['keyword']]
                    service_interims = [x for x in service_interims
                                        if x['keyword'] != i_f['keyword']]
            # Add remaining service interims to the analysis
            for v in service_interims:
                interim_fields.append(v)

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
                SamplingWorkflowEnabled = instance.bika_setup.getSamplingWorkflowEnabled()
                if SamplingWorkflowEnabled:
                    workflow.doActionFor(analysis, 'sampling_workflow')
                else:
                    workflow.doActionFor(analysis, 'no_sampling_workflow')
                new_analyses.append(analysis)
                # Note: subscriber might retract and/or unassign the AR

        # delete analyses
        delete_ids = []
        for analysis in instance.objectValues('Analysis'):
            service_uid = analysis.Schema()['Service'].getRaw(analysis)
            if service_uid not in service_uids:
                # If it is verified or published, don't delete it.
                if workflow.getInfoFor(analysis, 'review_state') in ('verified', 'published'):
                    continue # log it
                # If it is assigned to a worksheet, unassign it before deletion.
                elif workflow.getInfoFor(analysis, 'worksheetanalysis_review_state') == 'assigned':
                    ws = analysis.getBackReferences("WorksheetAnalysis")[0]
                    ws.removeAnalysis(analysis)
                # Unset the partition reference
                analysis.edit(SamplePartition = None)
                delete_ids.append(analysis.getId())

        if delete_ids:
            # Note: subscriber might promote the AR
            instance.manage_delObjects(ids = delete_ids)
        return new_analyses

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
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        if not shasattr(self, '_v_services'):
            self._v_services = [service.getObject() \
                for service in bsc(portal_type = 'AnalysisService')]
        return self._v_services

registerField(ARAnalysesField,
              title = 'Analyses',
              description = ('Used for Analysis instances')
              )
