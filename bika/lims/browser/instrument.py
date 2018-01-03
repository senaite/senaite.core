# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import json
from operator import itemgetter

import plone
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.browser.analyses import AnalysesView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.multifile import MultifileView
from bika.lims.browser.resultsimport.autoimportlogs import AutoImportLogsView
from bika.lims.config import QCANALYSIS_TYPES
from bika.lims.content.instrumentmaintenancetask import \
    InstrumentMaintenanceTaskStatuses as mstatus
from bika.lims.utils import t
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from plone.app.layout.viewlets import ViewletBase
from zExceptions import Forbidden
from zope.interface import implements


class InstrumentMaintenanceView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(InstrumentMaintenanceView, self).__init__(context, request)
        self.catalog = "portal_catalog"
        self.contentFilter = {
            'portal_type': 'InstrumentMaintenanceTask',
        }

        self.icon = self.portal_url + "/++resource++bika.lims.images/instrumentmaintenance_big.png"
        self.title = self.context.translate(_("Instrument Maintenance"))
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=InstrumentMaintenanceTask',
                                 'icon': '++resource++bika.lims.images/add.png'}}

        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.show_select_all_checkbox = False
        self.pagesize = 40
        self.form_id = "instrumentmaintenance"
        self.description = ""

        self.columns = {
            'getCurrentState': {'title': ''},
            'Title': {'title': _('Task'),
                      'index': 'sortable_title'},
            'getType': {'title': _('Task type', 'Type'), 'sortable': True},
            'getDownFrom': {'title': _('Down from'), 'sortable': True},
            'getDownTo': {'title': _('Down to'), 'sortable': True},
            'getMaintainer': {'title': _('Maintainer'), 'sortable': True},
        }

        self.review_states = [
            {
                'id': 'default',
                'title': _('Open'),
                'contentFilter': {'cancellation_state': 'active'},
                'columns': [
                    'getCurrentState',
                    'Title',
                    'getType',
                    'getDownFrom',
                    'getDownTo',
                    'getMaintainer',
                ]
            }, {
                'id': 'cancelled',
                'title': _('Cancelled'),
                'contentFilter': {'cancellation_state': 'cancelled'},
                'columns': [
                    'getCurrentState',
                    'Title',
                    'getType',
                    'getDownFrom',
                    'getDownTo',
                    'getMaintainer',
                ]
            }, {
                'id': 'all',
                'title': _('All'),
                'contentFilter': {},
                'columns': [
                    'getCurrentState',
                    'Title',
                    'getType',
                    'getDownFrom',
                    'getDownTo',
                    'getMaintainer'
                ]
            }
        ]

    def contentsMethod(self, *args, **kw):
        return self.context.getMaintenanceTasks()

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        outitems = []
        toshow = []
        for man in self.context.getMaintenanceTasks():
            toshow.append(man.UID())

        for item in items:
            if "obj" not in item:
                continue
            obj = item['obj']
            if obj.UID() in toshow:
                item['getType'] = safe_unicode(_(obj.getType()[0])).encode('utf-8')
                item['getDownFrom'] = obj.getDownFrom() and self.ulocalized_time(obj.getDownFrom(), long_format=1) or ''
                item['getDownTo'] = obj.getDownTo() and self.ulocalized_time(obj.getDownTo(), long_format=1) or ''
                item['getMaintainer'] = safe_unicode(_(obj.getMaintainer())).encode('utf-8')
                item['replace']['Title'] = "<a href='%s'>%s</a>" % \
                    (item['url'], safe_unicode(item['Title']).encode('utf-8'))

                status = obj.getCurrentState()
                statustext = obj.getCurrentStateI18n()
                statusimg = ""
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

                item['replace']['getCurrentState'] = \
                    "<img title='%s' src='%s/++resource++bika.lims.images/%s'/>" % \
                    (statustext, self.portal_url, statusimg)
                outitems.append(item)
        return outitems


class InstrumentCalibrationsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(InstrumentCalibrationsView, self).__init__(context, request)
        self.catalog = "portal_catalog"
        self.contentFilter = {
            'portal_type': 'InstrumentCalibration',
        }

        self.icon = self.portal_url + "/++resource++bika.lims.images/instrumentcalibration_big.png"
        self.title = self.context.translate(_("Instrument Calibrations"))
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=InstrumentCalibration',
                                 'icon': '++resource++bika.lims.images/add.png'}}

        self.show_table_only = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25
        self.form_id = "instrumentcalibrations"
        self.description = ""

        self.columns = {
            'Title': {'title': _('Task'),
                      'index': 'sortable_title'},
            'getDownFrom': {'title': _('Down from')},
            'getDownTo': {'title': _('Down to')},
            'getCalibrator': {'title': _('Calibrator')},
        }

        self.review_states = [
            {
                'id': 'default',
                'title': _('All'),
                'contentFilter': {},
                'columns': [
                    'Title',
                    'getDownFrom',
                    'getDownTo',
                    'getCalibrator',
                ]
            }
        ]

    def contentsMethod(self, *args, **kw):
        return self.context.getCalibrations()

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        outitems = []
        toshow = []

        for cal in self.context.getCalibrations():
            toshow.append(cal.UID())

        for item in items:
            if "obj" not in item:
                continue
            obj = item['obj']
            if obj.UID() in toshow:
                item['getDownFrom'] = obj.getDownFrom()
                item['getDownTo'] = obj.getDownTo()
                item['getCalibrator'] = obj.getCalibrator()
                item['replace']['Title'] = "<a href='%s'>%s</a>" % \
                    (item['url'], item['Title'])
                outitems.append(item)

        return outitems


class InstrumentValidationsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(InstrumentValidationsView, self).__init__(context, request)
        self.catalog = "portal_catalog"
        self.contentFilter = {
            'portal_type': 'InstrumentValidation',
        }

        self.icon = self.portal_url + "/++resource++bika.lims.images/instrumentvalidation_big.png"
        self.title = self.context.translate(_("Instrument Validations"))
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=InstrumentValidation',
                                 'icon': '++resource++bika.lims.images/add.png'}}

        self.show_table_only = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25
        self.form_id = "instrumentvalidations"
        self.description = ""

        self.columns = {
            'Title': {'title': _('Task'),
                      'index': 'sortable_title'},
            'getDownFrom': {'title': _('Down from')},
            'getDownTo': {'title': _('Down to')},
            'getValidator': {'title': _('Validator')},
        }
        self.review_states = [
            {
                'id': 'default',
                'title': _('All'),
                'contentFilter': {},
                'columns': [
                    'Title',
                    'getDownFrom',
                    'getDownTo',
                    'getValidator',
                ]
            }
        ]

    def contentsMethod(self, *args, **kw):
        return self.context.getValidations()

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        outitems = []
        toshow = []
        for val in self.context.getValidations():
            toshow.append(val.UID())
        for item in items:
            if "obj" not in item:
                continue
            obj = item['obj']
            if obj.UID() in toshow:
                item['getDownFrom'] = obj.getDownFrom()
                item['getDownTo'] = obj.getDownTo()
                item['getValidator'] = obj.getValidator()
                item['replace']['Title'] = "<a href='%s'>%s</a>" % \
                    (item['url'], item['Title'])
                outitems.append(item)
        return outitems


class InstrumentScheduleView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(InstrumentScheduleView, self).__init__(context, request)
        self.catalog = "portal_catalog"
        self.contentFilter = {
            'portal_type': 'InstrumentScheduledTask',
            'getInstrumentUID()': context.UID(),
        }

        self.icon = self.portal_url + "/++resource++bika.lims.images/instrumentschedule_big.png"
        self.title = self.context.translate(_("Instrument Scheduled Tasks"))
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
        self.description = ""

        self.columns = {
            'Title': {'title': _('Scheduled task'),
                      'index': 'sortable_title'},
            'getType': {'title': _('Task type', 'Type')},
            'getCriteria': {'title': _('Criteria')},
            'creator': {'title': _('Created by')},
            'created': {'title': _('Created')},
        }

        self.review_states = [
            {
                'id': 'default',
                'title': _('Active'),
                'contentFilter': {'inactive_state': 'active'},
                'transitions': [{'id': 'deactivate'}, ],
                'columns': [
                    'Title',
                    'getType',
                    'getCriteria',
                    'creator',
                    'created',
                ]
            }, {
                'id': 'inactive',
                'title': _('Dormant'),
                'contentFilter': {'inactive_state': 'inactive'},
                'transitions': [{'id': 'activate'}, ],
                'columns': [
                    'Title',
                    'getType',
                    'getCriteria',
                    'creator',
                    'created'
                ]
            }, {
                'id': 'all',
                'title': _('All'),
                'contentFilter': {},
                'columns': [
                    'Title',
                    'getType',
                    'getCriteria',
                    'creator',
                    'created',
                ]
            }
        ]

    def contentsMethod(self, *args, **kw):
        return self.context.getSchedule()

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        outitems = []
        toshow = []
        for sch in self.context.getSchedule():
            toshow.append(sch.UID())

        for item in items:
            if "obj" not in item:
                continue
            obj = item['obj']
            if obj.UID() in toshow:
                item['created'] = self.ulocalized_time(obj.created())
                item['creator'] = obj.Creator()
                item['getType'] = safe_unicode(_(obj.getType()[0])).encode('utf-8')
                item['replace']['Title'] = "<a href='%s'>%s</a>" % \
                    (item['url'], item['Title'])
                outitems.append(item)
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
            self._analysesview = InstrumentReferenceAnalysesView(
                self.context, self.request, show_categories=False)
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
        self.contentFilter = {'UID': asuids}
        self.anjson = {}

    # TODO-performance: Use folderitem and brains
    def folderitems(self):
        items = AnalysesView.folderitems(self)
        items.sort(key=itemgetter('CaptureDate'), reverse=True)
        for item in items:
            obj = item['obj']
            # TODO-performance: getting an object
            # Note here the object in items[i]['obj'] is a brain, cause the
            # base class (AnalysesView), calls folderitems(.., classic=False).
            obj = obj.getObject()
            imgtype = ""
            if obj.portal_type == 'ReferenceAnalysis':
                antype = QCANALYSIS_TYPES.getValue(obj.getReferenceType())
                if obj.getReferenceType() == 'c':
                    imgtype = "<img title='%s' src='%s/++resource++bika.lims.images/control.png'/>&nbsp;" % (antype, self.context.absolute_url())
                if obj.getReferenceType() == 'b':
                    imgtype = "<img title='%s' src='%s/++resource++bika.lims.images/blank.png'/>&nbsp;" % (antype, self.context.absolute_url())
                item['replace']['Partition'] = "<a href='%s'>%s</a>" % (obj.aq_parent.absolute_url(), obj.aq_parent.id)
            elif obj.portal_type == 'DuplicateAnalysis':
                antype = QCANALYSIS_TYPES.getValue('d')
                imgtype = "<img title='%s' src='%s/++resource++bika.lims.images/duplicate.png'/>&nbsp;" % (antype, self.context.absolute_url())
                item['sortcode'] = '%s_%s' % (obj.getSample().id, obj.getKeyword())
            else:
                item['sortcode'] = '%s_%s' % (obj.getSample().id, obj.getKeyword())

            item['before']['Service'] = imgtype

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
            item['Retractions'] = title
            item['replace']['Retractions'] = anchor

            # Create json
            qcid = obj.aq_parent.getId()
            serviceref = "%s (%s)" % (item['Service'], item['Keyword'])
            trows = self.anjson.get(serviceref, {})
            anrows = trows.get(qcid, [])
            # anid = '%s.%s' % (item['getReferenceAnalysesGroupID'],
            #                   item['id'])

            rr = obj.aq_parent.getResultsRangeDict()
            uid = obj.getServiceUID()
            if uid in rr:
                specs = rr[uid]
                try:
                    smin = float(specs.get('min', 0))
                    smax = float(specs.get('max', 0))
                    error = float(specs.get('error', 0))
                    target = float(specs.get('result', 0))
                    result = float(item['Result'])
                    error_amount = ((target / 100) * error) if target > 0 else 0
                    upper = smax + error_amount
                    lower = smin - error_amount

                    anrow = {
                        'date': item['CaptureDate'],
                        'min': smin,
                        'max': smax,
                        'target': target,
                        'error': error,
                        'erroramount': error_amount,
                        'upper': upper,
                        'lower': lower,
                        'result': result,
                        'unit': item['Unit'],
                        'id': item['uid']
                    }
                    anrows.append(anrow)
                    trows[qcid] = anrows
                    self.anjson[serviceref] = trows
                except:
                    pass

        return items

    def get_analyses_json(self):
        return json.dumps(self.anjson)


class InstrumentCertificationsView(BikaListingView):
    """ View for the table of Certifications. Includes Internal and
        External Calibrations. Also a bar to filter the results
    """

    def __init__(self, context, request, **kwargs):
        BikaListingView.__init__(self, context, request, **kwargs)
        self.form_id = "instrumentcertifications"

        self.icon = self.portal_url + "/++resource++bika.lims.images/instrumentcertification_big.png"
        self.title = self.context.translate(_("Calibration Certificates"))
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=InstrumentCertification',
                                 'icon': '++resource++bika.lims.images/add.png'}}

        self.columns = {
            'Title': {'title': _('Cert. Num'), 'index': 'sortable_title'},
            'getAgency': {'title': _('Agency'), 'sortable': False},
            'getDate': {'title': _('Date'), 'sortable': False},
            'getValidFrom': {'title': _('Valid from'), 'sortable': False},
            'getValidTo': {'title': _('Valid to'), 'sortable': False},
            'getDocument': {'title': _('Document'), 'sortable': False},
        }

        self.review_states = [
            {
                'id': 'default',
                'title': _('All'),
                'contentFilter': {},
                'columns': [
                    'Title',
                    'getAgency',
                    'getDate',
                    'getValidFrom',
                    'getValidTo',
                    'getDocument',
                ],
                'transitions': []
            }
        ]
        self.allow_edit = False
        self.show_select_column = False
        self.show_workflow_action_buttons = True
        uids = [c.UID() for c in self.context.getCertifications()]
        self.catalog = 'portal_catalog'
        self.contentFilter = {'UID': uids, 'sort_on': 'sortable_title'}

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        valid = [c.UID() for c in self.context.getValidCertifications()]
        latest = self.context.getLatestValidCertification()
        latest = latest.UID() if latest else ''

        for item in items:
            if "obj" not in item:
                continue
            obj = item['obj']
            item['getDate'] = self.ulocalized_time(obj.getDate(), long_format=0)
            item['getValidFrom'] = self.ulocalized_time(obj.getValidFrom(), long_format=0)
            item['getValidTo'] = self.ulocalized_time(obj.getValidTo(), long_format=0)
            item['replace']['Title'] = "<a href='%s'>%s</a>" % \
                (item['url'], item['Title'])
            if obj.getInternal() is True:
                item['replace']['getAgency'] = ""
                item['state_class'] = '%s %s' % (item['state_class'], 'internalcertificate')

            item['getDocument'] = ""
            item['replace']['getDocument'] = ""
            try:
                doc = obj.getDocument()
                if doc and doc.get_size() > 0:
                    anchor = "<a href='%s/at_download/Document'>%s</a>" % \
                        (obj.absolute_url(), doc.filename)
                    item['getDocument'] = doc.filename
                    item['replace']['getDocument'] = anchor
            except:
                # POSKeyError: 'No blob file'
                # Show the record, but not the link
                item['getDocument'] = _('Not available')
                item['replace']['getDocument'] = _('Not available')

            uid = obj.UID()
            if uid in valid:
                # Valid calibration.
                item['state_class'] = '%s %s' % (item['state_class'], 'active')
            elif uid == latest:
                # Latest valid certificate
                img = "<img title='%s' src='%s/++resource++bika.lims.images/exclamation.png'/>&nbsp;" \
                    % (t(_('Out of date')), self.portal_url)
                item['replace']['getValidTo'] = '%s %s' % (item['getValidTo'], img)
                item['state_class'] = '%s %s' % (item['state_class'], 'inactive outofdate')
            else:
                # Old and further calibrations
                item['state_class'] = '%s %s' % (item['state_class'], 'inactive')

        return items


class InstrumentAutoImportLogsView(AutoImportLogsView):
    """ Logs of Auto-Imports of this instrument.
    """

    def __init__(self, context, request, **kwargs):
        AutoImportLogsView.__init__(self, context, request, **kwargs)
        del self.columns['Instrument']
        self.review_states[0]['columns'].remove('Instrument')
        self.contentFilter = {'portal_type': 'AutoImportLog',
                              'getInstrumentUID': self.context.UID(),
                              'sort_on': 'Created',
                              'sort_order': 'reverse'}

        self.icon = self.portal_url + "/++resource++bika.lims.images/instrumentcertification_big.png"
        self.title = self.context.translate(
            _("Auto Import Logs of %s" % self.context.Title()))
        self.context_actions = {}

        self.show_table_only = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.show_select_all_checkbox = False
        self.pagesize = 25


class InstrumentMultifileView(MultifileView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(InstrumentMultifileView, self).__init__(context, request)
        self.show_workflow_action_buttons = False
        self.title = self.context.translate(_("Instrument Files"))
        self.description = "Different interesting documents and files to be attached to the instrument"

        self.show_table_only = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.show_select_all_checkbox = False
        self.pagesize = 25


class ajaxGetInstrumentMethods(BrowserView):
    """ Returns the method assigned to the defined instrument.
        uid: unique identifier of the instrument
    """
    # Modified to return multiple methods after enabling multiple method
    # for intruments.
    def __call__(self):
        out = {
            "title": None,
            "instrument": None,
            "methods": [],
        }
        try:
            plone.protect.CheckAuthenticator(self.request)
        except Forbidden:
            return json.dumps(out)
        bsc = getToolByName(self, 'bika_setup_catalog')
        results = bsc(portal_type='Instrument', UID=self.request.get("uid", '0'))
        instrument = results[0] if results and len(results) == 1 else None
        if instrument:
            instrument_obj = instrument.getObject()
            out["title"] = instrument_obj.Title()
            out["instrument"] = instrument.UID
            # Handle multiple Methods per instrument
            methods = instrument_obj.getMethods()
            for method in methods:
                out["methods"].append({
                    "uid": method.UID(),
                    "title": method.Title(),
                })
        return json.dumps(out)


class InstrumentQCFailuresViewlet(ViewletBase):
    """ Print a viewlet showing failed instruments
    """

    index = ViewPageTemplateFile("templates/instrument_qc_failures_viewlet.pt")

    def __init__(self, context, request, view, manager=None):
        super(InstrumentQCFailuresViewlet, self).__init__(context, request, view, manager=manager)
        self.nr_failed = 0
        self.failed = {
            'out-of-date': [],
            'qc-fail': [],
            'next-test': [],
            'validation': [],
            'calibration': [],
        }

    def get_failed_instruments(self):
        """ Find all active instruments who have failed QC tests
            Find instruments whose certificate is out of date
            Find instruments which are disposed until next calibration test

            Return a dictionary with all info about expired/invalid instruments

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
