from bika.lims.adapters.referencewidgetvocabulary import DefaultReferenceWidgetVocabulary
from bika.lims.jsonapi import get_include_fields
from bika.lims.jsonapi import load_brain_metadata
from bika.lims.jsonapi import load_field_values
from bika.lims.utils import dicts_to_dict
from bika.lims.interfaces import IAnalysisRequest
from bika.lims.interfaces import IFieldIcons
from bika.lims.interfaces import IJSONReadExtender
from bika.lims.permissions import *
from bika.lims.workflow import get_workflow_actions
from bika.lims.vocabularies import CatalogVocabulary
from bika.lims.utils import to_utf8
from bika.lims.workflow import doActionFor
from DateTime import DateTime
from Products.Archetypes import PloneMessageFactory as PMF
from plone.app.layout.globals.interfaces import IViewView
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.component import adapts
from zope.component import getAdapters
from zope.component import queryUtility
from zope.interface import implements

import json

from .view import AnalysisRequestViewView    # view first.
from .add import AnalysisRequestAddView
from .invoice import InvoicePrintView
from .invoice import InvoiceView
from invoice import InvoiceCreate
from .log import AnalysisRequestLog
from .manage_analyses import AnalysisRequestAnalysesView
from .manage_results import AnalysisRequestManageResultsView
from .published_results import AnalysisRequestPublishedResults
from .results_not_requested import AnalysisRequestResultsNotRequestedView
from .workflow import AnalysisRequestWorkflowAction
from .analysisrequests import AnalysisRequestsView


class ResultOutOfRange(object):

    """Return alerts for any analyses inside the context ar
    """
    implements(IFieldIcons)
    adapts(IAnalysisRequest)

    def __init__(self, context):
        self.context = context

    def __call__(self, result=None, **kwargs):
        workflow = getToolByName(self.context, 'portal_workflow')
        items = self.context.getAnalyses()
        field_icons = {}
        for obj in items:
            obj = obj.getObject() if hasattr(obj, 'getObject') else obj
            uid = obj.UID()
            astate = workflow.getInfoFor(obj, 'review_state')
            if astate == 'retracted':
                continue
            adapters = getAdapters((obj, ), IFieldIcons)
            for name, adapter in adapters:
                alerts = adapter(obj)
                if alerts:
                    if uid in field_icons:
                        field_icons[uid].extend(alerts[uid])
                    else:
                        field_icons[uid] = alerts[uid]
        return field_icons


class ClientContactVocabularyFactory(CatalogVocabulary):

    def __call__(self):
        parent = self.context.aq_parent
        return super(ClientContactVocabularyFactory, self).__call__(
            portal_type='Contact',
            path={'query': "/".join(parent.getPhysicalPath()),
                  'level': 0}
        )


class ReferenceWidgetVocabulary(DefaultReferenceWidgetVocabulary):

    def __call__(self):
        base_query = json.loads(self.request['base_query'])
        # In client context, restrict samples to client samples only
        if 'portal_type' in base_query \
        and (base_query['portal_type'] == 'Sample'
             or base_query['portal_type'][0] == 'Sample'):
            base_query['getClientUID'] = self.context.aq_parent.UID()
            self.request['base_query'] = json.dumps(base_query)
        return DefaultReferenceWidgetVocabulary.__call__(self)


class JSONReadExtender(object):

    """- Adds the full details of all analyses to the AR.Analyses field
    """

    implements(IJSONReadExtender)
    adapts(IAnalysisRequest)

    def __init__(self, context):
        self.context = context

    def ar_analysis_values(self):
        ret = []
        analyses = self.context.getAnalyses(cancellation_state='active')
        for proxy in analyses:
            analysis = proxy.getObject()
            service = analysis.getService()
            if proxy.review_state == 'retracted':
                # these are scraped up when Retested analyses are found below.
                continue
            # things that are manually inserted into the analysis.
            # These things will be included even if they are not present in
            # include_fields in the request.
            method = analysis.getMethod()
            if not method:
                method = service.getMethod()
            service = analysis.getService()
            analysis_data = {
                "Uncertainty": service.getUncertainty(analysis.getResult()),
                "Method": method.Title() if method else '',
                "Unit": service.getUnit(),
            }
            # Place all schema fields ino the result.
            analysis_data.update(load_brain_metadata(proxy, []))
            # Place all schema fields ino the result.
            analysis_data.update(load_field_values(analysis, []))
            # call any adapters that care to modify the Analysis data.
            # adapters = getAdapters((analysis, ), IJSONReadExtender)
            # for name, adapter in adapters:
            #     adapter(request, analysis_data)
            if not self.include_fields or "transitions" in self.include_fields:
                analysis_data['transitions'] = get_workflow_actions(analysis)
            if analysis.getRetested():
                retracted = self.context.getAnalyses(review_state='retracted',
                                            title=analysis.Title(),
                                            full_objects=True)
                prevs = sorted(retracted, key=lambda item: item.created())
                prevs = [{'created': str(p.created()),
                          'Result': p.getResult(),
                          'InterimFields': p.getInterimFields()}
                         for p in prevs]
                analysis_data['Previous Results'] = prevs
            ret.append(analysis_data)
        return ret

    def __call__(self, request, data):
        self.request = request
        self.include_fields = get_include_fields(request)
        if not self.include_fields or "Analyses" in self.include_fields:
            data['Analyses'] = self.ar_analysis_values()

class mailto_link_from_contacts:

    def __init__(self, context):
        self.context = context

    def __call__(self, field):
        contacts = field.get(self.context)
        if not type(contacts) in (list, tuple):
            contacts = [contacts, ]
        ret = []
        for contact in contacts:
            if contact:
                mailto = "<a href='mailto:%s'>%s</a>" % (
                    contact.getEmailAddress(), contact.getFullname())
            ret.append(mailto)
        return ",".join(ret)


def mailto_link_from_ccemails(ccemails):
    def __init__(self, context):
        self.context = context

    def __call__(self, field):
        ccemails = field.get(self.context)
        addresses = ccemails.split(",")
        ret = []
        for address in addresses:
            mailto = "<a href='mailto:%s'>%s</a>" % (
                address, address)
            ret.append(mailto)
        return ",".join(ret)


