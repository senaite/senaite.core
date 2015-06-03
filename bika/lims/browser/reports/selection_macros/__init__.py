from Products.CMFCore.utils import getToolByName
from zope.i18n import translate
from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.utils import getUsers
from bika.lims import bikaMessageFactory as _
from bika.lims import PMF

class SelectionMacrosView(BrowserView):
    """ Display snippets for the query form, and
        parse their results to contentFilter

    These methods are called directlly from tal:

        context/@@selection_macros/analysts

    To parse form values in reports:

        python:view.selection_macros.parse_analysisservice(allow_blank=False)

    The parse_ functions return {'contentFilter': (k,v),
                                 'parms': (k,v),
                                 'title': string
                                 }

    """

    def __init__(self, context, request):
        super(SelectionMacrosView, self).__init__(context, request)
        self.bc = self.bika_catalog
        self.bac = self.bika_analysis_catalog
        self.bsc = self.bika_setup_catalog
        self.pc = self.portal_catalog
        self.rc = self.reference_catalog

    select_analysiscategory_pt = ViewPageTemplateFile(
        "select_analysiscategory.pt")

    def select_analysiscategory(self, style=None):
        self.style = style
        self.analysiscategories = self.bsc(portal_type='AnalysisCategory',
                                           sort_on='sortable_title')
        return self.select_analysiscategory_pt()

    select_analysisservice_pt = ViewPageTemplateFile("select_analysisservice.pt")

    def select_analysisservice(self, allow_blank=True, multiselect=False,
                               style=None):
        self.style = style
        self.allow_blank = allow_blank
        self.multiselect = multiselect
        self.analysisservices = self.bsc(portal_type='AnalysisService',
                                         sort_on='sortable_title')
        return self.select_analysisservice_pt()

    def parse_analysisservice(self, request):
        val = request.form.get("ServiceUID", "")
        if val:
            if not type(val) in (list, tuple):
                val = (val,)  # Single service
            val = [self.rc.lookupObject(s) for s in val]
            uids = [o.UID() for o in val]
            titles = [o.Title() for o in val]
            res = {}
            res['contentFilter'] = ('getServiceUID', uids)
            res['parms'] = {'title': _("Services"), 'value': ','.join(titles)}
            res['titles'] = ','.join(titles)
            return res

    select_analysisspecification_pt = ViewPageTemplateFile(
        "select_analysisspecification.pt")

    def select_analysisspecification(self, style=None):
        self.style = style
        specfolder_uid = self.context.bika_setup.bika_analysisspecs.UID()
        res = []
        bsc = getToolByName(self.context, "bika_setup_catalog")
        for s in bsc(portal_type='AnalysisSpec'):
            if s.getClientUID == specfolder_uid:
                res.append({'uid': s.UID, 'title': s.Title})
        for c in self.context.clients.objectValues():
            for s in c.objectValues():
                if s.portal_type != 'AnalysisSpec':
                    continue
                res.append(
                    {'uid': s.UID(), 'title': s.Title() + " (" + c.Title() + ")"})
        self.specs = res
        return self.select_analysisspecification_pt()

    select_analyst_pt = ViewPageTemplateFile("select_analyst.pt")

    def select_analyst(self, allow_blank=False, style=None):
        self.style = style
        self.analysts = getUsers(self.context,
                                 ['Manager', 'Analyst', 'LabManager'],
                                 allow_blank)
        return self.select_analyst_pt()

    select_user_pt = ViewPageTemplateFile("select_user.pt")

    def select_user(self, allow_blank=True, style=None):
        self.style = style
        self.allow_blank = allow_blank
        self.users = getUsers(self.context, None, allow_blank)
        return self.select_user_pt()

    select_client_pt = ViewPageTemplateFile("select_client.pt")

    def select_client(self, style=None):
        self.style = style
        self.clients = self.pc(portal_type='Client', inactive_state='active',
                               sort_on='sortable_title')
        return self.select_client_pt()

    def parse_client(self, request):
        val = request.form.get("ClientUID", "")
        if val:
            obj = val and self.rc.lookupObject(val)
            title = obj.Title()
            res = {}
            res['contentFilter'] = ('getClientUID', val)
            res['parms'] = {'title': _("Client"), 'value': title}
            res['titles'] = title
            return res

    select_contact_pt = ViewPageTemplateFile("select_contact.pt")

    def select_contact(self, style=None):
        self.style = style
        self.contacts = self.pc(portal_type='Contact', inactive_state='active',
                                sort_on='sortable_title')
        return self.select_contact_pt()

    select_daterange_pt = ViewPageTemplateFile("select_daterange.pt")

    def select_daterange(self, field_id, field_title, style=None):
        self.style = style
        self.field_id = field_id
        self.field_title = _(field_title)
        return self.select_daterange_pt()

    def parse_daterange(self, request, field_id, field_title):
        from_date = request.get('%s_fromdate' % field_id, None)
        from_date = from_date and from_date + ' 00:00' or None
        to_date = request.get('%s_todate' % field_id, None)
        to_date = to_date and to_date + ' 23:59' or None
        if from_date and to_date:
            query = {'query': [from_date, to_date], 'range': 'min:max'}
        elif from_date or to_date:
            query = {'query': from_date or to_date,
                     'range': from_date and 'min' or 'max'}
        else:
            return None

        if from_date and to_date:
            parms = translate(_("From ${start_date} to ${end_date}",
                               mapping={"start_date":from_date, "end_date":to_date}))
        elif from_date:
            parms = translate(_("Before ${start_date}",
                               mapping={"start_date":from_date}))
        elif to_date:
            parms = translate(_("After ${end_date}",
                               mapping={"end_date":to_date}))

        res = {}
        res['contentFilter'] = (field_id, query)
        res['parms'] = {'title': field_title, 'value': parms}
        res['titles'] = parms
        return res

    select_instrument_pt = ViewPageTemplateFile("select_instrument.pt")

    def select_instrument(self, style=None):
        self.style = style
        self.instruments = self.bsc(portal_type='Instrument',
                                    inactive_state='active',
                                    sort_on='sortable_title')
        return self.select_instrument_pt()

    select_period_pt = ViewPageTemplateFile("select_period.pt")

    def select_period(self, style=None):
        self.style = style
        return self.select_period_pt()

    select_profile_pt = ViewPageTemplateFile("select_profile.pt")

    def select_profile(self, style=None):
        self.style = style
        self.analysisprofiles = self.bsc(portal_type='AnalysisProfile',
                                         inactive_state='active',
                                         sort_on='sortable_title')
        return self.select_profile_pt()

    select_supplier_pt = ViewPageTemplateFile("select_supplier.pt")

    def select_supplier(self, style=None):
        self.style = style
        self.suppliers = self.bsc(portal_type='Supplier', inactive_state='active',
                                  sort_on='sortable_title')
        return self.select_supplier_pt()

    select_reference_sample_pt = ViewPageTemplateFile(
        "select_reference_sample.pt")

    def select_reference_sample(self, style=None):
        self.style = style
        return self.select_reference_sample_pt()

    select_reference_service_pt = ViewPageTemplateFile(
        "select_reference_service.pt")

    def select_reference_service(self, style=None):
        self.style = style
        return self.select_reference_service_pt()

    select_state_pt = ViewPageTemplateFile("select_state.pt")

    def select_state(self, workflow_id, field_id, field_title, style=None):
        self.style = style
        self.field_id = field_id
        self.field_title = field_title
        states = self.portal_workflow[workflow_id].states
        self.states = []
        for state_id in states:
            state = states[state_id]
            self.states.append({'id': state.getId(), 'title': state.title})
        return self.select_state_pt()

    def parse_state(self, request, workflow_id, field_id, field_title):
        val = request.form.get(field_id, "")
        states = self.portal_workflow[workflow_id].states
        if val in states:
            state_title = states[val].title
            res = {}
            res['contentFilter'] = (field_id, val)
            res['parms'] = {'title': _('State'), 'value': state_title}
            res['titles'] = state_title
            return res

    select_samplepoint_pt = ViewPageTemplateFile("select_samplepoint.pt")

    def select_samplepoint(self, allow_blank=True, multiselect=False, style=None):
        self.style = style
        self.allow_blank = allow_blank
        self.multiselect = multiselect
        self.samplepoints = self.bsc(portal_type='SamplePoint',
                                     inactive_state='active',
                                     sort_on='sortable_title')
        return self.select_samplepoint_pt()

    def parse_samplepoint(self, request):
        val = request.form.get("SamplePointUID", "")
        if val:
            obj = val and self.rc.lookupObject(val)
            title = obj.Title()
            res = {}
            res['contentFilter'] = ('getSamplePointUID', val)
            res['parms'] = {'title': _("Sample Point"), 'value': title}
            res['titles'] = title
            return res

    select_sampletype_pt = ViewPageTemplateFile("select_sampletype.pt")

    def select_sampletype(self, allow_blank=True, multiselect=False, style=None):
        self.style = style
        self.allow_blank = allow_blank
        self.multiselect = multiselect
        self.sampletypes = self.bsc(portal_type='SampleType',
                                    inactive_state='active',
                                    sort_on='sortable_title')
        return self.select_sampletype_pt()

    def parse_sampletype(self, request):
        val = request.form.get("SampleTypeUID", "")
        if val:
            obj = val and self.rc.lookupObject(val)
            title = obj.Title()
            res = {}
            res['contentFilter'] = ('getSampleTypeUID', val)
            res['parms'] = {'title': _("Sample Type"), 'value': title}
            res['titles'] = title
            return res

    select_groupingperiod_pt = ViewPageTemplateFile("select_groupingperiod.pt")

    def select_groupingperiod(self, allow_blank=True, multiselect=False,
                              style=None):
        self.style = style
        self.allow_blank = allow_blank
        return self.select_groupingperiod_pt()

    select_output_format_pt = ViewPageTemplateFile("select_output_format.pt")

    def select_output_format(self, style=None):
        self.style = style
        return self.select_output_format_pt()
