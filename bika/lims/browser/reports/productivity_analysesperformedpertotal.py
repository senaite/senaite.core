from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.browser.reports.selection_macros import SelectionMacrosView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements

class Report(BrowserView):
    implements(IViewView)
    default_template = ViewPageTemplateFile("templates/productivity.pt")
    template = ViewPageTemplateFile("templates/productivity_analysesperformedpertotal.pt")

    def __init__(self, context, request, report=None):
        super(Report, self).__init__(context, request)
        self.report = report
        self.selection_macros = SelectionMacrosView(self.context, self.request)

    def __call__(self):
        
        parms = []
        titles = []
        
        # Apply filters
        self.contentFilter = {'portal_type': 'Analysis' }
        val = self.selection_macros.parse_daterange(self.request,
                                                    'getDateRequested',
                                                    _('Date Requested')) 
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
        totalpublishedcount = 0
        groupby = ('GroupingPeriod' in self.request.form) and self.request.form['GroupingPeriod'] or 'Day'
        for analysis in analyses:
            analysis = analysis.getObject()
            ankeyword = analysis.getKeyword()
            antitle = analysis.getServiceTitle()          
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
            
            dataline = {'Group': group, 'Count': 0, 'Published': 0, 'Analyses': {} }
            anline = {'Analysis':antitle, 'Count': 0, 'Published': 0 }
            if (group in datalines):
                dataline = datalines[group]                
                if (ankeyword in dataline['Analyses']):
                    anline = dataline['Analyses'][ankeyword]
            
            grouptotalcount = dataline['Count']+1
            grouppublishedcount = dataline['Published']
            
            anltotalcount = anline['Count']+1
            anlpublishedcount = anline['Published']
            
            workflow = getToolByName(self.context, 'portal_workflow')
            arstate = workflow.getInfoFor(analysis.aq_parent, 'review_state', '')
            if (arstate == 'published'):
                anlpublishedcount += 1
                grouppublishedcount += 1
                totalpublishedcount += 1
                
            groupratio = float(grouppublishedcount)/float(grouptotalcount)
            anlratio = float(anlpublishedcount)/float(anltotalcount)
            
            dataline['Count'] = grouptotalcount
            dataline['Published'] = grouppublishedcount
            dataline['PublishedRatio'] = groupratio
            dataline['PublishedRatioPercentage'] = ('{0:.0f}'.format(groupratio*100))+"%"
            
            anline['Count'] = anltotalcount
            anline['Published'] = anlpublishedcount
            anline['PublishedRatio'] = anlratio
            anline['PublishedRatioPercentage'] = ('{0:.0f}'.format(anlratio*100))+"%"
            
            dataline['Analyses'][ankeyword]=anline            
            datalines[group] = dataline                          
                
        # Footer total data      
        totalratio = float(totalpublishedcount)/float(totalcount)
        footline = {'Count': totalcount,
                    'Published': totalpublishedcount,
                    'PublishedRatio': totalratio,
                    'PublishedRatioPercentage': ('{0:.0f}'.format(totalratio*100))+"%" }
        footlines['Total'] = footline;
        
        self.report_data = {'parameters': parms,
                            'datalines': datalines,
                            'footlines': footlines }       
        
        return {'report_title': _('Analyses performed as % of total'),
                'report_data': self.template()}    
        