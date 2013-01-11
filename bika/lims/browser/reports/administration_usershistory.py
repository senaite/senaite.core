from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.browser.reports.selection_macros import SelectionMacrosView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
from bika.lims.utils import getUsers

class Report(BrowserView):
    implements(IViewView)
    default_template = ViewPageTemplateFile("templates/administration.pt")
    template = ViewPageTemplateFile("templates/administration_usershistory.pt")

    def __init__(self, context, request, report=None):
        super(Report, self).__init__(context, request)
        self.report = report
        self.selection_macros = SelectionMacrosView(self.context, self.request)

    def __call__(self):
        
        parms = []
        titles = []
        
        rt = getToolByName(self.context, 'portal_repository')
        mt = getToolByName(self.context, 'portal_membership')
        
        # Apply filters      
        self.contentFilter = {'portal_type': ('Department',
                                              'Method',
                                              'Analysis',
                                              'AnalysisCategory',
                                              'AnalysisProfile',
                                              'AnalysisRequest',
                                              'AnalysisService',
                                              'AnalysisSpec',
                                              'ARTemplate',
                                              'Attachment',
                                              'Batch',
                                              'Calculation',
                                              'Client',
                                              'Contact',
                                              'Container',
                                              'Department',
                                              'Instrument',
                                              'Manufacturer'
                                              'Method',
                                              'Preservation',
                                              'PriceList',
                                              'ReferenceAnalysis',
                                              'ReferenceDefinition',
                                              'ReferenceSample',
                                              'Sample',
                                              'SampleMatrix',
                                              'SamplePoint',
                                              'SampleType',
                                              'Supplier',
                                              'SupplierContact',
                                              'Worksheet',
                                              'WorksheetTemplate'
                                              )}                            
        
        val = self.selection_macros.parse_daterange(self.request,
                                                    'getDateCreated',
                                                    _('Date Created'))               
        if val:
            self.contentFilter[val['contentFilter'][0]] = val['contentFilter'][1]
            parms.append(val['parms'])
            titles.append(val['titles'])
            
                
        user = ''
        userfullname = ''
        if ('User' in self.request.form):
            user = self.request.form['User']
            userobj = mt.getMemberById(user)
            userfullname = userobj and userobj.getProperty('fullname') or ''
            parms.append({'title': _('User'), 'value': userfullname})
            titles.append(userfullname)
                                     
        # Query the catalog and store results in a dictionary             
        entities = self.bika_setup_catalog(self.contentFilter)
      
        if not entities:
            message = _("No historical actions matched your query")
            self.context.plone_utils.addPortalMessage(message, "error")
            return self.default_template()

        datalines = []
        tmpdatalines = {}
        footlines = {}
        
        for entity in entities:
            entity = entity.getObject()
            entitytype = _(entity.__class__.__name__)
            
            # Workflow states retrieval
            workflow = entity.workflow_history['bika_inactive_workflow']
            for action in workflow:                     
                actiontitle = _('Created')
                if not action['action'] or (action['action'] and action ['action']=='create'):
                    actiontitle=_('Created')
                elif action['action']=='deactivate':
                    actiontitle=_('Deactivated')
                else:
                    actiontitle=_(action['action'])                    
                
                if (user=='' or action['actor']==user):    
                    actorfullname = userfullname == '' and mt.getMemberById(user) or userfullname                              
                    dataline = {'EntityNameOrId':entity.title_or_id(),
                                'EntityAbsoluteUrl':entity.absolute_url(),
                                'EntityCreationDate':self.ulocalized_time(entity.CreationDate(),1),
                                'EntityModificationDate':self.ulocalized_time(entity.ModificationDate(),1),
                                'EntityType':entitytype,
                                'Action': actiontitle,
                                'ActionDate':action['time'],
                                'ActionDateStr':self.ulocalized_time(action['time'],1),
                                'ActionActor':action['actor'],
                                'ActionActorFullName':actorfullname,
                                'ActionComments':action['comments']
                                }
                    tmpdatalines[action['time']] = dataline         
            
            # History versioning retrieval
            history = rt.getHistoryMetadata(entity)
            if history:
                hislen = history.getLength(countPurged=False)
                for index in range(hislen):
                    meta=history.retrieve(index)['metadata']['sys_metadata']
                    metatitle = _(meta['comment'])                    
                    if (user=='' or meta['principal']==user):
                        actorfullname = userfullname == '' and mt.getMemberById(user) or userfullname    
                        dataline = {'EntityNameOrId':entity.title_or_id(),
                                    'EntityAbsoluteUrl':entity.absolute_url(),
                                    'EntityCreationDate':self.ulocalized_time(entity.CreationDate(),1),
                                    'EntityModificationDate':self.ulocalized_time(entity.ModificationDate(),1),
                                    'EntityType':entitytype,
                                    'Action': metatitle,
                                    'ActionDate':meta['timestamp'],
                                    'ActionDateStr':self.ulocalized_time(meta['timestamp'],1),
                                    'ActionActor':meta['principal'],
                                    'ActionActorFullName':actorfullname,
                                    'ActionComments':''
                                }
                        tmpdatalines[meta['timestamp']] = dataline 
                 
        # Sort datalines
        tmpkeys = tmpdatalines.keys()
        tmpkeys.sort(reverse=True)
        for index in range(len(tmpkeys)):
            datalines.append(tmpdatalines[tmpkeys[index]])
                    
        self.report_data = {'parameters': parms,
                            'datalines': datalines,
                            'footlines': footlines }       
        
        return {'report_title': _('Users history'),
                'report_data': self.template()}    
        