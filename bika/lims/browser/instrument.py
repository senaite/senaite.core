from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.content.instrumentmaintenancetask import InstrumentMaintenanceTaskStatuses as mstatus
from bika.lims.subscribers import doActionFor, skip
from operator import itemgetter
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements

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
        self.icon = "++resources++bika.lims.images/instrumentmaintenance_big.png"
        self.title = _("Instrument Maintenance")
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
        self.icon = "++resources++bika.lims.images/instrumentcalibration_big.png"
        self.title = _("Instrument Calibrations")
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
    
class InstrumentCertificationsView(BikaListingView):
    implements(IFolderContentsView, IViewView)
    
    def __init__(self, context, request):
        super(InstrumentCertificationsView, self).__init__(context, request)
        self.catalog = "portal_catalog"
        self.contentFilter = {
            'portal_type': 'InstrumentCertification',
        }
        self.context_actions = {_('Add'): 
                                {'url': 'createObject?type_name=InstrumentCertification',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.show_table_only = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25 
        self.form_id = "instrumentcertifications"
        self.icon = "++resources++bika.lims.images/instrumentcertification_big.png"
        self.title = _("Instrument Certifications")
        self.description = ""
        
        self.columns = {
            'Title': {'title': _('Certification Num'),
                      'index': 'sortable_title'},
            'getAgency': {'title': _('Agency')},
            'getDate': {'title': _('Date')},
            'getValidFrom': {'title': _('Valid from')},
            'getValidTo': {'title': _('Valid to')},
        }
        self.review_states = [
            {'id':'default',
             'title':_('All'),
             'contentFilter':{},
             'columns': [ 'Title',
                         'getAgency',
                         'getDate',
                         'getValidFrom',
                         'getValidTo']},
        ]
    
    def folderitems(self):
        items = BikaListingView.folderitems(self)
        outitems = []
        toshow = []
        for cer in self.context.getCertifications():
            toshow.append(cer.UID())
        for x in range (len(items)):
            if not items[x].has_key('obj'): continue            
            obj = items[x]['obj']
            if obj.UID() in toshow:
                items[x]['getAgency'] = obj.getAgency()
                items[x]['getDate'] = obj.getDate()
                items[x]['getValidFrom'] = obj.getValidFrom()
                items[x]['getValidTo'] = obj.getValidTo()
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
        self.icon = "++resources++bika.lims.images/instrumentvalidation_big.png"
        self.title = _("Instrument Validations")
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
        self.icon = "++resources++bika.lims.images/instrumentschedule_big.png"
        self.title = _("Instrument Scheduled Tasks")
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
