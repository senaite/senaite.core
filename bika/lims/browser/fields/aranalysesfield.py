from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.permissions import ViewRetractedAnalyses
from bika.lims.utils import t, dicts_to_dict
from bika.lims.utils.analysis import create_analysis
from decimal import Decimal
from Products.Archetypes.public import *
from Products.Archetypes.Registry import registerField
from Products.Archetypes.utils import shasattr
from Products.CMFCore.utils import getToolByName
from types import ListType, TupleType, DictType


class ARAnalysesField(ObjectField):

    """A field that stores Analyses instances

    get() returns the list of Analyses contained inside the AnalysesRequest
    set() converts a sequence of UIDS to Analysis instances in the AR
    """

    _properties = Field._properties.copy()
    _properties.update({
        'type': 'analyses',
        'default': None,
    })

    security = ClassSecurityInfo()

    security.declarePrivate('get')

    def get(self, instance, **kwargs):
        """ get() returns the list of contained analyses
            By default, return a list of catalog brains.

            If you want objects, pass full_objects = True

            If you want to override "ViewRetractedAnalyses",
            pass retracted=True

            other kwargs are passed to bika_analysis_catalog

        """

        full_objects = False
        if 'full_objects' in kwargs:
            full_objects = kwargs['full_objects']
            del kwargs['full_objects']

        if 'retracted' in kwargs:
            retracted = kwargs['retracted']
            del kwargs['retracted']
        else:
            mtool = getToolByName(instance, 'portal_membership')
            retracted = mtool.checkPermission(ViewRetractedAnalyses,
                                              instance)

        bac = getToolByName(instance, 'bika_analysis_catalog')
        contentFilter = dict([(k, v) for k, v in kwargs.items()
                              if k in bac.indexes()])
        contentFilter['portal_type'] = "Analysis"
        contentFilter['path'] = {'query': "/".join(instance.getPhysicalPath()),
                                 'level': 0}
        analyses = bac(contentFilter)
        if not retracted:
            analyses = [a for a in analyses if a.review_state != 'retracted']
        if full_objects:
            analyses = [a.getObject() for a in analyses]
        return analyses

    security.declarePrivate('set')

    def set(self, instance, service_uids, prices=None, specs=None, **kwargs):
        """Set the 'Analyses' field value, by creating and removing Analysis
        objects from the AR.

        service_uids is a list:
            The UIDs of all services which should exist in the AR.  If a service
            is not included here, the corrosponding Analysis will be removed.

        prices is a dictionary:
            key = AnalysisService UID
            value = price

        specs is a dictionary:
            key = AnalysisService UID
            value = dictionary: defined in ResultsRange field definition
        """
        if not service_uids:
            return

        assert type(service_uids) in (list, tuple)

        bsc = getToolByName(instance, 'bika_setup_catalog')
        workflow = getToolByName(instance, 'portal_workflow')

        # one can only edit Analyses up to a certain state.
        ar_state = workflow.getInfoFor(instance, 'review_state', '')
        assert ar_state in ('sample_registered', 'sampled',
                            'to_be_sampled', 'to_be_preserved',
                            'sample_due', 'sample_received',
                            'attachment_due', 'to_be_verified')

        # -  Modify existing AR specs with new form values for selected analyses.
        # -  new analysis requests are also using this function, so ResultsRange
        #    may be undefined.  in this case, specs= will contain the entire
        #    AR spec.
        rr = instance.getResultsRange()
        specs = specs if specs else []
        for s in specs:
            s_in_rr = False
            for i, r in enumerate(rr):
                if s['keyword'] == r['keyword']:
                    rr[i].update(s)
                    s_in_rr = True
            if not s_in_rr:
                rr.append(s)
        instance.setResultsRange(rr)

        new_analyses = []
        proxies = bsc(UID=service_uids)
        for proxy in proxies:
            service = proxy.getObject()
            service_uid = service.UID()
            keyword = service.getKeyword()
            price = prices[service_uid] if prices and service_uid in prices \
                else service.getPrice()
            vat = Decimal(service.getVAT())

            # analysis->InterimFields
            calc = service.getCalculation()
            interim_fields = calc and list(calc.getInterimFields()) or []

            # override defaults from service->InterimFields
            service_interims = service.getInterimFields()
            sif = dict([(x['keyword'], x.get('value', ''))
                        for x in service_interims])
            for i, i_f in enumerate(interim_fields):
                if i_f['keyword'] in sif:
                    interim_fields[i]['value'] = sif[i_f['keyword']]
                    service_interims = [x for x in service_interims
                                        if x['keyword'] != i_f['keyword']]
            # Add remaining service interims to the analysis
            for v in service_interims:
                interim_fields.append(v)

            # create the analysis if it doesn't exist
            if shasattr(instance, keyword):
                analysis = instance._getOb(keyword)
            else:
                analysis = create_analysis(
                    instance,
                    service,
                    keyword,
                    interim_fields
                )
                new_analyses.append(analysis)
            for i, r in enumerate(rr):
                if r['keyword'] == analysis.getService().getKeyword():
                    r['uid'] = analysis.UID()

            # XXX Price?
            # analysis.setPrice(price)

        # We add rr to the AR after we create all the analyses
        instance.setResultsRange(rr)

        # delete analyses
        delete_ids = []
        for analysis in instance.objectValues('Analysis'):
            service_uid = analysis.Schema()['Service'].getRaw(analysis)
            if service_uid not in service_uids:
                # If it is verified or published, don't delete it.
                if workflow.getInfoFor(analysis, 'review_state') in ('verified', 'published'):
                    continue  # log it
                # If it is assigned to a worksheet, unassign it before deletion.
                elif workflow.getInfoFor(analysis, 'worksheetanalysis_review_state') == 'assigned':
                    ws = analysis.getBackReferences("WorksheetAnalysis")[0]
                    ws.removeAnalysis(analysis)
                # Unset the partition reference
                analysis.edit(SamplePartition=None)
                delete_ids.append(analysis.getId())

        if delete_ids:
            # Note: subscriber might promote the AR
            instance.manage_delObjects(ids=delete_ids)
        return new_analyses

    security.declarePublic('Vocabulary')

    def Vocabulary(self, content_instance=None):
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
            self._v_services = [service.getObject()
                                for service in bsc(portal_type='AnalysisService')]
        return self._v_services

registerField(ARAnalysesField,
              title='Analyses',
              description=('Used for Analysis instances')
              )
