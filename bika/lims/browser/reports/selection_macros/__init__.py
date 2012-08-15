from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.utils import getUsers
from bika.lims import bikaMessageFactory as _

class SelectionMacrosView(BrowserView):
    """ Display snippets for the query form
    """
    def __init__(self, context, request):
        super(SelectionMacrosView, self).__init__(context, request)
        self.bc = getToolByName(context, 'bika_catalog')
        self.bac = getToolByName(context, 'bika_analysis_catalog')
        self.bsc = getToolByName(context, 'bika_setup_catalog')
        self.pc = getToolByName(context, 'portal_catalog')

    select_analysiscategory = ViewPageTemplateFile("select_analysiscategory.pt")

    def analysiscategories(self):
        return self.bsc(portal_type='AnalysisCategory',
                        sort_on='sortable_title')

    select_analysisservice = ViewPageTemplateFile("select_analysisservice.pt")

    def analysisservices(self):
        return self.bsc(portal_type='AnalysisService',
                        sort_on='sortable_title')

    select_analysisspecification = ViewPageTemplateFile("select_analysisspecification.pt")

    select_analyst = ViewPageTemplateFile("select_analyst.pt")

    def analysts(self):
        return getUsers(self.context, ['Manager', 'LabManager', 'Analyst'])

    select_cancellation_state = ViewPageTemplateFile("select_cancellation_state.pt")

    def cancellation_states(self):
        wf = getToolByName(self.context, 'portal_workflow')
        states = []
        for state_id in ('active', 'cancelled'):
            # the 'Analysis' type is irrelevant
            state_title = wf.getTitleForStateOnType(state_id, 'Analysis')
            states.append({
                'id': state_id,
                'title': state_title} )
        return states

    select_client = ViewPageTemplateFile("select_client.pt")

    def clients(self):
        return self.pc(portal_type='Client',
                       inactive_state='active',
                       sort_on='sortable_title')

    select_contact = ViewPageTemplateFile("select_contact.pt")

    def contacts(self):
        return self.pc(portal_type='Contact',
                       inactive_state='active',
                       sort_on='sortable_title')

    select_daterange = ViewPageTemplateFile("select_daterange.pt")

    def select_date_received(self):
        self.field_title = _("Date Received")
        self.field_name = 'Received'
        return self.select_daterange()

    def select_date_requested(self):
        self.field_title = _("Date Requested")
        self.field_name = 'Requested'
        return self.select_daterange()

    def select_date_published(self):
        self.field_title = _("Date Published")
        self.field_name = 'Published'
        return self.select_daterange()

    def select_date_loaded(self):
        self.field_title = _("Date Loaded")
        self.field_name = 'Loaded'
        return self.select_daterange()

    select_instrument = ViewPageTemplateFile("select_instrument.pt")

    def instruments(self):
        return self.bsc(portal_type='Instrument',
                        inactive_state='active',
                        sort_on='sortable_title')

    select_period = ViewPageTemplateFile("select_period.pt")

    select_profile = ViewPageTemplateFile("select_profile.pt")

    def analysisprofiles(self):
        return self.bsc(portal_type='AnalysisProfile',
                        inactive_state='active',
                        sort_on='sortable_title')

    select_analysis_review_state = ViewPageTemplateFile("select_analysis_review_state.pt")

    def analysis_review_states(self):
        wf = getToolByName(self.context, 'portal_workflow')
        states_folder = wf.bika_analysis_workflow.states
        states = []
        for state_id in ('sample_due',
                         'sample_received',
                         'attachment_due',
                         'to_be_verified',
                         'verified',
                         'published'):
            state = states_folder[state_id]
            states.append({
                'id': state.getId(),
                'title': state.title
            })
        return states

    select_samplepoint = ViewPageTemplateFile("select_samplepoint.pt")

    def samplepoints(self):
        return bika_setup_catalog(portal_type='SamplePoint',
                                  inactive_state='active',
                                  sort_on='sortable_title')

    select_sampletype = ViewPageTemplateFile("select_sampletype.pt")

    def sampletypes(self):
        return bika_setup_catalog(portal_type='SampleType',
                                  inactive_state='active',
                                  sort_on='sortable_title')

    select_worksheet_state = ViewPageTemplateFile("select_worksheet_state.pt")

##    def __call__(self):
##        return self.template()
