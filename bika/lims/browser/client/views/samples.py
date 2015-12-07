from bika.lims.browser.sample import SamplesView


class ClientSamplesView(SamplesView):
    def __init__(self, context, request):
        super(ClientSamplesView, self).__init__(context, request)

        self.contentFilter['path'] = {
            "query": "/".join(context.getPhysicalPath()),
            "level": 0}
        review_states = []
        for review_state in self.review_states:
            review_state['columns'].remove('Client')
            review_states.append(review_state)
        self.review_states = review_states
