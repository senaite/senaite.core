# coding=utf-8
from AccessControl import getSecurityManager
from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t, dicts_to_dict
from bika.lims.utils.analysis import format_uncertainty
from bika.lims.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import QCANALYSIS_TYPES
from bika.lims.interfaces import IResultOutOfRange
from bika.lims.permissions import *
from bika.lims.utils import isActive
from bika.lims.utils import getUsers
from bika.lims.utils import to_utf8
from DateTime import DateTime
from operator import itemgetter
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.utils.analysis import format_numeric_result
from zope.interface import implements
from zope.interface import Interface
from zope.component import getAdapters

import json



class AnalysesView(BikaListingView):
    """ Displays a list of Analyses in a table.
        Visible InterimFields from all analyses are added to self.columns[].
        Keyword arguments are passed directly to bika_analysis_catalog.
    """

    def __init__(self, context, request, **kwargs):
        self.catalog = "bika_analysis_catalog"
        self.contentFilter = dict(kwargs)
        self.contentFilter['portal_type'] = 'Analysis'
        self.contentFilter['sort_on'] = 'sortable_title'
        self.context_actions = {}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.show_column_toggles = False
        self.pagesize = 0
        self.form_id = 'analyses_form'

        self.portal = getToolByName(context, 'portal_url').getPortalObject()
        self.portal_url = self.portal.absolute_url()

        request.set('disable_plone.rightcolumn', 1);

        # each editable item needs it's own allow_edit
        # which is a list of field names.
        self.allow_edit = False

        self.columns = {
            'Service': {
                'title': _('Analysis'),
                'sortable': False},
            'Partition': {
                'title': _("Partition"),
                'sortable':False},
            'Method': {
                'title': _('Method'),
                'sortable': False,
                'toggle': True},
            'Instrument': {
                'title': _('Instrument'),
                'sortable': False,
                'toggle': True},
            'Analyst': {
                'title': _('Analyst'),
                'sortable': False,
                'toggle': True},
            'state_title': {
                'title': _('Status'),
                'sortable': False},
            'Result': {
                'title': _('Result'),
                'input_width': '6',
                'input_class': 'ajax_calculate numeric',
                'sortable': False},
            'Specification': {
                'title': _('Specification'),
                'sortable': False},
            'ResultDM': {
                'title': _('Dry'),
                'sortable': False},
            'Uncertainty': {
                'title': _('+-'),
                'sortable': False},
            'retested': {
                'title': "<img title='%s' src='%s/++resource++bika.lims.images/retested.png'/>"%\
                    (t(_('Retested')), self.portal_url),
                'type':'boolean',
                'sortable': False},
            'Attachments': {
                'title': _('Attachments'),
                'sortable': False},
            'CaptureDate': {
                'title': _('Captured'),
                'index': 'getResultCaptureDate',
                'sortable':False},
            'DueDate': {
                'title': _('Due Date'),
                'index': 'getDueDate',
                'sortable':False},
        }

        self.review_states = [
            {'id': 'default',
             'title':  _('All'),
             'contentFilter': {},
             'columns': ['Service',
                         'Partition',
                         'Result',
                         'Specification',
                         'Method',
                         'Instrument',
                         'Analyst',
                         'Uncertainty',
                         'CaptureDate',
                         'DueDate',
                         'state_title']
             },
        ]
        if not context.bika_setup.getShowPartitions():
            self.review_states[0]['columns'].remove('Partition')

        super(AnalysesView, self).__init__(context,
                                           request,
                                           show_categories=context.bika_setup.getCategoriseAnalysisServices(),
                                           expand_all_categories=True)

    def get_analysis_spec(self, analysis):
        keyword = analysis.getService().getKeyword()
        uid = analysis.UID()
        if hasattr(analysis.aq_parent, 'getResultsRange'):
            rr = dicts_to_dict(analysis.aq_parent.getResultsRange(), 'keyword')
            return rr.get(analysis.getKeyword(), None)
        if hasattr(analysis.aq_parent, 'getReferenceResults'):
            rr = dicts_to_dict(analysis.aq_parent.getReferenceResults(), 'uid')
            return rr.get(analysis.UID(), None)
        return {'keyword':keyword, 'uid':uid, 'min':'', 'max':'', 'error':''}

    def ResultOutOfRange(self, analysis):
        """ Template wants to know, is this analysis out of range?
        We scan IResultOutOfRange adapters, and return True if any IAnalysis
        adapters trigger a result.
        """
        adapters = getAdapters((analysis, ), IResultOutOfRange)
        spec = self.get_analysis_spec(analysis)
        for name, adapter in adapters:
            if not spec:
                return False
            if adapter(specification=spec):
                return True

    def getAnalysisSpecsStr(self, spec):
        specstr = ''
        if spec['min'] and spec['max']:
            specstr = '%s - %s' % (spec['min'], spec['max'])
        elif spec['min']:
            specstr = '> %s' % spec['min']
        elif spec['max']:
            specstr = '< %s' % spec['max']
        return specstr

    def get_methods_vocabulary(self, analysis = None):
        """ Returns a vocabulary with the methods available for the
            analysis specified.
            If the service has the getInstrumentEntryOfResults(), returns
            the methods available from the instruments capable to perform
            the service, as well as the methods set manually for the
            analysis on its edit view. If getInstrumentEntryOfResults()
            is unset, only the methods assigned manually to that service
            are returned. If the Analysis service method is set to None,
            but have also at least one method available, adds the 'None'
            option to the vocabulary.
            If the analysis is None, retrieves all the
            active methods from the catalog.
        """
        ret = []
        if analysis:
            service = analysis.getService()
            methods = service.getAvailableMethods()
            if methods and not service.getMethod():
                ret.append({'ResultValue': '',
                            'ResultText': _('None')})
            for method in methods:
                ret.append({'ResultValue': method.UID(),
                            'ResultText': method.Title()})
        else:
            # All active methods
            bsc = getToolByName(self.context, 'bika_setup_catalog')
            brains = bsc(portal_type='Method', inactive_state='active')
            for brain in brains:
                ret.append({'ResultValue': brain.UID,
                            'ResultText': brain.title})
        return ret

    def get_instruments_vocabulary(self, analysis = None):
        """ Returns a vocabulary with the instruments available (active,
            not out-of-date, with valid internal calibrations) for
            the analysis specified. If the analysis is None, retrieves
            all the active instruments from the catalog.
            If the instrument is not None and the instrument has a method
            assigned, returns the instruments capable to perform the
            method. If the instrument hasn't any method assigned, returns
            all the instruments available from the service default method.
            If the instrument's Service has the property
            getInstrumentEntryOfResults unset, always returns empty.
            If the analysis is a QC, the invalid instruments not
            out-of-date are also returned.
        """
        ret = []
        instruments = []
        if analysis:
            service = analysis.getService()
            if service.getInstrumentEntryOfResults() == False:
                return []

            method = analysis.getMethod() \
                    if hasattr(analysis, 'getMethod') else None
            instruments = method.getInstruments() if method \
                          else analysis.getService().getInstruments()

        else:
            # All active instruments
            bsc = getToolByName(self.context, 'bika_setup_catalog')
            brains = bsc(portal_type='Instrument', inactive_state='active')
            instruments = [brain.getObject() for brain in brains]

        for ins in instruments:
            if analysis \
                and analysis.portal_type in ['ReferenceAnalysis',
                                             'DuplicateAnalysis'] \
                and not ins.isOutOfDate():
                # Add the 'invalid', but in-date instrument
                ret.append({'ResultValue': ins.UID(),
                            'ResultText': ins.Title()})
            if ins.isValid():
                # Only add the 'valid' instruments: certificate
                # on-date and valid internal calibration tests
                ret.append({'ResultValue': ins.UID(),
                            'ResultText': ins.Title()})

        ret.insert(0, {'ResultValue': '',
                       'ResultText': _('None')});
        return ret

    def getAnalysts(self):
        analysts = getUsers(self.context, ['Manager', 'LabManager', 'Analyst'])
        analysts = analysts.sortedByKey()
        ret = []
        for a in analysts:
            ret.append({'ResultValue': a,
                        'ResultText': analysts.getValue(a)})
        return ret

    def folderitems(self):
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        workflow = getToolByName(self.context, 'portal_workflow')
        mtool = getToolByName(self.context, 'portal_membership')
        checkPermission = mtool.checkPermission
        if not self.allow_edit:
            can_edit_analyses = False
        else:
            if self.contentFilter.get('getPointOfCapture', '') == 'field':
                can_edit_analyses = checkPermission(EditFieldResults, self.context)
            else:
                can_edit_analyses = checkPermission(EditResults, self.context)
            self.allow_edit = can_edit_analyses
        self.show_select_column = self.allow_edit
        context_active = isActive(self.context)

        self.categories = []
        items = super(AnalysesView, self).folderitems(full_objects = True)

        # manually skim retracted analyses from the list
        new_items = []
        for i,item in enumerate(items):
            # self.contentsMethod may return brains or objects.
            if not ('obj' in items[i]):
                continue
            obj = hasattr(items[i]['obj'], 'getObject') and \
                items[i]['obj'].getObject() or \
                items[i]['obj']
            if workflow.getInfoFor(obj, 'review_state') == 'retracted' \
                and not checkPermission(ViewRetractedAnalyses, self.context):
                continue
            new_items.append(item)
        items = new_items

        methods = self.get_methods_vocabulary()

        self.interim_fields = {}
        self.interim_columns = {}
        self.specs = {}
        show_methodinstr_columns = False
        for i, item in enumerate(items):
            # self.contentsMethod may return brains or objects.
            obj = hasattr(items[i]['obj'], 'getObject') and \
                items[i]['obj'].getObject() or \
                items[i]['obj']
            if workflow.getInfoFor(obj, 'review_state') == 'retracted' \
                and not checkPermission(ViewRetractedAnalyses, self.context):
                continue

            result = obj.getResult()
            service = obj.getService()
            calculation = service.getCalculation()
            unit = service.getUnit()
            keyword = service.getKeyword()

            if self.show_categories:
                cat = obj.getService().getCategoryTitle()
                items[i]['category'] = cat
                if cat not in self.categories:
                    self.categories.append(cat)

            # Check for InterimFields attribute on our object,
            interim_fields = hasattr(obj, 'getInterimFields') \
                and obj.getInterimFields() or []
            # kick some pretty display values in.
            for x in range(len(interim_fields)):
                interim_fields[x]['formatted_value'] = \
                    format_numeric_result(obj, interim_fields[x]['value'])
            self.interim_fields[obj.UID()] = interim_fields
            items[i]['service_uid'] = service.UID()
            items[i]['Service'] = service.Title()
            items[i]['Keyword'] = keyword
            items[i]['Unit'] = unit and unit or ''
            items[i]['Result'] = ''
            items[i]['formatted_result'] = ''
            items[i]['interim_fields'] = interim_fields
            items[i]['Remarks'] = obj.getRemarks()
            items[i]['Uncertainty'] = ''
            items[i]['retested'] = obj.getRetested()
            items[i]['class']['retested'] = 'center'
            items[i]['result_captured'] = self.ulocalized_time(
                obj.getResultCaptureDate(), long_format=0)
            items[i]['calculation'] = calculation and True or False
            try:
                items[i]['Partition'] = obj.getSamplePartition().getId()
            except AttributeError:
                items[i]['Partition'] = ''
            if obj.portal_type == "ReferenceAnalysis":
                items[i]['DueDate'] = self.ulocalized_time(obj.aq_parent.getExpiryDate(), long_format=0)
            else:
                items[i]['DueDate'] = self.ulocalized_time(obj.getDueDate(), long_format=1)
            cd = obj.getResultCaptureDate()
            items[i]['CaptureDate'] = cd and self.ulocalized_time(cd, long_format=1) or ''
            items[i]['Attachments'] = ''

            item['allow_edit'] = []
            client_or_lab = ""

            tblrowclass = items[i].get('table_row_class');
            if obj.portal_type == 'ReferenceAnalysis':
                items[i]['st_uid'] = obj.aq_parent.UID()
                items[i]['table_row_class'] = ' '.join([tblrowclass, 'qc-analysis']);
            elif obj.portal_type == 'DuplicateAnalysis' and \
                obj.getAnalysis().portal_type == 'ReferenceAnalysis':
                items[i]['st_uid'] = obj.aq_parent.UID()
                items[i]['table_row_class'] = ' '.join([tblrowclass, 'qc-analysis']);
            else:
                if self.context.portal_type == 'AnalysisRequest':
                    sample = self.context.getSample()
                    st_uid = sample.getSampleType().UID()
                    items[i]['st_uid'] = st_uid
                    if st_uid not in self.specs:
                        proxies = bsc(portal_type = 'AnalysisSpec',
                                      getSampleTypeUID = st_uid)
                elif self.context.portal_type == "Worksheet":
                    if obj.portal_type == "DuplicateAnalysis":
                        sample = obj.getAnalysis().getSample()
                    elif obj.portal_type == "RejectAnalysis":
                        sample = obj.getAnalysis().getSample()
                    else:
                        sample = obj.aq_parent.getSample()
                    st_uid = sample.getSampleType().UID()
                    items[i]['st_uid'] = st_uid
                    if st_uid not in self.specs:
                        proxies = bsc(portal_type = 'AnalysisSpec',
                                      getSampleTypeUID = st_uid)
                elif self.context.portal_type == 'Sample':
                    st_uid = self.context.getSampleType().UID()
                    items[i]['st_uid'] = st_uid
                    if st_uid not in self.specs:
                        proxies = bsc(portal_type = 'AnalysisSpec',
                                      getSampleTypeUID = st_uid)
                else:
                    proxies = []
                if st_uid not in self.specs:
                    for spec in (p.getObject() for p in proxies):
                        if spec.getClientUID() == obj.getClientUID():
                            client_or_lab = 'client'
                        elif spec.getClientUID() == self.context.bika_setup.bika_analysisspecs.UID():
                            client_or_lab = 'lab'
                        else:
                            continue
                        for keyword, results_range in \
                            spec.getResultsRangeDict().items():
                            # hidden form field 'specs' keyed by sampletype uid:
                            # {st_uid: {'lab/client':{keyword:{min,max,error}}}}
                            if st_uid in self.specs:
                                if client_or_lab in self.specs[st_uid]:
                                    self.specs[st_uid][client_or_lab][keyword] = results_range
                                else:
                                    self.specs[st_uid][client_or_lab] = {keyword: results_range}
                            else:
                                self.specs[st_uid] = {client_or_lab: {keyword: results_range}}

            if checkPermission(ManageBika, self.context):
                service_uid = service.UID()
                latest = rc.lookupObject(service_uid).version_id
                items[i]['Service'] = service.Title()
                items[i]['class']['Service'] = "service_title"

            # Show version number of out-of-date objects
            # No: This should be done in another column, if at all.
            # The (vX) value confuses some more fragile forms.
            #     if hasattr(obj, 'reference_versions') and \
            #        service_uid in obj.reference_versions and \
            #        latest != obj.reference_versions[service_uid]:
            #         items[i]['after']['Service'] = "(v%s)" % \
            #              (obj.reference_versions[service_uid])

            # choices defined on Service apply to result fields.
            choices = service.getResultOptions()
            if choices:
                item['choices']['Result'] = choices

            # permission to view this item's results
            can_view_result = \
                getSecurityManager().checkPermission(ViewResults, obj)

            # permission to edit this item's results
            # Editing Field Results is possible while in Sample Due.
            poc = self.contentFilter.get("getPointOfCapture", 'lab')
            can_edit_analysis = self.allow_edit and context_active and \
                ( (poc == 'field' and getSecurityManager().checkPermission(EditFieldResults, obj))
                  or
                  (poc != 'field' and getSecurityManager().checkPermission(EditResults, obj)) )


            allowed_method_states = ['to_be_sampled',
                                     'to_be_preserved',
                                     'sample_received',
                                     'sample_registered',
                                     'sampled',
                                     'assigned']

            # Prevent from being edited if the instrument assigned
            # is not valid (out-of-date or uncalibrated), except if
            # the analysis is a QC with assigned status
            can_edit_analysis = can_edit_analysis \
                and (obj.isInstrumentValid() \
                    or (obj.portal_type == 'ReferenceAnalysis' \
                        and item['review_state'] in allowed_method_states))

            if can_edit_analysis:
                items[i]['allow_edit'].extend(['Analyst',
                                               'Result',
                                               'Remarks'])
                # if the Result field is editable, our interim fields are too
                for f in self.interim_fields[obj.UID()]:
                    items[i]['allow_edit'].append(f['keyword'])

                # if there isn't a calculation then result must be re-testable,
                # and if there are interim fields, they too must be re-testable.
                if not items[i]['calculation'] or \
                   (items[i]['calculation'] and self.interim_fields[obj.UID()]):
                    items[i]['allow_edit'].append('retested')


            # TODO: Only the labmanager must be able to change the method
            # can_set_method = getSecurityManager().checkPermission(SetAnalysisMethod, obj)
            can_set_method = can_edit_analysis \
                and item['review_state'] in allowed_method_states
            method = obj.getMethod() \
                        if hasattr(obj, 'getMethod') and obj.getMethod() \
                        else service.getMethod()

            # Display the methods selector if the AS has at least one
            # method assigned
            item['Method'] = ''
            item['replace']['Method'] = ''
            if can_set_method:
                voc = self.get_methods_vocabulary(obj)
                if voc:
                    # The service has at least one method available
                    item['Method'] = method.UID() if method else ''
                    item['choices']['Method'] = voc
                    item['allow_edit'].append('Method')
                    show_methodinstr_columns = True

                elif method:
                    # This should never happen
                    # The analysis has set a method, but its parent
                    # service hasn't any method available O_o
                    item['Method'] = method.Title()
                    item['replace']['Method'] = "<a href='%s'>%s</a>" % \
                        (method.absolute_url(), method.Title())
                    show_methodinstr_columns = True

            elif method:
                # Edition not allowed, but method set
                item['Method'] = method.Title()
                item['replace']['Method'] = "<a href='%s'>%s</a>" % \
                    (method.absolute_url(), method.Title())
                show_methodinstr_columns = True

            # TODO: Instrument selector dynamic behavior in worksheet Results
            # Only the labmanager must be able to change the instrument to be used. Also,
            # the instrument selection should be done in accordance with the method selected
            # can_set_instrument = service.getInstrumentEntryOfResults() and getSecurityManager().checkPermission(SetAnalysisInstrument, obj)
            can_set_instrument = service.getInstrumentEntryOfResults() \
                and can_edit_analysis \
                and item['review_state'] in allowed_method_states

            item['Instrument'] = ''
            item['replace']['Instrument'] = ''
            if service.getInstrumentEntryOfResults():
                instrument = None

                # If the analysis has an instrument already assigned, use it
                if service.getInstrumentEntryOfResults() \
                    and hasattr(obj, 'getInstrument') \
                    and obj.getInstrument():
                        instrument = obj.getInstrument()

                # Otherwise, use the Service's default instrument
                elif service.getInstrumentEntryOfResults():
                        instrument = service.getInstrument()

                if can_set_instrument:
                    # Edition allowed
                    voc = self.get_instruments_vocabulary(obj)
                    if voc:
                        # The service has at least one instrument available
                        item['Instrument'] = instrument.UID() if instrument else ''
                        item['choices']['Instrument'] = voc
                        item['allow_edit'].append('Instrument')
                        show_methodinstr_columns = True

                    elif instrument:
                        # This should never happen
                        # The analysis has an instrument set, but the
                        # service hasn't any available instrument
                        item['Instrument'] = instrument.Title()
                        item['replace']['Instrument'] = "<a href='%s'>%s</a>" % \
                            (instrument.absolute_url(), instrument.Title())
                        show_methodinstr_columns = True

                elif instrument:
                    # Edition not allowed, but instrument set
                    item['Instrument'] = instrument.Title()
                    item['replace']['Instrument'] = "<a href='%s'>%s</a>" % \
                        (instrument.absolute_url(), instrument.Title())
                    show_methodinstr_columns = True

            else:
                # Manual entry of results, instrument not allowed
                item['Instrument'] = _('Manual')
                msgtitle = t(_(
                    "Instrument entry of results not allowed for ${service}",
                    mapping={"service": safe_unicode(service.Title())},
                ))
                item['replace']['Instrument'] = \
                    '<a href="#" title="%s">%s</a>' % (msgtitle, t(_('Manual')))

            # Sets the analyst assigned to this analysis
            if can_edit_analysis:
                analyst = obj.getAnalyst()
                # widget default: current user
                if not analyst:
                    analyst = mtool.getAuthenticatedMember().getUserName()
                items[i]['Analyst'] = analyst
                item['choices']['Analyst'] = self.getAnalysts()
            else:
                items[i]['Analyst'] = obj.getAnalystName()

            # If the user can attach files to analyses, show the attachment col
            can_add_attachment = \
                getSecurityManager().checkPermission(AddAttachment, obj)
            if can_add_attachment or can_view_result:
                attachments = ""
                if hasattr(obj, 'getAttachment'):
                    for attachment in obj.getAttachment():
                        af = attachment.getAttachmentFile()
                        icon = af.getBestIcon()
                        attachments += "<span class='attachment' attachment_uid='%s'>" % (attachment.UID())
                        if icon: attachments += "<img src='%s/%s'/>" % (self.portal_url, icon)
                        attachments += '<a href="%s/at_download/AttachmentFile"/>%s</a>' % (attachment.absolute_url(), af.filename)
                        if can_edit_analysis:
                            attachments += "<img class='deleteAttachmentButton' attachment_uid='%s' src='%s'/>" % (attachment.UID(), "++resource++bika.lims.images/delete.png")
                        attachments += "</br></span>"
                items[i]['replace']['Attachments'] = attachments[:-12] + "</span>"

            # Only display data bearing fields if we have ViewResults
            # permission, otherwise just put an icon in Result column.
            if can_view_result:
                items[i]['Result'] = result
                scinot = self.context.bika_setup.getScientificNotationResults()
                dmk = self.context.bika_setup.getResultsDecimalMark()
                items[i]['formatted_result'] = obj.getFormattedResult(sciformat=int(scinot),decimalmark=dmk)
                items[i]['Uncertainty'] = format_uncertainty(obj, result, decimalmark=dmk, sciformat=int(scinot))

            else:
                items[i]['Specification'] = ""
                if 'Result' in items[i]['allow_edit']:
                    items[i]['allow_edit'].remove('Result')
                items[i]['before']['Result'] = \
                    '<img width="16" height="16" ' + \
                    'src="%s/++resource++bika.lims.images/to_follow.png"/>' % \
                    (self.portal_url)
            # Everyone can see valid-ranges
            spec = self.get_analysis_spec(obj)
            if spec:
                min_val = spec.get('min', '')
                min_str = ">{0}".format(min_val) if min_val else ''
                max_val = spec.get('max', '')
                max_str = "<{0}".format(max_val) if max_val else ''
                error_val = spec.get('error', '')
                error_str = "{0}%".format(error_val) if error_val else ''
                rngstr = ",".join([x for x in [min_str, max_str, error_str] if x])
            else:
                rngstr = ""
            items[i]['Specification'] = rngstr
            # Add this analysis' interim fields to the interim_columns list
            for f in self.interim_fields[obj.UID()]:
                if f['keyword'] not in self.interim_columns and not f.get('hidden', False):
                    self.interim_columns[f['keyword']] = f['title']
                # and to the item itself
                items[i][f['keyword']] = f
                items[i]['class'][f['keyword']] = 'interim'

            # check if this analysis is late/overdue

            resultdate = obj.aq_parent.getDateSampled() \
                if obj.portal_type == 'ReferenceAnalysis' \
                else obj.getResultCaptureDate()

            duedate = obj.aq_parent.getExpiryDate() \
                if obj.portal_type == 'ReferenceAnalysis' \
                else obj.getDueDate()

            items[i]['replace']['DueDate'] = \
                self.ulocalized_time(duedate, long_format=1)

            if items[i]['review_state'] not in ['to_be_sampled',
                                                'to_be_preserved',
                                                'sample_due',
                                                'published']:

                if (resultdate and resultdate > duedate) \
                    or (not resultdate and DateTime() > duedate):

                    items[i]['replace']['DueDate'] = '%s <img width="16" height="16" src="%s/++resource++bika.lims.images/late.png" title="%s"/>' % \
                        (self.ulocalized_time(duedate, long_format=1),
                         self.portal_url,
                         t(_("Late Analysis")))

            # Submitting user may not verify results (admin can though)
            if items[i]['review_state'] == 'to_be_verified' and \
               not checkPermission(VerifyOwnResults, obj):
                user_id = getSecurityManager().getUser().getId()
                self_submitted = False
                try:
                    review_history = list(workflow.getInfoFor(obj, 'review_history'))
                    review_history.reverse()
                    for event in review_history:
                        if event.get('action') == 'submit':
                            if event.get('actor') == user_id:
                                self_submitted = True
                            break
                    if self_submitted:
                        items[i]['after']['state_title'] = \
                             "<img src='++resource++bika.lims.images/submitted-by-current-user.png' title='%s'/>" % \
                             (t(_("Cannot verify: Submitted by current user")))
                except WorkflowException:
                    pass

            # add icon for assigned analyses in AR views
            if self.context.portal_type == 'AnalysisRequest':
                obj = items[i]['obj']
                if obj.portal_type in ['ReferenceAnalysis',
                                       'DuplicateAnalysis'] or \
                   workflow.getInfoFor(obj, 'worksheetanalysis_review_state') == 'assigned':
                    br = obj.getBackReferences('WorksheetAnalysis')
                    if len(br) > 0:
                        ws = br[0]
                        items[i]['after']['state_title'] = \
                             "<a href='%s'><img src='++resource++bika.lims.images/worksheet.png' title='%s'/></a>" % \
                             (ws.absolute_url(),
                              t(_("Assigned to: ${worksheet_id}",
                                  mapping={'worksheet_id': safe_unicode(ws.id)})))

        # the TAL requires values for all interim fields on all
        # items, so we set blank values in unused cells
        for item in items:
            for field in self.interim_columns:
                if field not in item:
                    item[field] = ''

        # XXX order the list of interim columns
        interim_keys = self.interim_columns.keys()
        interim_keys.reverse()

        # add InterimFields keys to columns
        for col_id in interim_keys:
            if col_id not in self.columns:
                self.columns[col_id] = {'title': self.interim_columns[col_id],
                                        'input_width': '6',
                                        'input_class': 'ajax_calculate numeric',
                                        'sortable': False}

        if can_edit_analyses:
            new_states = []
            for state in self.review_states:
                # InterimFields are displayed in review_state
                # They are anyway available through View.columns though.
                # In case of hidden fields, the calcs.py should check calcs/services
                # for additional InterimFields!!
                pos = 'Result' in state['columns'] and \
                    state['columns'].index('Result') or len(state['columns'])
                for col_id in interim_keys:
                    if col_id not in state['columns']:
                        state['columns'].insert(pos, col_id)
                # retested column is added after Result.
                pos = 'Result' in state['columns'] and \
                    state['columns'].index('Uncertainty') + 1 or len(state['columns'])
                state['columns'].insert(pos, 'retested')
                new_states.append(state)
            self.review_states = new_states
            # Allow selecting individual analyses
            self.show_select_column = True

        # Dry Matter.
        # The Dry Matter column is never enabled for reference sample contexts
        # and refers to getReportDryMatter in ARs.
        if items and \
            (hasattr(self.context, 'getReportDryMatter') and \
             self.context.getReportDryMatter()):

            # look through all items
            # if the item's Service supports ReportDryMatter, add getResultDM().
            for item in items:
                if item['obj'].getService().getReportDryMatter():
                    item['ResultDM'] = item['obj'].getResultDM()
                else:
                    item['ResultDM'] = ''
                if item['ResultDM']:
                    item['after']['ResultDM'] = "<em class='discreet'>%</em>"

            # modify the review_states list to include the ResultDM column
            new_states = []
            for state in self.review_states:
                pos = 'Result' in state['columns'] and \
                    state['columns'].index('Uncertainty') + 1 or len(state['columns'])
                state['columns'].insert(pos, 'ResultDM')
                new_states.append(state)
            self.review_states = new_states

        self.categories.sort()

        # self.json_specs = json.dumps(self.specs)
        self.json_interim_fields = json.dumps(self.interim_fields)
        self.items = items

        # Method and Instrument columns must be shown or hidden at the
        # same time, because the value assigned to one causes
        # a value reassignment to the other (one method can be performed
        # by different instruments)
        self.columns['Method']['toggle'] = show_methodinstr_columns
        self.columns['Instrument']['toggle'] = show_methodinstr_columns

        return items


class QCAnalysesView(AnalysesView):
    """ Renders the table of QC Analyses performed related to an AR. Different
        AR analyses can be achieved inside different worksheets, and each one
        of these can have different QC Analyses. This table only lists the QC
        Analyses performed in those worksheets in which the current AR has, at
        least, one analysis assigned and if the QC analysis services match with
        those from the current AR.
    """

    def __init__(self, context, request, **kwargs):
        AnalysesView.__init__(self, context, request, **kwargs)
        self.columns['getReferenceAnalysesGroupID'] = {'title': _('QC Sample ID'),
                                                       'sortable': False}
        self.columns['Worksheet'] = {'title': _('Worksheet'),
                                                'sortable': False}
        self.review_states[0]['columns'] = ['Service',
                                            'Worksheet',
                                            'getReferenceAnalysesGroupID',
                                            'Partition',
                                            'Method',
                                            'Instrument',
                                            'Result',
                                            'Uncertainty',
                                            'CaptureDate',
                                            'DueDate',
                                            'state_title']

        qcanalyses = context.getQCAnalyses()
        asuids = [an.UID() for an in qcanalyses]
        self.catalog = 'bika_analysis_catalog'
        self.contentFilter = {'UID': asuids,
                              'sort_on': 'sortable_title'}
        self.icon = self.portal_url + \
                    "/++resource++bika.lims.images/referencesample.png"

    def folderitems(self):
        items = AnalysesView.folderitems(self)
        # Group items by RefSample - Worksheet - Position
        for i in range(len(items)):
            obj = items[i]['obj']
            wss = obj.getBackReferences('WorksheetAnalysis')
            wsid = wss[0].id if wss and len(wss) > 0 else ''
            wshref = wss[0].absolute_url() if wss and len(wss) > 0 else None
            if wshref:
                items[i]['replace']['Worksheet'] = "<a href='%s'>%s</a>" % (wshref, wsid)

            imgtype = ""
            if obj.portal_type == 'ReferenceAnalysis':
                antype = QCANALYSIS_TYPES.getValue(obj.getReferenceType())
                if obj.getReferenceType() == 'c':
                    imgtype = "<img title='%s' src='%s/++resource++bika.lims.images/control.png'/>&nbsp;" % (antype, self.context.absolute_url())
                if obj.getReferenceType() == 'b':
                    imgtype = "<img title='%s' src='%s/++resource++bika.lims.images/blank.png'/>&nbsp;" % (antype, self.context.absolute_url())
                items[i]['replace']['Partition'] = "<a href='%s'>%s</a>" % (obj.aq_parent.absolute_url(), obj.aq_parent.id)
            elif obj.portal_type == 'DuplicateAnalysis':
                antype = QCANALYSIS_TYPES.getValue('d')
                imgtype = "<img title='%s' src='%s/++resource++bika.lims.images/duplicate.png'/>&nbsp;" % (antype, self.context.absolute_url())
                items[i]['sortcode'] = '%s_%s' % (obj.getSample().id, obj.getService().getKeyword())

            items[i]['before']['Service'] = imgtype
            items[i]['sortcode'] = '%s_%s' % (obj.getReferenceAnalysesGroupID(),
                                              obj.getService().getKeyword())

        # Sort items
        items = sorted(items, key = itemgetter('sortcode'))
        return items
