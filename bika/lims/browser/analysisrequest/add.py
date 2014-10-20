import json
import plone

from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.browser.analysisrequest import AnalysisRequestViewView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.content.analysisrequest import schema as AnalysisRequestSchema
from bika.lims.controlpanel.bika_analysisservices import \
    AnalysisServicesView as ASV
from bika.lims.interfaces import IAnalysisRequestAddView
from bika.lims.utils import getHiddenAttributesForClass, dicts_to_dict
from bika.lims.utils import t
from bika.lims.utils import tmpID
from bika.lims.utils.analysisrequest import create_analysisrequest
from bika.lims.utils.form import ajax_form_error
from magnitude import mg
from plone.app.layout.globals.interfaces import IViewView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType, safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getAdapter
from zope.interface import implements


class AnalysisServicesView(ASV):
    def _get_selected_items(self, full_objects=True, form_key=None):
        """ return a list of selected form objects
            full_objects defaults to True
        """
        form = self.request.form.get(form_key,
            {}) if form_key else self.request.form
        uc = getToolByName(self.context, 'uid_catalog')

        selected_items = {}
        for uid in form.get('uids', []):
            try:
                item = uc(UID=uid)[0].getObject()
            except IndexError:
                # ignore selected item if object no longer exists
                continue
            selected_items[uid] = item
        return selected_items.values()

    def __init__(self, context, request, poc, ar_count=None):
        super(AnalysisServicesView, self).__init__(context, request)
        self.ar_count = ar_count if ar_count else 4

        self.ar_add_items = []

        # Customise form for AR Add context
        self.poc = poc
        self.form_id = "services_" + poc
        self.contentFilter['getPointOfCapture'] = poc

        self.pagesize = 0
        self.table_only = True
        self.review_states = [
            x for x in self.review_states if x['id'] == 'default']
        self.review_states[0]['custom_actions'] = []
        self.review_states[0]['transitions'] = []

        # Configure column layout
        to_remove = ['Category', 'Instrument', 'Unit', 'Calculation', 'Keyword']
        if not context.bika_setup.getShowPrices():
            to_remove.append('Price')
        for col_name in to_remove:
            if col_name in self.review_states[0]['columns']:
                self.review_states[0]['columns'].remove(col_name)
        if context.bika_setup.getEnableARSpecs():
            self.columns.update(
                {'Min': {'title': _('Min')},
                 'Max': {'title': _('Max')},
                 'Error': {'title': _('Error %')}})
            self.review_states[0]['columns'].extend(
                ['Min', 'Max', 'Error'])

        # Add columns for each AR
        for arnum in range(self.ar_count):
            self.columns['ar.%s' % arnum] = {
                'title': _('AR ${ar_number}', mapping={'ar_number': arnum}),
                'sortable': False,
                'type': 'boolean'
            }
            self.review_states[0]['columns'].append('ar.%s' % arnum)

        # XXX. Removing sortable from services - it causes bugs in ar_add.
        for k, v in self.columns.items():
            self.columns[k]['sortable'] = False

        # results cached in ar_add_items
        self.folderitems()

    def folderitems(self):
        # This folderitems acts slightly differently from others, in that it
        # saves it's results in an attribute, and prevents itself from being
        # run multiple times.  This is necessary so that AR Add can check
        # the item count before choosing to render the table at all.
        if not self.ar_add_items:
            bs = self.context.bika_setup
            items = super(AnalysisServicesView, self).folderitems()
            for x, item in enumerate(items):
                if bs.getShowPrices():
                    items[x]['allow_edit'] = ['Price']
                if bs.getEnableARSpecs():
                    items[x]['allow_edit'].extend(['Min', 'Max', 'Error'])
                    items[x]['Min'] = ''
                    items[x]['Max'] = ''
                    items[x]['Error'] = ''
                for arnum in range(self.ar_count):
                    selected = self._get_selected_items(form_key='ar.%s' % arnum)
                    if item in selected:
                        items[x]['ar.%s' % arnum] = True
                    else:
                        items[x]['ar.%s' % arnum] = False
                    # always editable
                    items[x]['allow_edit'].append('ar.%s' % arnum)
            self.ar_add_items = items
        return self.ar_add_items


class AnalysisRequestAddView(AnalysisRequestViewView):
    """ The main AR Add form
    """
    implements(IViewView, IAnalysisRequestAddView)
    template = ViewPageTemplateFile("templates/ar_add.pt")
    ar_add_by_row_template = ViewPageTemplateFile('templates/ar_add_by_row.pt')
    ar_add_by_col_template = ViewPageTemplateFile('templates/ar_add_by_col.pt')

    def __init__(self, context, request):
        AnalysisRequestViewView.__init__(self, context, request)
        self.came_from = "add"
        self.can_edit_sample = True
        self.can_edit_ar = True
        self.DryMatterService = self.context.bika_setup.getDryMatterService()
        request.set('disable_plone.rightcolumn', 1)
        self.layout = self.request.get('layout', 'columns')
        self.ar_count = self.request.get('ar_count', 4)
        try:
            self.ar_count = int(self.ar_count)
        except ValueError:
            self.ar_count = 4

    def __call__(self):
        self.request.set('disable_border', 1)
        return self.template()

    def copy_to_new_specs(self):
        specs = {}
        copy_from = self.request.get('copy_from', "")
        if not copy_from:
            return {}
        uids = copy_from.split(",")

        n = 0
        for uid in uids:
            proxies = self.bika_catalog(UID=uid)
            rr = proxies[0].getObject().getResultsRange()
            new_rr = []
            for i, r in enumerate(rr):
                s_uid = self.bika_setup_catalog(portal_type='AnalysisService',
                                                getKeyword=r['keyword'])[0].UID
                r['uid'] = s_uid
                new_rr.append(r)
            specs[n] = new_rr
            n += 1
        return json.dumps(specs)

    def getContacts(self):
        adapter = getAdapter(self.context.aq_parent, name='getContacts')
        return adapter()

    def partitioned_services(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        ps = []
        for service in bsc(portal_type='AnalysisService'):
            service = service.getObject()
            if service.getPartitionSetup() \
                    or service.getSeparate():
                ps.append(service.UID())
        return json.dumps(ps)

    def get_fields_with_visibility(self, visibility, mode=None):
        mode = mode if mode else 'add'
        schema = self.context.Schema()
        fields = []
        for field in schema.fields():
            isVisible = field.widget.isVisible
            v = isVisible(self.context, mode, default='invisible', field=field)
            if v == visibility:
                fields.append(field)
        return fields

    def services_widget_content(self, poc, ar_count=None):
        """Return a table displaying services to be selected for inclusion
        in a new AR.  Used in add_by_row view popup, and add_by_col add view.
        """
        if not ar_count:
            ar_count = self.ar_count
        s = AnalysisServicesView(self.context, self.request,
                                 poc, ar_count=ar_count)
        s.folderitems()
        if not s.ar_add_items:
            return ""
        return s.contents_table()


class SecondaryARSampleInfo(BrowserView):
    """Return fieldnames and pre-digested values for Sample fields which
    javascript must disable/display while adding secondary ARs.

    This relies on the schema field's widget.isVisible setting, and
    will allow an extra visibility setting:   "disabled".

    """

    def __init__(self, context, request):
        super(SecondaryARSampleInfo, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        uid = self.request.get('Sample_uid', False)
        if not uid:
            return []
        uc = getToolByName(self.context, "uid_catalog")
        proxies = uc(UID=uid)
        if not proxies:
            return []
        sample = proxies[0].getObject()
        sample_schema = sample.Schema()
        sample_fields = dict([(f.getName(), f) for f in sample_schema.fields()])
        ar_schema = self.context.Schema()
        ar_fields = [f.getName() for f in ar_schema.fields()
                     if f.widget.isVisible(self.context,
                                           'secondary') == 'disabled']
        ret = []
        for fieldname in ar_fields:
            if fieldname in sample_fields:
                fieldvalue = sample_fields[fieldname].getAccessor(sample)()
                if fieldvalue is None:
                    fieldvalue = ''
                if hasattr(fieldvalue, 'Title'):
                    fieldvalue = fieldvalue.Title()
                if hasattr(fieldvalue, 'year'):
                    fieldvalue = fieldvalue.strftime(self.date_format_short)
            else:
                fieldvalue = ''
            ret.append([fieldname, fieldvalue])
        return json.dumps(ret)


class ajaxAnalysisRequestSubmit():
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):

        form = self.request.form
        plone.protect.CheckAuthenticator(self.request.form)
        plone.protect.PostOnly(self.request.form)
        came_from = 'came_from' in form and form['came_from'] or 'add'
        wftool = getToolByName(self.context, 'portal_workflow')
        uc = getToolByName(self.context, 'uid_catalog')
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        layout = form['layout']

        errors = {}

        form_parts = json.loads(self.request.form['parts'])

        # Get header values out, get values, exclude from any loops below
        headerfieldnames = ['Client', 'Client_uid', 'Contact', 'Contact_uid',
                            'CCContact', 'CCContact_uid', 'CCEmails',
                            'Batch', 'Batch_uid',
                            'InvoiceContact', 'InvoiceContact_uid']
        headers = {}
        for field in form.keys():
            if field in headerfieldnames:
                headers[field] = form[field]


        # First make a list of non-empty fieldnames
        fieldnames = []
        for arnum in range(int(form['ar_count'])):
            name = 'ar.%s' % arnum
            ar = form.get(name, None)
            if ar and 'Analyses' in ar.keys() and ar['Analyses'] != '':
                fieldnames.append(arnum)

        if len(fieldnames) == 0:
            ajax_form_error(errors,
                            message=t(_("No analyses have been selected")))
            return json.dumps({'errors': errors})

        # Now some basic validation
        required_fields = [field.getName() for field
                           in AnalysisRequestSchema.fields()
                           if field.required]

        for fieldname in fieldnames:
            formkey = "ar.%s" % fieldname
            ar = form[formkey]

            # check that required fields have values
            for field in required_fields:
                # This one is still special.
                if field in ['RequestID']:
                    continue
                    # And these are not required if this is a secondary AR
                if ar.get('Sample', '') != '' and field in [
                    'SamplingDate',
                    'SampleType'
                ]:
                    continue
                if not ar.get(field, '') and not headers.get(field, ''):
                    ajax_form_error(errors, field, fieldname)
        # Return errors if there are any
        if errors:
            return json.dumps({'errors': errors})

        # Get the prices from the form data
        prices = form.get('Prices', None)
        # Initialize the Anlysis Request collection
        ARs = []
        # if a new profile is created automatically,
        # this flag triggers the status message
        new_profile = None
        # The actual submission
        # fieldname == same as arnum == same as column ...
        for fieldname in fieldnames:
            # Get partitions from the form data
            if form_parts:
                partitions = form_parts[str(fieldname)]
            else:
                partitions = []
            # Get the form data using the appropriate form key
            formkey = "ar.%s" % fieldname
            values = form[formkey].copy()
            # resolved values is formatted as acceptable by archetypes
            # widget machines
            resolved_values = {}
            for k, v in values.items():
                # Analyses, we handle that specially.
                if k == 'Analyses':
                    continue
                # Insert the reference *_uid values instead of titles.
                if "_uid" in k:
                    v = values[k]
                    v = v.split(",") if v and "," in v else v
                    fname = k.replace("_uid", "")
                    resolved_values[fname] = v
                    continue
                # we want to write the UIDs and ignore the title values
                if k + "_uid" in values:
                    continue
                resolved_values[k] = values[k]
            # Get the analyses from the form data
            analyses = values["Analyses"]

            # Gather the specifications from the form
            specs = json.loads(form['copy_to_new_specs']).get(str(fieldname),
                {})
            if not specs:
                specs = json.loads(form['specs']).get(str(fieldname), {})
            if specs:
                specs = dicts_to_dict(specs, 'keyword')
            # Modify the spec with all manually entered values
            for service_uid in analyses:
                min_element_name = "ar.%s.min.%s" % (fieldname, service_uid)
                max_element_name = "ar.%s.max.%s" % (fieldname, service_uid)
                error_element_name = "ar.%s.error.%s" % (fieldname, service_uid)
                service_keyword = bsc(UID=service_uid)[0].getKeyword
                if min_element_name in form:
                    if service_keyword not in specs:
                        specs[service_keyword] = {}
                    specs[service_keyword]["keyword"] = service_keyword
                    specs[service_keyword]["min"] = form[min_element_name]
                    specs[service_keyword]["max"] = form[max_element_name]
                    specs[service_keyword]["error"] = form[error_element_name]

            # Selecting a template sets the hidden 'parts' field to template values.
            # Selecting a profile will allow ar_add.js to fill in the parts field.
            # The result is the same once we are here.
            if not partitions:
                partitions = [{
                                  'services': [],
                                  'container': None,
                                  'preservation': '',
                                  'separate': False
                              }]
            # Apply DefaultContainerType to partitions without a container
            default_container_type = resolved_values.get(
                'DefaultContainerType', None
            )
            if default_container_type:
                container_type = bsc(UID=default_container_type)[0].getObject()
                containers = container_type.getContainers()
                for partition in partitions:
                    if not partition.get("container", None):
                        partition['container'] = containers
            # Retrieve the catalogue reference to the client
            if layout and layout == 'columns':
                client = uc(UID=resolved_values['Client'])[0].getObject()
            else:
                client = uc(UID=headers['Client_uid'])[0].getObject()
            # Create the Analysis Request
            ar = create_analysisrequest(
                client,
                self.request,
                resolved_values,
                analyses=analyses,
                partitions=partitions,
                specifications=specs.values(),
                prices=prices
            )
            # Add Headers
            for fieldname in headers.keys():
                if headers[fieldname] != '' and not fieldname.endswith('_uid'):
                    if headers.get(fieldname + '_uid'):
                        field = ar.Schema()[fieldname];
                        mutator = field.getMutator(ar)
                        uid = headers[fieldname + '_uid']
                        obj = uc(UID=uid)[0].getObject()
                        mutator(obj)
                    else:
                        ar.edit(fieldname=headers[fieldname])

            # Add the created analysis request to the list
            ARs.append(ar.getId())
        # Display the appropriate message after creation
        if len(ARs) > 1:
            message = _("Analysis requests ${ARs} were successfully created.",
                        mapping={'ARs': safe_unicode(', '.join(ARs))})
        else:
            message = _("Analysis request ${AR} was successfully created.",
                        mapping={'AR': safe_unicode(ARs[0])})
        self.context.plone_utils.addPortalMessage(message, 'info')
        # Automatic label printing
        # Won't print labels for Register on Secondary ARs
        new_ars = None
        if came_from == 'add':
            new_ars = [ar for ar in ARs if ar[-2:] == '01']
        if 'register' in self.context.bika_setup.getAutoPrintLabels() and new_ars:
            return json.dumps({
                'success': message,
                'labels': new_ars,
                'labelsize': self.context.bika_setup.getAutoLabelSize()
            })
        else:
            return json.dumps({'success': message})
