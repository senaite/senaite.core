from types import ListType, TupleType
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import *
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.utils import shasattr
from Products.Archetypes.Registry import registerField
from Products.bika.browser.widgets import AnalysesWidget
from decimal import Decimal

class AnalysesField(ObjectField):
    """A field that stores Analyses instances

    get() returns the list of Analyses contained inside the AnalysesRequest 
    set() converts a sequence of dictionaries to Analysis instances
    created inside the AnalysisRequest.
    """

    _properties = Field._properties.copy()
    _properties.update({
        'type' : 'analyses',
        'default' : None,
        'widget' : AnalysesWidget,
        })

    security = ClassSecurityInfo()

    security.declarePrivate('get')
    def get(self, instance, **kwargs):
        """get() returns the list of contained analyses
        """
        return instance.objectValues('Analysis')

    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        """ value must be a sequence of uid:price
        """
        if not value:
            return

        assert type(value) in (ListType, TupleType)

        # one can only edit Analyses if the AR is 'sample_received'
        # created state is for sample in the interlab skin    
        wf_tool = instance.portal_workflow
        ar_state = wf_tool.getInfoFor(instance, 'review_state', '')
        assert ar_state in ('created', 'sample_due', 'sample_received', 'assigned')

        # add new analyses
        rc = getToolByName(instance, REFERENCE_CATALOG)
        keep_ids = []
        dependancies = {}
        services = {}
        prices = {}
        parents = {}
        children = {}
        calc_codes = {}
        all_dependant_calcs = []
        for item in value:
            uid = item.split(':')[0]
            keep_ids.append(uid)
            price = item.split(':')[1]
            service = rc.lookupObject(uid)
            services[uid] = service
            prices[uid] = price
            calc_type = service.getCalculationType()
            if calc_type:
                calc_code = calc_type.getCalcTypeCode()
            else:
                calc_code = None
            calc_codes[uid] = calc_code
            if calc_code == 'dep':
                analysis_key = service.getAnalysisKey()
                dependancies[analysis_key] = []
                for s in service.getCalcDependancy():
                    dependancies[analysis_key].append(s.getAnalysisKey())
                    all_dependant_calcs.append(s.getAnalysisKey())

        analyses = services.keys()
        for uid in analyses:
            service = services[uid]
            price = prices[uid]
            try:
                float_price = float(price)
            except ValueError:
                price = Decimal('0', 2)
            calc_code = calc_codes[uid]
            if not shasattr(instance, service.id):
                instance.invokeFactory(
                    id = service.id, type_name = 'Analysis')
            analysis = instance._getOb(service.id)
            ar_report_dm = analysis.aq_parent.getReportDryMatter()
            vat = service.getVAT()
            vat = vat and vat or Decimal('0', 2)
            totalprice = price + (price * vat) / 100

            # Using getRaw method on field rather than generated
            # accessor to prevent object lookup
            if analysis.Schema()['Service'].getRaw(analysis) is None:
                analysis.edit(
                    Service = service,
                    CalcType = calc_code,
                    AnalysisKey = service.getAnalysisKey(),
                    Price = price,
                    VAT = vat,
                    TotalPrice = totalprice,
                    Unit = service.getUnit(),
                )
            else:
                # the price or unit of an existing analysis may have changed
                if (analysis.getPrice() != price) or \
                   (analysis.getUnit() != service.getUnit()) or \
                   (analysis.getCalcType() != calc_code):
                    analysis.edit(
                        CalcType = calc_code,
                        AnalysisKey = service.getAnalysisKey(),
                        Price = price,
                        VAT = service.getVAT(),
                        TotalPrice = totalprice,
                        Unit = service.getUnit(),
                    )
            if analysis.getCalcType() == 'dep':
                parents[service.getAnalysisKey()] = analysis
            if service.getAnalysisKey() in all_dependant_calcs:
                children[service.getAnalysisKey()] = analysis.UID()
            if service.getAnalysisKey() in all_dependant_calcs:
                analysis._affects_other_analysis = True
            else:
                analysis._affects_other_analysis = False
            if ar_report_dm:
                if service.getReportDryMatter():
                    analysis.setReportDryMatter(True)
                else:
                    analysis.setReportDryMatter(False)


            review_state = wf_tool.getInfoFor(analysis, 'review_state', '')
            if ar_state in ('sample_received', 'assigned') and \
               review_state == 'sample_due':
                wf_tool.doActionFor(analysis, 'receive')

        # set up the dependancies

        if all_dependant_calcs:
            instance._has_dependant_calcs = True
        else:
            instance._has_dependant_calcs = False

        dep_calcs = dependancies.keys()
        for dep in dep_calcs:
            parent = parents[dep]
            dependant_uids = []
            for item in dependancies[dep]:
                dependant_uids.append(children[item])
            parent.setDependantAnalysis(dependant_uids)


        # delete analyses
        delete_ids = []
        for analysis in instance.objectValues('Analysis'):
            service_uid = analysis.Schema()['Service'].getRaw(analysis)
            if service_uid not in keep_ids:
                delete_ids.append(analysis.getId())
        instance.manage_delObjects(ids = delete_ids)


    security.declarePublic('Vocabulary')
    def Vocabulary(self, content_instance = None):
        """ Create a vocabulary from analysis services
        """
        vocab = []
        for service in self.Services():
            vocab.append((service.UID(), service.Title()))
        return vocab

    security.declarePublic('Vocabulary')
    def Services(self):
        """ Return analysis services
        """
        if not shasattr(self, '_v_services'):
            self._v_services = [service.getObject() \
                for service in self.portal_catalog(
                portal_type = 'AnalysisService')]
        return self._v_services


registerField(AnalysesField,
              title = 'Analyses',
              description = ('Used for Analysis instances')
              )

