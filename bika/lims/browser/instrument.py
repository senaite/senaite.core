from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.interfaces import IInstrumentMaintenanceFolder
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