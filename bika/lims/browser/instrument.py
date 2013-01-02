from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
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
        self.show_table_only = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25 
        self.form_id = "instrumentmaintenance"
        self.icon = "++resources++bika.lims.images/instrumentmaintenance_big.png"
        self.title = _("Instrument Maintenance")
        self.description = ""
        
        self.columns = {
            'Title': {'title': _('Task'),
                      'index': 'sortable_title'},
            'getDownFrom': {'title': _('Down from')},
            'getDownTo': {'title': _('Down to')},
            'getMaintainer': {'title': _('Maintainer')},
            'getCost': {'title': _('Cost')},
        }
        self.review_states = [
            {'id':'default',
             'title':_('All'),
             'contentFilter':{},
             'columns': [ 'Title',
                         'getDownFrom',
                         'getDownTo',
                         'getMaintainer',
                         'getCost']},
        ]
    
    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range (len(items)):
            if not items[x].has_key('obj'): continue
            
            obj = items[x]['obj']
            items[x]['getDownFrom'] = obj.getDownFrom()
            items[x]['getDownTo'] = obj.getDownTo()
            items[x]['getMaintainer'] = obj.getMaintainer()
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])
                 
        return items

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
        for x in range (len(items)):
            if not items[x].has_key('obj'): continue
            
            obj = items[x]['obj']
            items[x]['getDownFrom'] = obj.getDownFrom()
            items[x]['getDownTo'] = obj.getDownTo()
            items[x]['getCalibrator'] = obj.getCalibrator()
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])
                 
        return items
    
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
        for x in range (len(items)):
            if not items[x].has_key('obj'): continue
            
            obj = items[x]['obj']
            items[x]['getAgency'] = obj.getAgency()
            items[x]['getDate'] = obj.getDate()
            items[x]['getValidFrom'] = obj.getValidFrom()
            items[x]['getValidTo'] = obj.getValidTo()
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])
                 
        return items

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
        for x in range (len(items)):
            if not items[x].has_key('obj'): continue
            
            obj = items[x]['obj']
            items[x]['getDownFrom'] = obj.getDownFrom()
            items[x]['getDownTo'] = obj.getDownTo()
            items[x]['getValidator'] = obj.getValidator()
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])
                 
        return items
