from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.content.instrumentmaintenancetask import InstrumentMaintenanceTaskStatuses as mstatus
from bika.lims.subscribers import doActionFor, skip
from operator import itemgetter
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from plone.app.layout.viewlets import ViewletBase
from zope.interface import implements
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import QCANALYSIS_TYPES
from bika.lims.utils import to_utf8
from bika.lims.permissions import *
from operator import itemgetter
from bika.lims.browser import BrowserView
from bika.lims.browser.analyses import AnalysesView
from bika.lims.browser.analyses import QCAnalysesView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zExceptions import Forbidden
from operator import itemgetter

import plone
import json

class InstrumentMaintenanceView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(InstrumentMaintenanceView, self).__init__(context, request)
        self.catalog = "portal_catalog"
        self.contentFilter = {
            'portal_type': 'InstrumentMaintenanceTask',
        }
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=InstrumentMaintenanceTask',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.show_select_all_checkbox = False
        self.pagesize = 40
        self.form_id = "instrumentmaintenance"
        self.icon = self.portal_url + "/++resource++bika.lims.images/instrumentmaintenance_big.png"
        self.title = self.context.translate(_("Instrument Maintenance"))
        self.description = ""

        self.columns = {
            'getCurrentState' : {'title': ''},
            'Title': {'title': _('Task'),
                      'index': 'sortable_title'},
            'getType' : {'title': _('Task type', 'Type'), 'sortable': True},
            'getDownFrom': {'title': _('Down from'), 'sortable': True},
            'getDownTo': {'title': _('Down to'), 'sortable': True},
            'getMaintainer': {'title': _('Maintainer'), 'sortable': True},
        }

        self.review_states = [
            {'id':'default',
             'title': _('Open'),
             'contentFilter': {'cancellation_state':'active'},
             'columns': ['getCurrentState',
                         'Title',
                         'getType',
                         'getDownFrom',
                         'getDownTo',
                         'getMaintainer']},
            {'id':'cancelled',
             'title': _('Cancelled'),
             'contentFilter': {'cancellation_state': 'cancelled'},
             'columns': ['getCurrentState',
                         'Title',
                         'getType',
                         'getDownFrom',
                         'getDownTo',
                         'getMaintainer']},

            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['getCurrentState',
                         'Title',
                         'getType',
                         'getDownFrom',
                         'getDownTo',
                         'getMaintainer']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        outitems = []
        toshow = []
        for man in self.context.getMaintenanceTasks():
            toshow.append(man.UID())
        for x in range (len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            if obj.UID() in toshow:
                items[x]['getType'] = safe_unicode(_(obj.getType()[0])).encode('utf-8')
                items[x]['getDownFrom'] = obj.getDownFrom() and self.ulocalized_time(obj.getDownFrom(), long_format=1) or ''
                items[x]['getDownTo'] = obj.getDownTo() and self.ulocalized_time(obj.getDownTo(), long_format=1) or ''
                items[x]['getMaintainer'] = safe_unicode(_(obj.getMaintainer())).encode('utf-8')
                items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                     (items[x]['url'], safe_unicode(items[x]['Title']).encode('utf-8'))

                status = obj.getCurrentState();
                statustext = obj.getCurrentStateI18n();
                statusimg = "";
                if status == mstatus.CLOSED:
                    statusimg = "instrumentmaintenance_closed.png"
                elif status == mstatus.CANCELLED:
                    statusimg = "instrumentmaintenance_cancelled.png"
                elif status == mstatus.INQUEUE:
                    statusimg = "instrumentmaintenance_inqueue.png"
                elif status == mstatus.OVERDUE:
                    statusimg = "instrumentmaintenance_overdue.png"
                elif status == mstatus.PENDING:
                    statusimg = "instrumentmaintenance_pending.png"

                items[x]['replace']['getCurrentState'] = \
                    "<img title='%s' src='%s/++resource++bika.lims.images/%s'/>" % \
                    (statustext, self.portal_url, statusimg)
                outitems.append(items[x])
        return outitems

class InstrumentCalibrationsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(InstrumentCalibrationsView, self).__init__(context, request)
        self.catalog = "portal_catalog"
        self.contentFilter = {
            'portal_type': 'InstrumentCalibration',
        }
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=InstrumentCalibration',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.show_table_only = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25
        self.form_id = "instrumentcalibrations"
        self.icon = self.portal_url + "/++resource++bika.lims.images/instrumentcalibration_big.png"
        self.title = self.context.translate(_("Instrument Calibrations"))
        self.description = ""

        self.columns = {
            'Title': {'title': _('Task'),
                      'index': 'sortable_title'},
            'getDownFrom': {'title': _('Down from')},
            'getDownTo': {'title': _('Down to')},
            'getCalibrator': {'title': _('Calibrator')},
        }
        self.review_states = [
            {'id':'default',
             'title':_('All'),
             'contentFilter':{},
             'columns': [ 'Title',
                         'getDownFrom',
                         'getDownTo',
                         'getCalibrator']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        outitems = []
        toshow = []
        for cal in self.context.getCalibrations():
            toshow.append(cal.UID())
        for x in range (len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            if obj.UID() in toshow:
                items[x]['getDownFrom'] = obj.getDownFrom()
                items[x]['getDownTo'] = obj.getDownTo()
                items[x]['getCalibrator'] = obj.getCalibrator()
                items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                     (items[x]['url'], items[x]['Title'])
                outitems.append(items[x])
        return outitems

class InstrumentValidationsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(InstrumentValidationsView, self).__init__(context, request)
        self.catalog = "portal_catalog"
        self.contentFilter = {
            'portal_type': 'InstrumentValidation',
        }
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=InstrumentValidation',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.show_table_only = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25
        self.form_id = "instrumentvalidations"
        self.icon = self.portal_url + "/++resource++bika.lims.images/instrumentvalidation_big.png"
        self.title = self.context.translate(_("Instrument Validations"))
        self.description = ""

        self.columns = {
            'Title': {'title': _('Task'),
                      'index': 'sortable_title'},
            'getDownFrom': {'title': _('Down from')},
            'getDownTo': {'title': _('Down to')},
            'getValidator': {'title': _('Validator')},
        }
        self.review_states = [
            {'id':'default',
             'title':_('All'),
             'contentFilter':{},
             'columns': [ 'Title',
                         'getDownFrom',
                         'getDownTo',
                         'getValidator']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        outitems = []
        toshow = []
        for val in self.context.getValidations():
            toshow.append(val.UID())
        for x in range (len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            if obj.UID() in toshow:
                items[x]['getDownFrom'] = obj.getDownFrom()
                items[x]['getDownTo'] = obj.getDownTo()
                items[x]['getValidator'] = obj.getValidator()
                items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                     (items[x]['url'], items[x]['Title'])
                outitems.append(items[x])
        return outitems

class InstrumentScheduleView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(InstrumentScheduleView, self).__init__(context, request)
        self.catalog = "portal_catalog"
        self.contentFilter = {
            'portal_type': 'InstrumentScheduledTask',
            'getInstrumentUID()':context.UID(),
        }
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=InstrumentScheduledTask',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.show_table_only = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.show_select_all_checkbox = False
        self.pagesize = 25

        self.form_id = "instrumentschedule"
        self.icon = self.portal_url + "/++resource++bika.lims.images/instrumentschedule_big.png"
        self.title = self.context.translate(_("Instrument Scheduled Tasks"))
        self.description = ""

        self.columns = {
            'Title': {'title': _('Scheduled task'),
                      'index': 'sortable_title'},
            'getType': {'title': _('Task type', 'Type')},
            'getCriteria': {'title': _('Criteria')},
            'creator': {'title': _('Created by')},
            'created' : {'title': _('Created')},
        }

        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id':'deactivate'}, ],
             'columns': [ 'Title',
                         'getType',
                         'getCriteria',
                         'creator',
                         'created']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': [ 'Title',
                         'getType',
                         'getCriteria',
                         'creator',
                         'created']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': [ 'Title',
                         'getType',
                         'getCriteria',
                         'creator',
                         'created']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        outitems = []
        toshow = []
        for sch in self.context.getSchedule():
            toshow.append(sch.UID())

        for x in range (len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            if obj.UID() in toshow:
                items[x]['created'] = self.ulocalized_time(obj.created())
                items[x]['creator'] = obj.Creator()
                items[x]['getType'] = safe_unicode(_(obj.getType()[0])).encode('utf-8')
                items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                     (items[x]['url'], items[x]['Title'])
                outitems.append(items[x])
        return outitems


class InstrumentReferenceAnalysesViewView(BrowserView):
    """ View of Reference Analyses linked to the Instrument.
        Only shows the Reference Analyses (Control and Blanks), the rest
        of regular and duplicate analyses linked to this instrument are
        not displayed.
        The Reference Analyses from an Instrument can be from Worksheets
        (QC analysis performed regularly for any Analysis Request) or
        attached directly to the instrument, without being linked to
        any Worksheet). In this case, the Reference Analyses are created
        automatically by the instrument import tool.
    """

    implements(IViewView)
    template = ViewPageTemplateFile("templates/instrument_referenceanalyses.pt")

    def __init__(self, context, request):
        super(InstrumentReferenceAnalysesViewView, self).__init__(context, request)
        self.icon = self.portal_url + "/++resource++bika.lims.images/referencesample_big.png"
        self.title = self.context.translate(_("Internal Calibration Tests"))
        self.description = ""
        self._analysesview = None

    def __call__(self):
        return self.template()

    def get_analyses_table(self):
        """ Returns the table of Reference Analyses
        """
        return self.get_analyses_view().contents_table()

    def get_analyses_view(self):
        if not self._analysesview:
            # Creates the Analyses View if not exists yet
            self._analysesview = InstrumentReferenceAnalysesView(self.context,
                                    self.request,
                                    show_categories=False)
            self._analysesview.allow_edit = False
            self._analysesview.show_select_column = False
            self._analysesview.show_workflow_action_buttons = False
            self._analysesview.form_id = "%s_qcanalyses" % self.context.UID()
            self._analysesview.review_states[0]['transitions'] = [{}]

        return self._analysesview

    def get_analyses_json(self):
        return self.get_analyses_view().get_analyses_json()


class InstrumentReferenceAnalysesView(AnalysesView):
    """ View for the table of Reference Analyses linked to the Instrument.
        Only shows the Reference Analyses (Control and Blanks), the rest
        of regular and duplicate analyses linked to this instrument are
        not displayed.
    """

    def __init__(self, context, request, **kwargs):
        AnalysesView.__init__(self, context, request, **kwargs)
        self.columns['getReferenceAnalysesGroupID'] = {'title': _('QC Sample ID'),
                                                       'sortable': False}
        self.columns['Partition'] = {'title': _('Reference Sample'),
                                     'sortable': False}
        self.columns['Retractions'] = {'title': '',
                                                  'sortable': False}
        self.review_states[0]['columns'] = ['Service',
                                            'getReferenceAnalysesGroupID',
                                            'Partition',
                                            'Result',
                                            'Uncertainty',
                                            'CaptureDate',
                                            'Retractions']


        analyses = self.context.getReferenceAnalyses()
        asuids = [an.UID() for an in analyses]
        self.catalog = 'bika_analysis_catalog'
        self.contentFilter = {'UID': asuids}
        self.anjson = {}

    def folderitems(self):
        items = AnalysesView.folderitems(self)
        items.sort(key=itemgetter('CaptureDate'), reverse=True)
        for i in range(len(items)):
            obj = items[i]['obj']
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
            else:
                items[i]['sortcode'] = '%s_%s' % (obj.getSample().id, obj.getService().getKeyword())

            items[i]['before']['Service'] = imgtype

            # Get retractions field
            pdf = obj.getRetractedAnalysesPdfReport()
            title = ''
            anchor = ''
            try:
                if pdf:
                    filesize = 0
                    title = _('Retractions')
                    anchor = "<a class='pdf' target='_blank' href='%s/at_download/RetractedAnalysesPdfReport'>%s</a>" % \
                             (obj.absolute_url(), _("Retractions"))
                    filesize = pdf.get_size()
                    filesize = filesize / 1024 if filesize > 0 else 0
            except:
                # POSKeyError: 'No blob file'
                # Show the record, but not the link
                title = _('Retraction report unavailable')
                anchor = title
            items[i]['Retractions'] = title
            items[i]['replace']['Retractions'] = anchor


            # Create json
            qcid = obj.aq_parent.id;
            serviceref = "%s (%s)" % (items[i]['Service'], items[i]['Keyword'])
            trows = self.anjson.get(serviceref, {});
            anrows = trows.get(qcid, []);
            anid = '%s.%s' % (items[i]['getReferenceAnalysesGroupID'],
                              items[i]['id'])

            rr = obj.aq_parent.getResultsRangeDict()
            uid = obj.getServiceUID()
            if uid in rr:
                specs = rr[uid];
                try:
                    smin  = float(specs.get('min', 0))
                    smax = float(specs.get('max', 0))
                    error  = float(specs.get('error', 0))
                    target = float(specs.get('result', 0))
                    result = float(items[i]['Result'])
                    error_amount = ((target / 100) * error) if target > 0 else 0
                    upper  = smax + error_amount
                    lower   = smin - error_amount

                    anrow = { 'date': items[i]['CaptureDate'],
                              'min': smin,
                              'max': smax,
                              'target': target,
                              'error': error,
                              'erroramount': error_amount,
                              'upper': upper,
                              'lower': lower,
                              'result': result,
                              'unit': items[i]['Unit'],
                              'id': items[i]['uid'] }
                    anrows.append(anrow);
                    trows[qcid] = anrows;
                    self.anjson[serviceref] = trows
                except:
                    pass

        return items

    def get_analyses_json(self):
        return json.dumps(self.anjson)


class InstrumentCertificationsViewView(BrowserView):
    """ View of Instrument Certifications
        Shows the list of Instrument Certifications, either Internal and
        External Calibrations.
    """

    implements(IViewView)
    template = ViewPageTemplateFile("templates/instrument_certifications.pt")
    _certificationsview = None

    def __call__(self):
        return self.template()

    def get_certifications_table(self):
        """ Returns the table of Certifications
        """
        return self.get_certifications_view().contents_table()

    def get_certifications_view(self):
        """ Returns the Certifications Table view
        """
        if not self._certificationsview:
            self._certificationsview = InstrumentCertificationsView(
                                        self.context,
                                        self.request)
        return self._certificationsview


class InstrumentCertificationsView(BikaListingView):
    """ View for the table of Certifications. Includes Internal and
        External Calibrations. Also a bar to filter the results
    """

    def __init__(self, context, request, **kwargs):
        BikaListingView.__init__(self, context, request, **kwargs)
        self.form_id = "instrumentcertifications"
        self.columns = {
            'Title': {'title': _('Cert. Num'),
                      'index': 'sortable_title'},
            'getAgency': {'title': _('Agency')},
            'getDate': {'title': _('Date')},
            'getValidFrom': {'title': _('Valid from')},
            'getValidTo': {'title': _('Valid to')},
            'getDocument': {'title': _('Document')},
        }
        self.review_states = [
            {'id':'default',
             'title':_('All'),
             'contentFilter':{},
             'columns': [ 'Title',
                         'getAgency',
                         'getDate',
                         'getValidFrom',
                         'getValidTo',
                         'getDocument'],
             'transitions': [{}]},
        ]
        self.allow_edit = False
        self.show_select_column = False
        self.show_workflow_action_buttons = False
        uids = [c.UID() for c in self.context.getCertifications()]
        self.catalog = 'portal_catalog'
        self.contentFilter = {'UID': uids, 'sort_on': 'sortable_title'}

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        valid  = [c.UID() for c in self.context.getValidCertifications()]
        latest = self.context.getLatestValidCertification()
        latest = latest.UID() if latest else ''
        for x in range (len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
           # items[x]['getAgency'] = obj.getAgency()
            items[x]['getDate'] = self.ulocalized_time(obj.getDate(), long_format=0)
            items[x]['getValidFrom'] = self.ulocalized_time(obj.getValidFrom(), long_format=0)
            items[x]['getValidTo'] = self.ulocalized_time(obj.getValidTo(), long_format=0)
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])
            if obj.getInternal() == True:
                items[x]['replace']['getAgency'] = ""
                items[x]['state_class'] = '%s %s' % (items[x]['state_class'], 'internalcertificate')

            items[x]['getDocument'] = ""
            items[x]['replace']['getDocument'] = ""
            try:
                doc = obj.getDocument()
                if doc and doc.get_size() > 0:
                    anchor = "<a href='%s/at_download/Document'>%s</a>" % \
                            (obj.absolute_url(), doc.filename)
                    items[x]['getDocument'] = doc.filename
                    items[x]['replace']['getDocument'] = anchor
            except:
                # POSKeyError: 'No blob file'
                # Show the record, but not the link
                title = _('Not available')
                items[x]['getDocument'] = _('Not available')
                items[x]['replace']['getDocument'] = _('Not available')

            uid = obj.UID()
            if uid in valid:
                # Valid calibration.
                items[x]['state_class'] = '%s %s' % (items[x]['state_class'], 'active')
            elif uid == latest:
                # Latest valid certificate
                img = "<img title='%s' src='%s/++resource++bika.lims.images/exclamation.png'/>&nbsp;" \
                % (t(_('Out of date')), self.portal_url)
                items[x]['replace']['getValidTo'] = '%s %s' % (items[x]['getValidTo'], img)
                items[x]['state_class'] = '%s %s' % (items[x]['state_class'], 'inactive outofdate')
            else:
                # Old and further calibrations
                items[x]['state_class'] = '%s %s' % (items[x]['state_class'], 'inactive')

        return items


class InstrumentMultifileView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(InstrumentMultifileView, self).__init__(context, request)
        self.catalog = "bika_setup_catalog"
        self.contentFilter = {
            'portal_type': 'Multifile',
        }
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=Multifile',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.show_table_only = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25
        self.form_id = "instrumentmultifile"
        self.icon = self.portal_url + "/++resource++bika.lims.images/instrumentcertification_big.png"
        self.title = self.context.translate(_("Instrument Files"))
        self.description = ""

        self.columns = {
            'DocumentID': {'title': _('Document ID'),
                           'index': 'sortable_title'},
            'DocumentVersion': {'title': _('Document Version'), 'index': 'sortable_title'},
            'DocumentLocation': {'title': _('Document Location'), 'index': 'sortable_title'},
            'DocumentType': {'title': _('Document Type'), 'index': 'sortable_title'},
            'FileDownload': {'title': _('File')}
        }
        self.review_states = [
            {'id': 'default',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['DocumentID',
                         'DocumentVersion',
                         'DocumentLocation',
                         'DocumentType',
                         'FileDownload']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        outitems = []
        toshow = []
        for val in self.context.getDocuments():
            toshow.append(val.UID())
        for x in range (len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            if obj.UID() in toshow:
                items[x]['replace']['DocumentID'] = "<a href='%s'>%s</a>" % \
                    (items[x]['url'], items[x]['DocumentID'])
                items[x]['FileDownload'] = obj.getFile().filename
                filename = obj.getFile().filename if obj.getFile().filename != '' else 'File'
                items[x]['replace']['FileDownload'] = "<a href='%s'>%s</a>" % \
                    (obj.getFile().absolute_url_path(), filename)
                items[x]['DocumentVersion'] = obj.getDocumentVersion()
                items[x]['DocumentLocation'] = obj.getDocumentLocation()
                items[x]['DocumentType'] = obj.getDocumentType()
                outitems.append(items[x])
        return outitems


class ajaxGetInstrumentMethod(BrowserView):
    """ Returns the method assigned to the defined instrument.
        uid: unique identifier of the instrument
    """
    def __call__(self):
        methoddict = {}
        try:
            plone.protect.CheckAuthenticator(self.request)
        except Forbidden:
            return json.dumps(methoddict)
        bsc = getToolByName(self, 'bika_setup_catalog')
        instrument = bsc(portal_type='Instrument', UID=self.request.get("uid", '0'))
        if instrument and len(instrument) == 1:
            method = instrument[0].getObject().getMethod()
            if method:
                methoddict = {'uid': method.UID(),
                              'title': method.Title()}
        return json.dumps(methoddict)


class InstrumentQCFailuresViewlet(ViewletBase):
    """ Print a viewlet showing failed instruments
    """

    index = ViewPageTemplateFile("templates/instrument_qc_failures_viewlet.pt")

    def __init__(self, context, request, view, manager=None):
        super(InstrumentQCFailuresViewlet, self).__init__(context, request, view, manager=manager)
        self.nr_failed = 0
        self.failed = {'out-of-date': [],
                       'qc-fail': [],
                       'next-test': [],
                       'validation': [],
                       'calibration': []}

    def get_failed_instruments(self):
        """ Find all active instruments who have failed QC tests
            Find instruments whose certificate is out of date
            Find instruments which are disposed until next calibration test

            Return a dictionary with the following structure:

                out-of-date: [{uid: <uid>,
                              title: <title>,
                              link: <absolute_path>},]
                qc-fail:     [{uid: <uid>,
                              title: <title>,
                              link: <absolute_path>},]
                next-test:   [{uid: <uid>,
                              title: <title>,
                              link: <absolute_path>},]

        >>> portal = layer['portal']
        >>> portal_url = portal.absolute_url()
        >>> from plone.app.testing import SITE_OWNER_NAME
        >>> from plone.app.testing import SITE_OWNER_PASSWORD
        >>> from DateTime import DateTime
        >>> from transaction import commit

        Expire the Blott Titrator's certificate:

        >>> bsc = portal.bika_setup_catalog
        >>> blott = bsc(portal_type='Instrument', Title='Blott Titrator')[0].getObject()
        >>> cert = blott.objectValues('InstrumentCertification')[0]
        >>> cert.setValidTo(DateTime('2014/11/27'))
        >>> commit()

        Then be sure that the viewlet is displayed:

        >>> browser = layer['getBrowser'](portal, loggedIn=True, username=SITE_OWNER_NAME, password=SITE_OWNER_PASSWORD)
        >>> browser.open(portal_url)
        >>> browser.contents
        '...instruments are out-of-date...'

        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        insts = bsc(portal_type='Instrument', inactive_state='active')
        for i in insts:
            i = i.getObject()
            instr = {
                'uid': i.UID(),
                'title': i.Title(),
            }
            if i.isValidationInProgress():
                instr['link'] = '<a href="%s/validations">%s</a>' % (
                    i.absolute_url(), i.Title()
                )
                self.nr_failed += 1
                self.failed['validation'].append(instr)
            elif i.isCalibrationInProgress():
                instr['link'] = '<a href="%s/calibrations">%s</a>' % (
                    i.absolute_url(), i.Title()
                )
                self.nr_failed += 1
                self.failed['calibration'].append(instr)
            elif i.isOutOfDate():
                instr['link'] = '<a href="%s/certifications">%s</a>' % (
                    i.absolute_url(), i.Title()
                )
                self.nr_failed += 1
                self.failed['out-of-date'].append(instr)
            elif not i.isQCValid():
                instr['link'] = '<a href="%s/referenceanalyses">%s</a>' % (
                    i.absolute_url(), i.Title()
                )
                self.nr_failed += 1
                self.failed['qc-fail'].append(instr)
            elif i.getDisposeUntilNextCalibrationTest():
                instr['link'] = '<a href="%s/referenceanalyses">%s</a>' % (
                    i.absolute_url(), i.Title()
                )
                self.nr_failed += 1
                self.failed['next-test'].append(instr)

    def render(self):

        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        roles = member.getRoles()
        allowed = 'LabManager' in roles or 'Manager' in roles

        self.get_failed_instruments()

        if allowed and self.nr_failed:
            return self.index()
        else:
            return ""
