from Products.CMFCore.utils import getToolByName
from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.utils import getUsers
from bika.lims import bikaMessageFactory as _

class SelectionMacrosView(BrowserView):
    """ Display snippets for the query form

    These methods are called directlly from tal:

        context/@@selection_macros/analysts

    or from Python:

        python:view.selection_macros.analysisservices(allow_blank=False)

    """
    def __init__(self, context, request):
        super(SelectionMacrosView, self).__init__(context, request)
        self.bc = getToolByName(context, 'bika_catalog')
        self.bac = getToolByName(context, 'bika_analysis_catalog')
        self.bsc = getToolByName(context, 'bika_setup_catalog')
        self.pc = getToolByName(context, 'portal_catalog')

    select_analysiscategory_pt = ViewPageTemplateFile("select_analysiscategory.pt")
    def select_analysiscategory(self):
        self.analysiscategories = self.bsc(portal_type='AnalysisCategory',
                                           sort_on='sortable_title')
        return self.select_analysiscategory_pt()

    select_analysisservice_pt = ViewPageTemplateFile("select_analysisservice.pt")
    def select_analysisservice(self, allow_blank=True, multiselect=False):
        self.allow_blank = allow_blank
        self.multiselect = multiselect
        self.analysisservices = self.bsc(portal_type='AnalysisService',
                                         sort_on='sortable_title')
        return self.select_analysisservice_pt()

    select_analysisspecification_pt = ViewPageTemplateFile("select_analysisspecification.pt")
    def select_analysisspecification(self, specs=['lab', 'client']):
        self.specs = specs
        return self.select_analysisspecification_pt()

    select_analyst_pt = ViewPageTemplateFile("select_analyst.pt")
    def select_analyst(self):
        self.analysts = getUsers(self.context,
                                 ['Manager', 'LabManager', 'Analyst'])
        return self.select_analyst_pt()

    select_client_pt = ViewPageTemplateFile("select_client.pt")
    def select_client(self):
        self.clients = self.pc(portal_type='Client',
                               inactive_state='active',
                               sort_on='sortable_title')
        return self.select_client_pt()

    select_contact_pt = ViewPageTemplateFile("select_contact.pt")
    def select_contact(self):
        self.contacts = self.pc(portal_type='Contact',
                                inactive_state='active',
                                sort_on='sortable_title')
        return self.select_contact_pt()

    select_daterange_pt = ViewPageTemplateFile("select_daterange.pt")
    def select_daterange(self, field_id, field_title):
        self.field_id = field_id
        self.field_title = _(field_title)
        return self.select_daterange_pt()

    select_instrument_pt = ViewPageTemplateFile("select_instrument.pt")
    def select_instrument(self):
        self.instruments = self.bsc(portal_type='Instrument',
                                    inactive_state='active',
                                    sort_on='sortable_title')
        return self.select_instrument_pt()

    select_period_pt = ViewPageTemplateFile("select_period.pt")
    def select_period(self):
        return self.select_period_pt()

    select_profile_pt = ViewPageTemplateFile("select_profile.pt")
    def select_profile(self):
        self.analysisprofiles = self.bsc(portal_type='AnalysisProfile',
                                         inactive_state='active',
                                         sort_on='sortable_title')
        return self.select_profile_pt()

    select_state_pt = ViewPageTemplateFile("select_state.pt")
    def select_state(self, workflow_id, field_id, field_title):
        self.field_id = field_id
        self.field_title = field_title
        wf = getToolByName(self.context, 'portal_workflow')
        states = wf[workflow_id].states
        self.states = []
        for state_id in states:
            state = states[state_id]
            self.states.append({
                'id': state.getId(),
                'title': state.title
            })
        return self.select_state_pt()

    select_samplepoint_pt = ViewPageTemplateFile("select_samplepoint.pt")
    def select_samplepoint(self, allow_blank=True, multiselect=False):
        self.allow_blank = allow_blank
        self.multiselect = multiselect
        self.samplepoints = self.bsc(portal_type='SamplePoint',
                                     inactive_state='active',
                                     sort_on='sortable_title')
        return self.select_samplepoint_pt()

    select_sampletype_pt = ViewPageTemplateFile("select_sampletype.pt")
    def select_sampletype(self, allow_blank=True, multiselect=False):
        self.allow_blank = allow_blank
        self.multiselect = multiselect
        self.sampletypes = self.bsc(portal_type='SampleType',
                                    inactive_state='active',
                                    sort_on='sortable_title')
        return self.select_sampletype_pt()
