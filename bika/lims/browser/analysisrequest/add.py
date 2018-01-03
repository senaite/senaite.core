# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import datetime
import json
import traceback
from datetime import date

import plone
from Products.Archetypes import PloneMessageFactory as PMF
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.taskqueue.interfaces import ITaskQueue
from plone.app.layout.globals.interfaces import IViewView
from zope.component import getAdapter
from zope.component import queryUtility
from zope.interface import implements

from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.browser import BrowserView
from bika.lims.browser.analysisrequest import AnalysisRequestViewView
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.content.analysisrequest import schema as AnalysisRequestSchema
from bika.lims.controlpanel.bika_analysisservices import \
    AnalysisServicesView as ASV
from bika.lims.interfaces import IAnalysisRequestAddView
from bika.lims.utils import t


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
        self.show_workflow_action_buttons = False

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
            # The parent folder can be a client or a batch, but we need the
            # client.  It is possible that this will be None!  This happens
            # when the AR is inside a batch, and the batch has no Client set.
            client = ''
            if not self.context.aq_parent.portal_type == "AnalysisRequestsFolder":
                client = self.context.aq_parent if self.context.aq_parent.portal_type == 'Client'\
                    else self.context.aq_parent.getClient()
            # TODO: Forcing the sort_on value. We should find a better way,
            # this is just a quick fix.
            self.contentFilter['sort_on'] = 'title'
            items = super(AnalysisServicesView, self).folderitems()
            for x, item in enumerate(items):
                if 'obj' not in items[x]:
                    continue
                obj = items[x]['obj']
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
        self.analysisrequest_catalog =\
            getToolByName(self.context, CATALOG_ANALYSIS_REQUEST_LISTING)
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
            return json.dumps(specs)
        uids = copy_from.split(",")
        proxies = self.analysisrequest_catalog(UID=uids)
        if not proxies:
            logger.warning(
                'No object found for UIDs {0} while copying specs'
                .format(copy_from))
            return json.dumps(specs)
        n = 0
        for proxie in proxies:
            res_range = proxie.getObject().getResultsRange()
            new_rr = []
            for i, rr in enumerate(res_range):
                s_uid = self.bika_setup_catalog(
                    portal_type='AnalysisService',
                    getKeyword=rr['keyword'])[0].UID
                rr['uid'] = s_uid
                new_rr.append(rr)
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
            visibility_guard = True
            # visibility_guard is a widget field defined in the schema in order to know the visibility of the widget when the field is related to a dynamically changing content such as workflows. For instance those fields related to the workflow will be displayed only if the workflow is enabled, otherwise they should not be shown.
            if 'visibility_guard' in dir(field.widget):
                visibility_guard = eval(field.widget.visibility_guard)
            if v == visibility and visibility_guard:
                fields.append(field)
        return fields

    def services_widget_content(self, poc, ar_count=None):

        """Return a table displaying services to be selected for inclusion
        in a new AR.  Used in add_by_row view popup, and add_by_col add view.

        :param ar_count: number of AR columns to generate columns for.
        :returns: string: rendered HTML content of bika_listing_table.pt.
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
                    # TODO Parsing with hardcoded date format is not good. Replace it with global format.
                    # We do it now because of parsing format in line 433.
                    fieldvalue = fieldvalue.strftime("%Y-%m-%d")
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


class AbstractAnalysisRequestSubmit():

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.valid_states = {}
        # Errors are aggregated here, and returned together to the browser
        self.errors = {}

    def __call__(self):
        self.validate_form()
        if self.errors:
            return json.dumps({'errors': self.errors})

        return self.process_form()

    def validate_form(self):
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
        self.valid_states = {}
        for arnum, state in nonblank_states.items():
            secondary = False
            # Secondary ARs are a special case, these fields are not required
            if state.get('Sample', ''):
                if 'SamplingDate' in required:
                    required.remove('SamplingDate')
                if 'SampleType' in required:
                    required.remove('SampleType')
                secondary = True
            # If this is not a Secondary AR, make sure that Sample Type UID is valid. This shouldn't
            # happen, but making sure just in case.
            else:
                st_uid = state.get('SampleType', None)
                if not st_uid or not bsc(portal_type='SampleType', UID=st_uid):
                    msg = t(_("Not a valid Sample Type."))
                    ajax_form_error(self.errors, arnum=arnum, message=msg)
                    continue
            # checking if sampling date is not future
            if state.get('SamplingDate', ''):
                samplingdate = state.get('SamplingDate', '')
                try:
                    samp_date = datetime.datetime.strptime(
                        samplingdate.strip(), "%Y-%m-%d %H:%M")
                except ValueError:
                    print traceback.format_exc()
                    msg = \
                        "Bad time formatting: Getting '{}' but expecting an" \
                        " string with '%Y-%m-%d %H:%M' format." \
                            .format(samplingdate)
                    ajax_form_error(self.errors, arnum=arnum, message=msg)
                    continue
                today = date.today()
                if not secondary and today > samp_date.date():
                    msg = t(_("Expected Sampling Date can't be in the past"))
                    ajax_form_error(self.errors, arnum=arnum, message=msg)
                    continue
            # If Sampling Date is not set, we are checking whether it is the user left it empty,
            # or it is because we have Sampling Workflow Disabled
            elif not self.context.bika_setup.getSamplingWorkflowEnabled():
                # Date Sampled is required in this case
                date_sampled = state.get('DateSampled', '')
                if not date_sampled:
                    msg = \
                        "Date Sampled Field is required."
                    ajax_form_error(self.errors, arnum=arnum, message=msg)
                    continue
                try:
                    date_sampled = datetime.datetime.strptime(
                        date_sampled.strip(), "%Y-%m-%d %H:%M")
                except ValueError:
                    print traceback.format_exc()
                    msg = \
                        "Bad time formatting: Getting '{}' but expecting an" \
                        " string with '%Y-%m-%d %H:%M' format." \
                            .format(date_sampled)
                    ajax_form_error(self.errors, arnum=arnum, message=msg)
                    continue
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
            self.valid_states[arnum] = state

        # - Expand lists of UIDs returned by multiValued reference widgets
        # - Transfer _uid values into their respective fields
        for arnum in self.valid_states.keys():
            for field, value in self.valid_states[arnum].items():
                if field.endswith('_uid') and ',' in value:
                    self.valid_states[arnum][field] = value.split(',')
                elif field.endswith('_uid'):
                    self.valid_states[arnum][field] = value

    def process_form(self):
        # To be implemented by child classes
        pass


class AnalysisRequestSubmit(AbstractAnalysisRequestSubmit):
    """Handle data submitted from analysisrequest add forms.  As much
    as possible, the incoming json arrays should already match the requirement
    of the underlying AR/sample schema.
    """

    def process_form(self):
        # Now, we will create the specified ARs.
        portal_catalog = getToolByName(self.context, 'portal_catalog')
        ARs = []
        new_ar_uids = []
        from bika.lims.utils.analysisrequest import \
            create_analysisrequest as crar
        for arnum, state in self.valid_states.items():
            # Create the Analysis Request
            ar = crar(
                portal_catalog(UID=state['Client'])[0].getObject(),
                self.request,
                state
            )
            ARs.append(ar.Title())
            # Automatic label printing won't print "register" labels for
            # Secondary ARs
            if ar.Title()[-2:] == '01':
                new_ar_uids.append(ar.UID())

        # Display the appropriate message after creation
        if len(ARs) > 1:
            message = _('Analysis requests ${ARs} were successfully created.',
                        mapping={'ARs': safe_unicode(', '.join(ARs))})
        else:
            message = _('Analysis request ${AR} was successfully created.',
                        mapping={'AR': safe_unicode(ARs[0])})
        self.context.plone_utils.addPortalMessage(message, 'info')

        if new_ar_uids and 'register'\
                in self.context.bika_setup.getAutoPrintStickers():
            return json.dumps({
                'success': message,
                'stickers': new_ar_uids,
                'stickertemplate': self.context.bika_setup.getAutoStickerTemplate()
            })
        else:
            return json.dumps({'success': message})


class AsyncAnalysisRequestSubmit(AnalysisRequestSubmit):

    def process_form(self):

        # We want to first know the total number of analyses to be created
        num_analyses = 0
        uids_arr = [ar.get('Analyses', []) for ar in self.valid_states.values()]
        for arr in uids_arr:
            num_analyses += len(arr)

        if num_analyses < 50:
            # Do not process asynchronously
            return AnalysisRequestSubmit.process_form(self)

        # Only load asynchronously if queue ar-create is available
        task_queue = queryUtility(ITaskQueue, name='ar-create')
        if task_queue is None:
            # ar-create queue not registered. Proceed synchronously
            logger.info("SYNC: total = %s" % num_analyses)
            return AnalysisRequestSubmit.process_form(self)
        else:
            # ar-create queue registered, create asynchronously
            logger.info("[A]SYNC: total = %s" % num_analyses)
            path = self.request.PATH_INFO
            path = path.replace('_submit_async', '_submit')
            task_queue.add(path, method='POST')
            msg = _('One job added to the Analysis Request creation queue')
            self.context.plone_utils.addPortalMessage(msg, 'info')
            return json.dumps({'success': 'With taskqueue'})
