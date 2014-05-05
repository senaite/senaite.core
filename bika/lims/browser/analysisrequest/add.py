import json

from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.content.analysisrequest import schema as AnalysisRequestSchema
from bika.lims.interfaces import IAnalysisRequestAddView
from bika.lims.browser.analysisrequest import AnalysisRequestViewView
from bika.lims.jsonapi import load_brain_metadata
from bika.lims.jsonapi import load_field_values
from bika.lims.utils import to_utf8
from bika.lims.utils import tmpID
from bika.lims.workflow import doActionFor
from plone.app.layout.globals.interfaces import IViewView
from Products.Archetypes import PloneMessageFactory as PMF
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.utils import _createObjectByType
from zope.component import getAdapter
from zope.interface import implements
import plone


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

    def getContacts(self):
        adapter = getAdapter(self.context.aq_parent, name='getContacts')
        return adapter()

    def getWidgetVisibility(self):
        adapter = getAdapter(self.context, name='getWidgetVisibility')
        ret = adapter()
        ordered_ret = {}
        # respect schemaextender's re-ordering of fields
        schema_fields = [f.getName() for f in self.context.Schema().fields()]
        for mode, state_field_lists in ret.items():
            ordered_ret[mode] = {}
            for statename, state_fields in state_field_lists.items():
                ordered_ret[mode][statename] = \
                    [field for field in schema_fields if field in state_fields]
        return ordered_ret


    def partitioned_services(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        ps = []
        for service in bsc(portal_type='AnalysisService'):
            service = service.getObject()
            if service.getPartitionSetup() \
                or service.getSeparate():
                ps.append(service.UID())
        return json.dumps(ps)

class SecondaryARSampleInfo(BrowserView):
    """Return fieldnames and pre-digested values for Sample fields which
    javascript must disable/display while adding secondary ARs
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        uid = self.request.get('Sample_uid')
        uc = getToolByName(self.context, "uid_catalog")
        sample = uc(UID=uid)[0].getObject()
        sample_schema = sample.Schema()
        adapter = getAdapter(self.context, name='getWidgetVisibility')
        wv = adapter()
        fieldnames = wv.get('secondary', {}).get('invisible', [])
        ret = []
        for fieldname in fieldnames:
            if fieldname in sample_schema:
                fieldvalue = sample_schema[fieldname].getAccessor(sample)()
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


class ajaxExpandCategory(BikaListingView):
    """ ajax requests pull this view for insertion when category header
    rows are clicked/expanded. """
    template = ViewPageTemplateFile("templates/analysisrequest_analysisservices.pt")

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

        SamplingWorkflowEnabled = \
            self.context.bika_setup.getSamplingWorkflowEnabled()

        errors = {}

        def error(field=None, column=None, message=None):
            if not message:
                message = to_utf8(self.context.translate(
                    PMF('Input is required but no input given.')))
            if (column or field):
                error_key = " %s.%s" % (int(column) + 1, field or '')
            else:
                error_key = "Form Error"
            errors[error_key] = message

        form_parts = json.loads(self.request.form['parts'])

        # First make a list of non-empty columns
        columns = []
        for column in range(int(form['col_count'])):
            if "ar.%s" % column not in form:
                continue
            ar = form["ar.%s" % column]
            if 'Analyses' not in ar.keys():
                continue
            columns.append(column)

        if len(columns) == 0:
            error(message=to_utf8(self.context.translate(_("No analyses have been selected"))))
            return json.dumps({'errors': errors})

        # Now some basic validation
        required_fields = [field.getName() for field
                           in AnalysisRequestSchema.fields()
                           if field.required]

        for column in columns:
            formkey = "ar.%s" % column
            ar = form[formkey]

            # Secondary ARs don't have sample fields present in the form data
            # if 'Sample_uid' in ar and ar['Sample_uid']:
            #     adapter = getAdapter(self.context, name='getWidgetVisibility')
            #     wv = adapter().get('secondary', {}).get('invisible', [])
            #     required_fields = [x for x in required_fields if x not in wv]

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
                if (field in ar and not ar.get(field, '')):
                    error(field, column)

        if errors:
            return json.dumps({'errors': errors})

        prices = form.get('Prices', None)
        ARs = []

        # if a new profile is created automatically,
        # this flag triggers the status message
        new_profile = None

        # The actual submission
        for column in columns:
            if form_parts:
                parts = form_parts[str(column)]
            else:
                parts = []
            formkey = "ar.%s" % column
            values = form[formkey].copy()

            # resolved values is formatted as acceptable by archetypes
            # widget machines
            resolved_values = {}
            for k, v in values.items():
                # Analyses, we handle that specially.
                if k == 'Analyses':
                    continue

                if "%s_uid" % k in values:
                    v = values["%s_uid" % k]
                    if v and "," in v:
                        v = v.split(",")
                    resolved_values[k] = values["%s_uid" % k]
                else:
                    resolved_values[k] = values[k]

            client = uc(UID=values['Client_uid'])[0].getObject()
            if values.get('Sample_uid', ''):
                # Secondary AR
                sample = uc(UID=values['Sample_uid'])[0].getObject()
            else:
                # Primary AR
                sample = _createObjectByType("Sample", client, tmpID())
                saved_form = self.request.form
                self.request.form = resolved_values
                sample.setSampleType(resolved_values['SampleType'])
                if 'SamplePoint' in resolved_values:
                    sample.setSamplePoint(resolved_values['SamplePoint'])
                if 'StorageLocation' in resolved_values:
                    sample.setStorageLocation(
                                resolved_values['StorageLocation'])
                sample.processForm()
                self.request.form = saved_form
                if SamplingWorkflowEnabled:
                    wftool.doActionFor(sample, 'sampling_workflow')
                else:
                    wftool.doActionFor(sample, 'no_sampling_workflow')
                    # Object has been renamed
                sample.edit(SampleID=sample.getId())

            resolved_values['Sample'] = sample
            resolved_values['Sample_uid'] = sample.UID()

            # Selecting a template sets the hidden 'parts' field to template values.
            # Selecting a profile will allow ar_add.js to fill in the parts field.
            # The result is the same once we are here.
            if not parts:
                parts = [{'services': [],
                          'container': [],
                          'preservation': '',
                          'separate': False}]

            # Apply DefaultContainerType to partitions without a container
            d_clist = []
            D_UID = values.get("DefaultContainerType_uid", None)
            if D_UID:
                d_clist = [c.UID for c in bsc(portal_type='Container')
                           if c.getObject().getContainerType().UID() == D_UID]
                for i in range(len(parts)):
                    if not parts[i].get('container', []):
                        parts[i]['container'] = d_clist

            # create the AR
            Analyses = values["Analyses"]

            specs = {}
            if len(values.get("min", [])):
                for i, service_uid in enumerate(Analyses):
                    specs[service_uid] = {
                        "min": values["min"][i],
                        "max": values["max"][i],
                        "error": values["error"][i]
                    }

            saved_form = self.request.form
            self.request.form = resolved_values
            ar = _createObjectByType("AnalysisRequest", client, tmpID())
            ar.setSample(sample)
            ar.processForm()
            self.request.form = saved_form
            # Object has been renamed
            ar.edit(RequestID=ar.getId())

            # Create sample partitions
            parts_and_services = {}
            for _i in range(len(parts)):
                p = parts[_i]
                part_prefix = sample.getId() + "-P"
                if '%s%s' % (part_prefix, _i + 1) in sample.objectIds():
                    parts[_i]['object'] = sample['%s%s' % (part_prefix, _i + 1)]
                    parts_and_services['%s%s' % (part_prefix, _i + 1)] = p['services']
                else:
                    part = _createObjectByType("SamplePartition", sample, tmpID())
                    parts[_i]['object'] = part
                    # Sort available containers by capacity and select the
                    # smallest one possible.
                    if p.get('container', ''):
                        containers = [_p.getObject() for _p in bsc(UID=p['container'])]
                        if containers:
                            try:
                                containers.sort(lambda a, b: cmp(
                                    a.getCapacity()
                                    and mg(float(a.getCapacity().lower().split(" ", 1)[0]),
                                           a.getCapacity().lower().split(" ", 1)[1])
                                    or mg(0, 'ml'),
                                    b.getCapacity()
                                    and mg(float(b.getCapacity().lower().split(" ", 1)[0]),
                                           b.getCapacity().lower().split(" ", 1)[1])
                                    or mg(0, 'ml')
                                ))
                            except:
                                pass
                            container = containers[0]
                        else:
                            container = None
                    else:
                        container = None

                    # If container is pre-preserved, set the part's preservation,
                    # and flag the partition to be transitioned below.
                    if container \
                        and container.getPrePreserved() \
                        and container.getPreservation():
                        preservation = container.getPreservation().UID()
                        parts[_i]['prepreserved'] = True
                    else:
                        preservation = p.get('preservation', '')
                        parts[_i]['prepreserved'] = False

                    part.edit(
                        Container=container,
                        Preservation=preservation,
                    )
                    part.processForm()
                    if SamplingWorkflowEnabled:
                        wftool.doActionFor(part, 'sampling_workflow')
                    else:
                        wftool.doActionFor(part, 'no_sampling_workflow')
                    parts_and_services[part.id] = p['services']

            if SamplingWorkflowEnabled:
                wftool.doActionFor(ar, 'sampling_workflow')
            else:
                wftool.doActionFor(ar, 'no_sampling_workflow')

            ARs.append(ar.getId())

            new_analyses = ar.setAnalyses(Analyses, prices=prices, specs=specs)
            ar_analyses = ar.objectValues('Analysis')

            # Add analyses to sample partitions
            for part in sample.objectValues("SamplePartition"):
                part_services = parts_and_services[part.id]
                analyses = [a for a in new_analyses
                            if a.getServiceUID() in part_services]
                if analyses:
                    part.edit(
                        Analyses=analyses,
                    )
                    for analysis in analyses:
                        analysis.setSamplePartition(part)

            # If Preservation is required for some partitions,
            # and the SamplingWorkflow is disabled, we need
            # to transition to to_be_preserved manually.
            if not SamplingWorkflowEnabled:
                to_be_preserved = []
                sample_due = []
                lowest_state = 'sample_due'
                for p in sample.objectValues('SamplePartition'):
                    if p.getPreservation():
                        lowest_state = 'to_be_preserved'
                        to_be_preserved.append(p)
                    else:
                        sample_due.append(p)
                for p in to_be_preserved:
                    doActionFor(p, 'to_be_preserved')
                for p in sample_due:
                    doActionFor(p, 'sample_due')
                doActionFor(sample, lowest_state)
                doActionFor(ar, lowest_state)

            # receive secondary AR
            if values.get('Sample_uid', ''):

                doActionFor(ar, 'sampled')
                doActionFor(ar, 'sample_due')
                not_receive = ['to_be_sampled', 'sample_due', 'sampled',
                               'to_be_preserved']
                sample_state = wftool.getInfoFor(sample, 'review_state')
                if sample_state not in not_receive:
                    doActionFor(ar, 'receive')
                for analysis in ar.getAnalyses(full_objects=1):
                    doActionFor(analysis, 'sampled')
                    doActionFor(analysis, 'sample_due')
                    if sample_state not in not_receive:
                        doActionFor(analysis, 'receive')

            # Transition pre-preserved partitions.
            for p in parts:
                if 'prepreserved' in p and p['prepreserved']:
                    part = p['object']
                    state = wftool.getInfoFor(part, 'review_state')
                    if state == 'to_be_preserved':
                        wftool.doActionFor(part, 'preserve')

        if len(ARs) > 1:
            message = _("Analysis requests ${ARs} were successfully created.",
                        mapping={'ARs': ', '.join(ARs)})
        else:
            message = _("Analysis request ${AR} was successfully created.",
                        mapping={'AR': ARs[0]})

        self.context.plone_utils.addPortalMessage(message, 'info')

        # automatic label printing
        # won't print labels for Register on Secondary ARs
        new_ars = None
        if came_from == 'add':
            new_ars = [ar for ar in ARs if ar[-2:] == '01']
        if 'register' in self.context.bika_setup.getAutoPrintLabels() and new_ars:
            return json.dumps({'success': message,
                               'labels': new_ars,
                               'labelsize': self.context.bika_setup.getAutoLabelSize()})
        else:
            return json.dumps({'success': message})
