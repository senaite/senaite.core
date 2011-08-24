from types import ListType, TupleType, DictType
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import *
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.utils import shasattr
from Products.Archetypes.Registry import registerField
from decimal import Decimal
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('bika')

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

    security  = ClassSecurityInfo()

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
    def set(self, instance, service_uids, prices=None, **kwargs):
        """ service_uids are the services selected on the AR Add/Edit form.
            prices is a service_uid keyed dictionary containing the prices entered on the form.
        """
        if not service_uids:
            return

        assert type(service_uids) in (ListType, TupleType)
        assert prices

        workflow = instance.portal_workflow
        # one can only edit Analyses up to a certain state.
        ar_state = workflow.getInfoFor(instance, 'review_state', '')
        assert ar_state in ('sample_due', 'sample_received', 'assigned')

        services = {}
        rc = getToolByName(instance, REFERENCE_CATALOG)
        for service_uid in service_uids:
            service = rc.lookupObject(service_uid)
            services[service_uid] = service
            price = prices[service_uid]
            vat = Decimal(service.getVAT())

            #create the analysis if it doesn't exist
            if not hasattr(instance, service.getKeyword()):
                instance.invokeFactory(id = service.getKeyword(), type_name = 'Analysis')
            analysis = instance._getOb(service.getKeyword())

            calc = service.getCalculation()
            interim_fields = calc and calc.getInterimFields() or []

            # Using getRaw method on field rather than generated
            # accessor to prevent object lookup
            if analysis.Schema()['Service'].getRaw(analysis) is None:
                # if analysis['Service'] is None
                analysis.edit(
                    Service = service,
                    InterimFields = interim_fields,
                    Keyword = service.getKeyword(),
                    Price = str(price),
                    Unit = service.getUnit(),
                    MaxTimeAllowed = service.getMaxTimeAllowed(),
                )
            else:
                # the price or unit of an existing analysis may have changed
                if (analysis.getPrice() != price) or \
                   (analysis.getUnit() != service.getUnit()):
                    analysis.edit(
                        Keyword = service.getKeyword(),
                        Price = str(price),
                        Unit = service.getUnit(),
                    )

            review_state = workflow.getInfoFor(analysis, 'review_state', '')
            if ar_state in ('sample_received', 'assigned') and \
                review_state == 'sample_due':
                workflow.doActionFor(analysis, 'receive')

        # delete analyses
        delete_ids = []
        for analysis in instance.objectValues('Analysis'):
            service_uid = analysis.Schema()['Service'].getRaw(analysis)
            if service_uid not in service_uids:
                delete_ids.append(analysis.getId())
        instance.manage_delObjects(ids=delete_ids)

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

