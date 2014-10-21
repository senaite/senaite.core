from bika.lims.jsonapi import load_field_values
from bika.lims.interfaces import IJSONReadExtender, IARTemplate
from zope.component import adapts
from zope.interface import implements


class JSONReadExtender(object):
    """- Place additional information about profile services
    into the returned records.
    Used in AR Add to prevent extra requests
    """

    implements(IJSONReadExtender)
    adapts(IARTemplate)

    def __init__(self, context):
        self.context = context

    def __call__(self, request, data):
        bsc = self.context.bika_setup_catalog
        service_data = []
        for item in self.context.getAnalyses():
            service_uid = item['service_uid']
            service = bsc(UID=service_uid)[0].getObject()
            this_service = {'UID': service.UID(),
                            'PointOfCapture': service.getPointOfCapture(),
                            'CategoryTitle': service.getCategory().Title()}
            service_data.append(this_service)
        data['service_data'] = service_data
