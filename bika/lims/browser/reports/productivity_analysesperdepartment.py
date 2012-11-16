from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.browser.reports.selection_macros import SelectionMacrosView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements

class Report(BrowserView):
    implements(IViewView)
    default_template = ViewPageTemplateFile("templates/productivity.pt")
    template = ViewPageTemplateFile("templates/productivity_analysesperdepartment.pt")

    def __init__(self, context, request, report=None):
        super(Report, self).__init__(context, request)
        self.report = report
        self.selection_macros = SelectionMacrosView(self.context, self.request)

    def __call__(self):
        
        parms = []
        titles = []
        
        # Apply filters
        self.contentFilter = {'portal_type': 'Analysis'}
        val = self.selection_macros.parse_daterange(self.request,
                                                    'getDateRequested',
                                                    _('Date Requested')) 
        if val:
            self.contentFilter[val['contentFilter'][0]] = val['contentFilter'][1]
            parms.append(val['parms'])
            titles.append(val['titles'])

        val = self.selection_macros.parse_state(self.request,
                                                'bika_analysis_workflow',
                                                'getAnalysisState',
                                                _('Analysis State'))
        if val:
            self.contentFilter[val['contentFilter'][0]] = val['contentFilter'][1]
            parms.append(val['parms'])
            titles.append(val['titles'])
            
                                
        # Query the catalog and store results in a dictionary             
        analyses = self.bika_analysis_catalog(self.contentFilter)
        if not analyses:
            message = _("No analyses matched your query")
            self.context.plone_utils.addPortalMessage(message, "error")
            return self.default_template()

        datalines = {}
        footlines = {}
        totalcount = len(analyses)
        groupby = ('GroupingPeriod' in self.request.form) and self.request.form['GroupingPeriod'] or 'Day'
        for analysis in analyses:
            analysis = analysis.getObject()
            analysisservice = analysis.getService()          
            department = analysisservice.getDepartment().Title()           
            daterequested = analysis.getDateReceived()
                
            group = ''
            if groupby == 'Day':
                group = self.ulocalized_time(daterequested)                 
            elif groupby == 'Week':
                group = daterequested.strftime("%Y") + ", " + daterequested.strftime("%U")                                
            elif groupby == 'Month':
                group = daterequested.strftime("%B") + " " + daterequested.strftime("%Y")            
            elif groupby == 'Year':
                group = daterequested.strftime("%Y")
            else :
                group = self.ulocalized_time(daterequested)
            
            dataline = {'Group': group, 'Count': 0, 'Departments': {} }
            deptline = {'Department':department, 'Count':0}
            if (group in datalines):
                dataline = datalines[group]                
                if (department in dataline['Departments']):
                    deptline = dataline['Departments'][department]
            
            groupcount = dataline['Count']+1
            deptcount = deptline['Count']+1
            groupratio = float(groupcount)/float(totalcount)
            deptratio = float(deptcount)/float(groupcount)
                        
            dataline['Count'] = groupcount
            dataline['Ratio'] = groupratio
            dataline['RatioPercentage'] = ('{0:.0f}'.format(groupratio*100))+"%"
            
            deptline['Count'] = deptcount
            deptline['Ratio'] = deptratio
            deptline['RatioPercentage'] = ('{0:.0f}'.format(deptratio*100))+"%"
            
            dataline['Departments'][department]=deptline            
            datalines[group] = dataline                          
                
        # Footer total data      
        footline = {'Count': totalcount}
        footlines['Total'] = footline;
        
        self.report_data = {'parameters': parms,
                            'datalines': datalines,
                            'footlines': footlines }       
        
        return {'report_title': _('Analyses per department'),
                'report_data': self.template()}    
        