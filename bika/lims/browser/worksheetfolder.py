from DateTime import DateTime
from DocumentTemplate import sequence
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.interfaces import IWorksheet
from bika.lims.browser.analyses import AnalysesView
from plone.app.content.browser.interfaces import IFolderContentsView
from zope.interface import implements
import plone, json

class WorksheetFolderView(BikaListingView):
    contentFilter = {'portal_type': 'Worksheet',
                              'sort_on':'id',
                              'sort_order': 'reverse'}
    content_add_actions = {_('Worksheet'): "worksheet_add"}
    show_editable_border = False
    show_table_only = False
    show_sort_column = False
    show_select_row = False
    show_select_all_checkbox = True
    show_select_column = True
    pagesize = 50

    columns = {
           'Title': {'title': _('Worksheet Number')},
           'Owner': {'title': _('Owner')},
           'Analyst': {'title': _('Analyst')},
           'Template': {'title': _('Template')},
           'Analyses': {'title': _('Analyses')},
           'CreationDate': {'title': _('Creation Date')},
           'state_title': {'title': _('State')},
          }
    review_states = [
                {'title': _('All'), 'id':'all',
                 'contentFilter': {'portal_type': 'Worksheet'},
                 'columns':['Title',
                            'Owner',
                            'Analyst',
                            'Template',
                            'Analyses',
                            'CreationDate',
                            'state_title']},
                {'title': _('Worksheet Open'), 'id':'open',
                 'contentFilter': {'review_state':'open'},
                 'columns':['Title',
                            'Owner',
                            'Analyst',
                            'Template',
                            'Analyses',
                            'CreationDate',
                            'state_title']},
                {'title': _('To Be Verified'), 'id':'to_be_verified',
                 'columns':['Title',
                            'Owner',
                            'Analyst',
                            'Template',
                            'Analyses',
                            'CreationDate',
                            'state_title']},
                {'title': _('Verified'), 'id':'verified',
                 'columns':['Title',
                            'Owner',
                            'Analyst',
                            'Template',
                            'Analyses',
                            'CreationDate',
                            'state_title']},
                # XXX reject workflow - one transition, to set a flag
                # "has been rejected in the past" on this worksheet.
                {'title': _('Rejected'), 'id':'rejected',
                 'contentFilter': {'review_state':'open'},
                 'columns':['Title',
                            'Owner',
                            'Analyst',
                            'Template',
                            'Analyses',
                            'CreationDate',
                            'state_title']}
                  ]
    def __init__(self, context, request):
        super(WorksheetFolderView, self).__init__(context, request)
        self.title = "%s: %s" % (self.context.Title(), _("Worksheets"))
        self.description = ""

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        mtool = getToolByName(self, 'portal_membership')
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['Title'] = obj.Title()
            items[x]['Owner'] = obj.getOwnerTuple()[1]
            analyst = obj.getAnalyst()
            items[x]['Analyst'] = analyst and \
                mtool.getMemberById(analyst).getProperty('fullname') or ''
            items[x]['Template'] = obj.getWorksheetTemplate() and \
                obj.getWorksheetTemplate().Title() or ''
            items[x]['Analyses'] = len(obj.getAnalyses())
            items[x]['CreationDate'] = obj.CreationDate() and \
                 self.context.toLocalizedTime(obj.CreationDate(), long_format = 0) or ''
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])

        return items
