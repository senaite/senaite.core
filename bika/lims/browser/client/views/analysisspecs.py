from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.permissions import *
from bika.lims.utils import isActive
from bika.lims.utils import tmpID
from plone.app.layout.globals.interfaces import IViewView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from zope.interface import implements


class ClientAnalysisSpecsView(BikaListingView):
    implements(IViewView)

    def __init__(self, context, request):
        super(ClientAnalysisSpecsView, self).__init__(context, request)
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {
            'portal_type': 'AnalysisSpec',
            'sort_on': 'sortable_title',
            'getClientUID': context.UID(),
            'path': {
                "query": "/".join(context.getPhysicalPath()),
                "level": 0
            }
        }
        self.context_actions = {}

        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50
        self.form_id = "analysisspecs"

        self.icon = self.portal_url + "/++resource++bika.lims.images/analysisspec_big.png"
        self.title = self.context.translate(_("Analysis Specifications"))

        self.columns = {
            'Title': {'title': _('Title'),
                      'index': 'title'},
            'SampleType': {'title': _('Sample Type'),
                           'index': 'getSampleTypeTitle'},
        }
        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id': 'deactivate'}, ],
             'columns': ['Title', 'SampleType']},
            {'id': 'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id': 'activate'}, ],
             'columns': ['Title', 'SampleType']},
            {'id': 'all',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['Title', 'SampleType']},
        ]

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        checkPermission = mtool.checkPermission
        if isActive(self.context):
            if checkPermission(AddAnalysisSpec, self.context):
                self.context_actions[_('Add')] = \
                    {'url': 'createObject?type_name=AnalysisSpec',
                     'icon': '++resource++bika.lims.images/add.png'}
                #
                # @lemoene with the changes made in AR-specs, I dont know how much
                # sense this makes anymore.
                # if checkPermission("Modify portal content", self.context):
                #     self.context_actions[_('Set to lab defaults')] = \
                #         {'url': 'set_to_lab_defaults',
                #          'icon': '++resource++bika.lims.images/analysisspec.png'}
        return super(ClientAnalysisSpecsView, self).__call__()

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            items[x]['Title'] = obj.Title()
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                                           (items[x]['url'], items[x]['Title'])
            items[x]['SampleType'] = obj.getSampleType().Title() \
                if obj.getSampleType() else ""
        return items


class SetSpecsToLabDefaults(BrowserView):
    """ Remove all client specs, and add copies of all lab specs
    """

    def __call__(self):
        form = self.request.form
        bsc = getToolByName(self.context, 'bika_setup_catalog')

        # find and remove existing specs
        cs = bsc(portal_type='AnalysisSpec',
                 getClientUID=self.context.UID())
        if cs:
            self.context.manage_delObjects([s.id for s in cs])

        # find and duplicate lab specs
        ls = bsc(portal_type='AnalysisSpec',
                 getClientUID=self.context.bika_setup.bika_analysisspecs.UID())
        ls = [s.getObject() for s in ls]
        for labspec in ls:
            clientspec = _createObjectByType("AnalysisSpec", self.context,
                                             tmpID())
            clientspec.processForm()
            clientspec.edit(
                SampleType=labspec.getSampleType(),
                ResultsRange=labspec.getResultsRange(),
            )
        translate = self.context.translate
        message = _("Analysis specifications reset to lab defaults.")
        self.context.plone_utils.addPortalMessage(message, 'info')
        self.request.RESPONSE.redirect(self.context.absolute_url() +
                                       "/analysisspecs")
        return
