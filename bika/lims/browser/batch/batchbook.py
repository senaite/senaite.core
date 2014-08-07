from operator import itemgetter
from AccessControl import getSecurityManager
from Products.CMFPlone import PloneMessageFactory
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.permissions import EditResults, AddAnalysisRequest
from Products.CMFCore.utils import getToolByName

import re


class BatchBookView(BikaListingView):

    def __init__(self, context, request):
        super(BatchBookView, self).__init__(context, request)
        self.icon = self.portal_url + \
            "/++resource++bika.lims.images/batchbook_big.png"
        self.context_actions = {}
        self.contentFilter = {"sort_on":"created"}
        self.title = context.Title()
        self.Description = context.Description()
        self.show_select_all_checkbox = True
        self.show_sort_column = False
        self.show_column_toggles = True
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 0
        self.form_id = "list"
        self.page_start_index = 0
        self.show_categories = True
        self.expand_all_categories = True

        self.insert_submit_button = False

        request.set('disable_plone.rightcolumn', 1)

        self.columns = {
            'AnalysisRequest': {
                'title': _('Analysis Request'),
                'index': 'id',
                'sortable': True,
            },
            'Batch': {
                'title': _('Batch'),
                'sortable': True,
            },
            'Sub-group': {
                'title': _('Sub-group'),
                'sortable': True,
            },
            'created': {
                'title': PloneMessageFactory('Date Created'),
                'index': 'created',
                'toggle': False,
            },
            'state_title': {
                'title': _('State'),
                'index': 'review_state'
            },
        }

        self.review_states = [
            {'id': 'default',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['AnalysisRequest',
                         'Batch',
                         'Sub-group',
                         'created',
                         'state_title'],
             },
        ]

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        checkPermission = mtool.checkPermission
        self.allow_edit = checkPermission("Modify portal content", self.context)

        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.checkPermission(AddAnalysisRequest, self.portal):
            # This is permitted from the global permission above, AddAnalysisRequest.
            review_states = []
            for review_state in self.review_states:
                review_state.get('custom_actions', []).extend(
                    [{'id': 'copy_to_new',
                      'title': _('Copy to new'),
                      'url': 'workflow_action?action=copy_to_new'}, ])
                review_states.append(review_state)
            self.review_states = review_states

        return super(BatchBookView, self).__call__()

    def folderitems(self):
        """Accumulate a list of all AnalysisRequest objects contained in
        this Batch, as well as those which are inherited.
        """
        wf = getToolByName(self.context, 'portal_workflow')
        schema = self.context.Schema()

        ars = []

        for o in schema.getField('InheritedObjects').get(self.context):
            if o.portal_type == 'AnalysisRequest':
                if o not in ars:
                    ars.append(o)
            elif o.portal_type == 'Batch':
                for ar in o.getAnalysisRequests():
                    if ar not in ars:
                        ars.append(ar)

        for ar in self.context.getAnalysisRequests():
            if ar not in ars:
                ars.append(ar)

        self.categories = []
        analyses = {}
        items = []
        services = []
        keywords = []
        for ar in ars:
            analyses[ar.id] = []
            for analysis in ar.getAnalyses(full_objects=True):
                analyses[ar.id].append(analysis)
                service = analysis.getService()
                if service.getKeyword() not in keywords:
                    # we use a keyword check, because versioned services are !=.
                    keywords.append(service.getKeyword())
                    services.append(service)

            batchlink = ""
            batch = ar.getBatch()
            if batch:
                batchlink = "<a href='%s'>%s</a>" % (
                    batch.absolute_url(), batch.Title())

            arlink = "<a href='%s'>%s</a>" % (
                ar.absolute_url(), ar.Title())

            subgroup = ar.Schema()['SubGroup'].get(ar)
            sub_title = subgroup.Title() if subgroup else 'No Subgroup'
            sub_sort = subgroup.getSortKey() if subgroup else '1'
            sub_class = re.sub(r"[^A-Za-z\w\d\-\_]", '', sub_title)

            if [sub_sort, sub_title] not in self.categories:
                self.categories.append([sub_sort, sub_title])

            review_state = wf.getInfoFor(ar, 'review_state')
            state_title = wf.getTitleForStateOnType(
                review_state, 'AnalysisRequest')

            item = {
                'obj': ar,
                'id': ar.id,
                'uid': ar.UID(),
                'category': sub_title,
                'title': ar.Title(),
                'type_class': 'contenttype-AnalysisRequest',
                'url': ar.absolute_url(),
                'relative_url': ar.absolute_url(),
                'view_url': ar.absolute_url(),
                'created': self.ulocalized_time(ar.created()),
                'sort_key': ar.created(),
                'replace': {
                    'Batch': batchlink,
                    'AnalysisRequest': arlink,
                    'Sub-group': sub_title,
                },
                'before': {},
                'after': {},
                'choices': {},
                'class': {'Batch': 'Title'},
                'state_class': 'state-active subgroup_{0}'.format(sub_class) if sub_class else 'state-active',
                'allow_edit': [],
                'Batch': '',
                'Sub-group': '',
                'AnalysisRequest': '',
                'state_title': state_title,
            }
            items.append(item)

        unitstr = '<em class="discreet" style="white-space:nowrap;">%s</em>'
        checkPermission = getSecurityManager().checkPermission

        # Insert columns for analyses
        for service in services:
            keyword = service.getKeyword()
            self.columns[keyword] = {
                'title': service.ShortTitle if service.ShortTitle else service.title,
                'sortable': True
            }
            self.review_states[0]['columns'].insert(
                len(self.review_states[0]['columns']) - 1, keyword)

            # Insert values for analyses
            for i, item in enumerate(items):
                for analysis in analyses[item['id']]:
                    if keyword not in items[i]:
                        items[i][keyword] = ''
                    if analysis.getKeyword() != keyword:
                        continue

                    edit = checkPermission(EditResults, analysis)
                    calculation = analysis.getService().getCalculation()
                    if self.allow_edit and edit and not calculation:
                        items[i]['allow_edit'].append(keyword)
                        if not self.insert_submit_button:
                            self.insert_submit_button = True

                    value = analysis.getResult()
                    items[i][keyword] = value
                    items[i]['class'][keyword] = ''

                    if value or (edit and not calculation):

                        unit = unitstr % service.getUnit()
                        items[i]['after'][keyword] = unit

                if keyword not in items[i]['class']:
                    items[i]['class'][keyword] = 'empty'
        if self.insert_submit_button:
            custom_actions = self.review_states[0].get('custom_actions', [])
            custom_actions.append({'id': 'submit'})
            self.review_states[0]['custom_actions'] = custom_actions

        self.categories.sort()
        self.categories = [x[1] for x in self.categories]

        items = sorted(items, key=itemgetter("sort_key"))

        return items
