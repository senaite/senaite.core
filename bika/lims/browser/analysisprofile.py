from bika.lims.jsonapi import load_field_values
from bika.lims.interfaces import IJSONReadExtender, IAnalysisProfile
from zope.component import adapts
from zope.interface import implements


class JSONReadExtender(object):
    """- Place additional information about profile services
    into the returned records.
    Used in AR Add to prevent extra requests
    """

    implements(IJSONReadExtender)
    adapts(IAnalysisProfile)

    def __init__(self, context):
        self.context = context

    def __call__(self, request, data):
        service_data = []
        for service in self.context.getService():
            this_service = {'UID': service.UID(),
                            'PointOfCapture': service.getPointOfCapture(),
                            'CategoryTitle': service.getCategory().Title()}
            service_data.append(this_service)
        data['service_data'] = service_data
