from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from plone.app.textfield import RichTextValue
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory
from Products.CMFCore.utils import getToolByName
import plone


class ARResultsInterpretationView(BrowserView):
    """ Renders the view for ResultsInterpration per Department
    """
    template = ViewPageTemplateFile("templates/analysisrequest_results_interpretation.pt")

    def __init__(self, context, request, **kwargs):
        super(ARResultsInterpretationView, self).__init__(context, request)
        self.context = context

    def __call__(self):
        wf = getToolByName(self.context, 'portal_workflow')
        mtool = getToolByName(self.context, 'portal_membership')
        self.allow_edit = mtool.checkPermission('Modify portal content',self.context)
        return self.template()

    def getText(self, department, mode='raw'):
        """ Returns the text saved for the selected department.
        """
        row = self.context.getResultsInterpretationByDepartment(department)
        rt = RichTextValue(row.get('richtext',''), 'text/plain', 'text/html')
        if mode=='output':
            return rt.output
        else:
            return rt.raw


class Save:
    """
        Saves the ResultsInterpretation by department to the AR
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        form = self.request.form
        plone.protect.CheckAuthenticator(form)

        # Save the results interpretation
        res = form.get('ResultsInterpretationDepts',[])
        self.context.setResultsInterpretationDepts(res)
