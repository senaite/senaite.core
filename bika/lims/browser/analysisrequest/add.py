import json
from bika.lims.utils.sample import create_sample
from bika.lims.utils.samplepartition import create_samplepartition
from bika.lims.workflow import doActionFor
import plone

from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.browser import BrowserView
from bika.lims.browser.analysisrequest import AnalysisRequestViewView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.content.analysisrequest import schema as AnalysisRequestSchema
from bika.lims.controlpanel.bika_analysisservices import \
    AnalysisServicesView as ASV
from bika.lims.interfaces import IAnalysisRequestAddView, ISample
from bika.lims.utils import getHiddenAttributesForClass, dicts_to_dict
from bika.lims.utils import t
from bika.lims.utils import tmpID
from bika.lims.utils.analysisrequest import create_analysisrequest
from magnitude import mg
from plone.app.layout.globals.interfaces import IViewView
from Products.Archetypes import PloneMessageFactory as PMF
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

    def __init__(self, context, request, poc, ar_count=None, category=None):
        super(AnalysisServicesView, self).__init__(context, request)

        self.contentFilter['getPointOfCapture'] = poc
        self.contentFilter['inactive_state'] = 'active'

        if category:
            self.contentFilter['getCategoryTitle'] = category

        self.cat_header_class = "ignore_bikalisting_default_handler"

        ar_count_default = ar_count if ar_count else 4
        try:
            self.ar_count = int(self.request.get('ar_count', ar_count_default))
        except ValueError:
            self.ar_count = ar_count_default

        self.ar_add_items = []

        # Customise form for AR Add context
        self.form_id = poc

        self.filter_indexes = ['id', 'Title', 'SearchableText', 'getKeyword']

        self.pagesize = 999999
        self.table_only = True

        default = [x for x in self.review_states if x['id'] == 'default'][0]
        columns = default['columns']

        self.review_states = [
            {'id': 'default',
             'title': _('All'),
             'contentFilter': {},
             'columns': columns,
            },
        ]

        self.review_states[0]['custom_actions'] = []
        self.review_states[0]['transitions'] = []

        # Configure column layout
        to_remove = ['Category', 'Instrument', 'Unit',
                     'Calculation', 'Keyword', 'Price']
        for col_name in to_remove:
            if col_name in self.review_states[0]['columns']:
                self.review_states[0]['columns'].remove(col_name)

        # Add columns for each AR
        for arnum in range(self.ar_count):
            column = {
                'title': _('AR ${ar_number}', mapping={'ar_number': arnum}),
                'sortable': False,
                'type': 'boolean',
            }

            self.columns['ar.%s' % arnum] = column
            self.review_states[0]['columns'].append('ar.%s' % arnum)

        # Removing sortable from services - it fails to respect table_only,
        # and re-renders main-template inside the container!
        for k, v in self.columns.items():
            self.columns[k]['sortable'] = False

        # results cached in ar_add_items
        self.folderitems()

    def selected_cats(self, items):
        """This AnalysisServicesView extends the default selected_cats,
        in order to include auto_expand categories as defined by
        client.getDefaultCategories()

        :param items: The original selected_cats calculates visibility
            by looking at items in the current listing batch.
        """
        cats = super(AnalysisServicesView, self).selected_cats(items)
        client = self.context.getClient()
        if client:
            cats.extend([c.Title() for c in client.getDefaultCategories()])
        return cats

    def restricted_cats(self, items):
        """This AnalysisServicesView extends the default restricted_cats,
        in order to include those listed in client.getRestrictedCategories
        """
        cats = super(AnalysisServicesView, self).restricted_cats(items)
        client = self.context.getClient()
        if client:
            cats.extend([c.Title() for c in client.getRestrictedCategories()])
        return cats

    def folderitems(self):
        # This folderitems acts slightly differently from others, in that it
        # saves it's results in an attribute, and prevents itself from being
        # run multiple times.  This is necessary so that AR Add can check
        # the item count before choosing to render the table at all.
        if not self.ar_add_items:
            bs = self.context.bika_setup
            # The parent folder can be a client or a batch, but we need the
            # client.  It is possible that this will be None!  This happens
            # when the AR is inside a batch, and the batch has no Client set.
            client = self.context.aq_parent if self.context.aq_parent.portal_type == 'Client'\
                else self.context.aq_parent.getClient()
            items = super(AnalysisServicesView, self).folderitems()
            for x, item in enumerate(items):
                if 'obj' not in items[x]:
                    continue
                obj = items[x]['obj']
                kw = obj.getKeyword()
                for arnum in range(self.ar_count):
                    key = 'ar.%s' % arnum
                    # If AR Specification fields are enabled, these should
                    # not be allowed to wrap inside the cell:
                    items[x]['class'][key] = 'nowrap'
                    # checked or not:
                    selected = self._get_selected_items(form_key=key)
                    items[x][key] = item in selected
                    # always editable:
                    items[x]['allow_edit'].append(key)
                    # fields and controls after each checkbox
                    items[x]['after'][key] = ''
                    if self.context.bika_setup.getEnableARSpecs():
                        items[x]['after'][key] += '''
                            <input class="min" size="3" placeholder="&gt;min"/>
                            <input class="max" size="3" placeholder="&lt;max"/>
                            <input class="error" size="3" placeholder="err%"/>
                        '''
                    items[x]['after'][key] += '<span class="partnr"></span>'

                    # Price and VAT percentage are cheats: There is code in
                    # bika_listing_table_items.pt which allows them to be
                    # inserted into as attributes on <TR>.  TAL has this flaw;
                    # that attributes cannot be dynamically inserted.
                    # XXX five.zpt should fix this.  we must test five.zpt!
                    items[x]['price'] = obj.getBulkPrice() \
                        if client and client.getBulkDiscount() \
                        else obj.getPrice()
                    items[x]['vat_percentage'] = obj.getVAT()

                    # place a clue for the JS to recognize that these are
                    # AnalysisServices being selected here (service_selector
                    # bika_listing):
                    # XXX five.zpt should fix this.  we must test five.zpt!
                    poc = items[x]['obj'].getPointOfCapture()
                    items[x]['table_row_class'] = \
                        'service_selector bika_listing ' + poc
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
        self.layout = "columns"
        self.ar_count = self.request.get('ar_count', 4)
        try:
            self.ar_count = int(self.ar_count)
        except:
            self.ar_count = 4

    def __call__(self):
        self.request.set('disable_border', 1)
        self.ShowPrices = self.context.bika_setup.getShowPrices()
        if 'ajax_category_expand' in self.request.keys():
            cat = self.request.get('cat')
            asv = AnalysisServicesView(self.context,
                                        self.request,
                                        self.request['form_id'],
                                        category=cat,
                                        ar_count=self.ar_count)
            return asv()
        else:
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

        :param ar_count: number of AR columns to generate columns for.
        :return: string: rendered HTML content of bika_listing_table.pt.
            If no items are found, returns "".
        """

        if not ar_count:
            ar_count = self.ar_count

        s = AnalysisServicesView(self.context, self.request, poc,
                                 ar_count=ar_count)
        s.form_id = poc
        s.folderitems()

        if not s.ar_add_items:
            return ''
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
                     if f.widget.isVisible(self.context, 'secondary') == 'disabled']
        ret = []
        for fieldname in ar_fields:
            if fieldname in sample_fields:
                fieldvalue = sample_fields[fieldname].getAccessor(sample)()
                if fieldvalue is None:
                    fieldvalue = ''
                if hasattr(fieldvalue, 'Title'):
                    # Must store UID for referencefields.
                    ret.append([fieldname + '_uid', fieldvalue.UID()])
                    fieldvalue = fieldvalue.Title()
                if hasattr(fieldvalue, 'year'):
                    fieldvalue = fieldvalue.strftime(self.date_format_short)
            else:
                fieldvalue = ''
            ret.append([fieldname, fieldvalue])
        return json.dumps(ret)

def ajax_form_error(errors, field=None, arnum=None, message=None):
    if not message:
        message = t(PMF('Input is required but no input given.'))
    if (arnum or field):
        error_key = ' %s.%s' % (int(arnum) + 1, field or '')
    else:
        error_key = 'Form Error'
    errors[error_key] = message

class ajaxAnalysisRequestSubmit():
    """Handle data submitted from analysisrequest add forms.  As much
    as possible, the incoming json arrays should already match the requirement
    of the underlying AR/sample schema.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        # Errors are aggregated here, and returned together to the browser
        self.errors = {}

    def __call__(self):
        form = self.request.form
        plone.protect.CheckAuthenticator(self.request.form)
        plone.protect.PostOnly(self.request.form)
        uc = getToolByName(self.context, 'uid_catalog')
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        portal_catalog = getToolByName(self.context, 'portal_catalog')

        # Load the form data from request.state.  If anything goes wrong here,
        # put a bullet through the whole process.
        try:
            states = json.loads(form['state'])
        except Exception as e:
            message = t(_('Badly formed state: ${errmsg}',
                          mapping={'errmsg': e.message}))
            ajax_form_error(self.errors, message=message)
            return json.dumps({'errors': self.errors})

        # Validate incoming form data
        required = [field.getName() for field
                    in AnalysisRequestSchema.fields()
                    if field.required] + ["Analyses"]

        # First remove all states which are completely empty; if all
        # required fields are not present, we assume that the current
        # AR had no data entered, and can be ignored
        nonblank_states = {}
        for arnum, state in states.items():
            for key, val in state.items():
                if val \
                        and "%s_hidden" % key not in state \
                        and not key.endswith('hidden'):
                    nonblank_states[arnum] = state
                    break

        # in valid_states, all ars that pass validation will be stored
        valid_states = {}
        for arnum, state in nonblank_states.items():
            # Secondary ARs are a special case, these fields are not required
            if state.get('Sample', ''):
                if 'SamplingDate' in required:
                    required.remove('SamplingDate')
                if 'SampleType' in required:
                    required.remove('SampleType')
            # fields flagged as 'hidden' are not considered required because
            # they will already have default values inserted in them
            for fieldname in required:
                if fieldname + '_hidden' in state:
                    required.remove(fieldname)
            missing = [f for f in required if not state.get(f, '')]
            # If there are required fields missing, flag an error
            if missing:
                msg = t(_('Required fields have no values: '
                          '${field_names}',
                          mapping={'field_names': ', '.join(missing)}))
                ajax_form_error(self.errors, arnum=arnum, message=msg)
                continue
            # This ar is valid!
            valid_states[arnum] = state

        # - Expand lists of UIDs returned by multiValued reference widgets
        # - Transfer _uid values into their respective fields
        for arnum in valid_states.keys():
            for field, value in valid_states[arnum].items():
                if field.endswith('_uid') and ',' in value:
                    valid_states[arnum][field] = value.split(',')
                elif field.endswith('_uid'):
                    valid_states[arnum][field] = value

        if self.errors:
            return json.dumps({'errors': self.errors})

        # Now, we will create the specified ARs.
        ARs = []
        for arnum, state in valid_states.items():
            # Create the Analysis Request
            ar = create_analysisrequest(
                portal_catalog(UID=state['Client'])[0].getObject(),
                self.request,
                state
            )
            ARs.append(ar.Title())

        # Display the appropriate message after creation
        if len(ARs) > 1:
            message = _('Analysis requests ${ARs} were successfully created.',
                        mapping={'ARs': safe_unicode(', '.join(ARs))})
        else:
            message = _('Analysis request ${AR} was successfully created.',
                        mapping={'AR': safe_unicode(ARs[0])})
        self.context.plone_utils.addPortalMessage(message, 'info')
        # Automatic label printing won't print "register" labels for Secondary. ARs
        new_ars = [ar for ar in ARs if ar[-2:] == '01']
        if 'register' in self.context.bika_setup.getAutoPrintStickers() \
                and new_ars:
            return json.dumps({
                'success': message,
                'stickers': new_ars,
                'stickertemplate': self.context.bika_setup.getAutoStickerTemplate()
            })
        else:
            return json.dumps({'success': message})



def create_analysisrequest(context, request, values):
    """Create an AR.

    :param context the container in which the AR will be created (Client)
    :param request the request object
    :param values a dictionary containing fieldname/value pairs, which
           will be applied.  Some fields will have specific code to handle them,
           and others will be directly written to the schema.
    :return the new AR instance

    Special keys present (or required) in the values dict, which are not present
    in the schema:

        - Partitions: data about partitions to be created, and the
                      analyses that are to be assigned to each.

        - Prices: custom prices set in the HTML form.

        - ResultsRange: Specification values entered in the HTML form.

    """
    # Gather neccesary tools
    workflow = getToolByName(context, 'portal_workflow')
    bc = getToolByName(context, 'bika_catalog')

    # Create new sample or locate the existing for secondary AR
    sample = False
    if values['Sample']:
        if ISample.providedBy(values['Sample']):
            secondary = True
            sample = values['Sample']
            samplingworkflow_enabled = sample.getSamplingWorkflowEnabled()
        else:
            brains = bc(UID=values['Sample'])
            if brains:
                secondary = True
                sample = brains[0].getObject()
                samplingworkflow_enabled = sample.getSamplingWorkflowEnabled()
    if not sample:
        secondary = False
        sample = create_sample(context, request, values)
        samplingworkflow_enabled = context.bika_setup.getSamplingWorkflowEnabled()

    # Create the Analysis Request
    ar = _createObjectByType('AnalysisRequest', context, tmpID())
    ar.setSample(sample)

    # processform renames the sample, this requires values to contain the Sample.
    values['Sample'] = sample
    ar.processForm(REQUEST=request, values=values)

    # Object has been renamed
    ar.edit(RequestID=ar.getId())

    # Set initial AR state
    workflow_action = 'sampling_workflow' if samplingworkflow_enabled \
        else 'no_sampling_workflow'
    workflow.doActionFor(ar, workflow_action)


    # We need to send a list of service UIDS to setAnalyses function.
    # But we may have received a list of titles, list of UIDS,
    # list of keywords or list of service objects!
    service_uids = []
    for obj in values['Analyses']:
        uid = False
        # service objects
        if hasattr(obj, 'portal_type') and obj.portal_type == 'AnalysisService':
            uid = obj.UID()
        # Analysis objects (shortcut for eg copying analyses from other AR)
        elif hasattr(obj, 'portal_type') and obj.portal_type == 'Analysis':
            uid = obj.getService()
        # Maybe already UIDs.
        if not uid:
            bsc = getToolByName(context, 'bika_setup_catalog')
            brains = bsc(portal_type='AnalysisService', UID=obj)
            if brains:
                uid = brains[0].UID
        # Maybe already UIDs.
        if not uid:
            bsc = getToolByName(context, 'bika_setup_catalog')
            brains = bsc(portal_type='AnalysisService', title=obj)
            if brains:
                uid = brains[0].UID
        if uid:
            service_uids.append(uid)
        else:
            logger.info("In analysisrequest.add.create_analysisrequest: cannot "
                        "find uid of this service: %s" % obj)

    # Set analysis request analyses
    ar.setAnalyses(service_uids,
                   prices=values.get("Prices", []),
                   specs=values.get('ResultsRange', []))
    analyses = ar.getAnalyses(full_objects=True)

    skip_receive = ['to_be_sampled', 'sample_due', 'sampled', 'to_be_preserved']
    if secondary:
        # Only 'sample_due' and 'sample_recieved' samples can be selected
        # for secondary analyses
        doActionFor(ar, 'sampled')
        doActionFor(ar, 'sample_due')
        sample_state = workflow.getInfoFor(sample, 'review_state')
        if sample_state not in skip_receive:
            doActionFor(ar, 'receive')

    for analysis in analyses:
        doActionFor(analysis, 'sample_due')
        analysis_state = workflow.getInfoFor(analysis, 'review_state')
        if analysis_state not in skip_receive:
            doActionFor(analysis, 'receive')

    if not secondary:
        # Create sample partitions
        partitions = []
        for n, partition in enumerate(values['Partitions']):
            # Calculate partition id
            partition_prefix = sample.getId() + "-P"
            partition_id = '%s%s' % (partition_prefix, n + 1)
            partition['part_id'] = partition_id
            # Point to or create sample partition
            if partition_id in sample.objectIds():
                partition['object'] = sample[partition_id]
            else:
                partition['object'] = create_samplepartition(
                    sample,
                    partition
                )
            # now assign analyses to this partition.
            obj = partition['object']
            for analysis in analyses:
                if analysis.getService().UID() in partition['services']:
                    analysis.setSamplePartition(obj)

            partitions.append(partition)

        # If Preservation is required for some partitions,
        # and the SamplingWorkflow is disabled, we need
        # to transition to to_be_preserved manually.
        if not samplingworkflow_enabled:
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

        # Transition pre-preserved partitions
        for p in partitions:
            if 'prepreserved' in p and p['prepreserved']:
                part = p['object']
                state = workflow.getInfoFor(part, 'review_state')
                if state == 'to_be_preserved':
                    workflow.doActionFor(part, 'preserve')

    # Return the newly created Analysis Request
    return ar
