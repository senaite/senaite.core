import json
import plone

from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.browser.analysisrequest import AnalysisRequestViewView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.content.analysisrequest import schema as AnalysisRequestSchema
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


class AnalysisRequestAddView(AnalysisRequestViewView):
    """ The main AR Add form
    """
    implements(IViewView, IAnalysisRequestAddView)
    template = ViewPageTemplateFile("templates/ar_add.pt")

    def __init__(self, context, request):
        AnalysisRequestViewView.__init__(self, context, request)
        self.came_from = "add"
        self.can_edit_sample = True
        self.can_edit_ar = True
        self.DryMatterService = self.context.bika_setup.getDryMatterService()
        request.set('disable_plone.rightcolumn', 1)
        self.col_count = self.request.get('col_count', 4)
        try:
            self.col_count = int(self.col_count)
        except:
            self.col_count = 4

    def __call__(self):
        self.request.set('disable_border', 1)
        return self.template()

    def copy_to_new_specs(self):
        specs = {}
        copy_from = self.request.get('copy_from', "")
        if not copy_from:
            return {}
        uids =  copy_from.split(",")

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

    def get_fields_with_visibility(self, visibility):
        schema = self.context.Schema()
        fields = []
        for field in schema.fields():
            isVisible = field.widget.isVisible
            v = isVisible(self.context, 'add', default='invisible', field=field)
            if v == visibility:
                fields.append(field)
        return fields


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
            return {}
        uc = getToolByName(self.context, 'uid_catalog')
        proxies = uc(UID=uid)
        if not proxies:
            return {}
        sample = proxies[0].getObject()
        sample_schema = sample.Schema()
        sample_fields = dict([(f.getName(), f) for f in sample_schema.fields()])
        ar_schema = self.context.Schema()
        ar_fields = dict([(f.getName(), f) for f in ar_schema.fields()
                          if f.widget.isVisible(self.context,
                                                'secondary') == 'disabled'])
        ret = {}
        for fieldname in ar_fields.keys():
            uid = False
            if fieldname in sample_fields:
                # Always try to retrieve field value from the Sample as most
                # secondary fields are sample-bound.
                fieldvalue = sample_fields[fieldname].getAccessor(sample)()
            elif fieldname in ar_fields:
                # Some, eg "Client", are only available as conveniences
                # on the AR.
                fieldvalue = ar_fields[fieldname].getAccessor(self.context)()
            if fieldvalue is None:
                fieldvalue = ''
            if hasattr(fieldvalue, 'UID'):
                uid = fieldvalue.UID()
            if uid:
                ret[fieldname + '_uid'] = uid
            if hasattr(fieldvalue, 'Title'):
                fieldvalue = fieldvalue.Title()
            if hasattr(fieldvalue, 'year'):
                fieldvalue = fieldvalue.strftime(self.date_format_short)
            ret[fieldname] = fieldvalue
        return json.dumps(ret)


class ajaxExpandCategory(BikaListingView):
    """ ajax requests pull this view for insertion when category header
    rows are clicked/expanded. """
    template = ViewPageTemplateFile(
        "templates/analysisrequest_analysisservices.pt")

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request.form)
        plone.protect.PostOnly(self.request.form)
        if hasattr(self.context, 'getRequestID'):
            self.came_from = "edit"
        return self.template()

    def bulk_discount_applies(self):
        client = None
        if self.context.portal_type == 'AnalysisRequest':
            client = self.context.aq_parent
        elif self.context.portal_type == 'Batch':
            client = self.context.getClient()
        elif self.context.portal_type == 'Client':
            client = self.context
        return client.getBulkDiscount() if client is not None else False

    def Services(self, poc, CategoryUID):
        """ return a list of services brains """
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        services = bsc(portal_type="AnalysisService",
                       sort_on='sortable_title',
                       inactive_state='active',
                       getPointOfCapture=poc,
                       getCategoryUID=CategoryUID)
        return services


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

        errors = {}

        form_parts = json.loads(self.request.form['parts'])

        # First make a list of non-empty columns
        columns = []
        for column in range(int(form['col_count'])):
            name = 'ar.%s' % column
            ar = form.get(name, None)
            if ar and 'Analyses' in ar.keys():
                columns.append(column)

        if len(columns) == 0:
            ajax_form_error(errors, message=t(_("No analyses have been selected")))
            return json.dumps({'errors':errors})

        # Now some basic validation
        required_fields = [field.getName() for field
                           in AnalysisRequestSchema.fields()
                           if field.required]

        for column in columns:
            formkey = "ar.%s" % column
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
                if not ar.get(field, ''):
                    ajax_form_error(errors, field, column)
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
        for column in columns:
            # Get partitions from the form data
            if form_parts:
                partitions = form_parts[str(column)]
            else:
                partitions = []
            # Get the form data using the appropriate form key
            formkey = "ar.%s" % column
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
                if k+"_uid" in values:
                    continue
                resolved_values[k] = values[k]
            # Get the analyses from the form data
            analyses = values["Analyses"]

            # Gather the specifications from the form
            specs = json.loads(form['copy_to_new_specs']).get(str(column), {})
            if not specs:
                specs = json.loads(form['specs']).get(str(column), {})
            if specs:
                specs = dicts_to_dict(specs, 'keyword')
            # Modify the spec with all manually entered values
            for service_uid in analyses:
                min_element_name = "ar.%s.min.%s" % (column, service_uid)
                max_element_name = "ar.%s.max.%s" % (column, service_uid)
                error_element_name = "ar.%s.error.%s" % (column, service_uid)
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
            client = uc(UID=resolved_values['Client'])[0].getObject()
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
        if 'register' in self.context.bika_setup.getAutoPrintStickers() and new_ars:
            return json.dumps({
                'success': message,
                'stickers': new_ars,
                'stickertemplate': self.context.bika_setup.getAutoStickerTemplate()
            })
        else:
            return json.dumps({'success': message})
