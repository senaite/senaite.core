from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.utils import to_utf8
from plone.app.contentmenu.menu import WorkflowSubMenuItem as _WorkflowSubMenuItem
from Products.CMFCore.utils import getToolByName

try:
    from Products.CMFPlacefulWorkflow import ManageWorkflowPolicies
except ImportError:
    from Products.CMFCore.permissions import ManagePortal as ManageWorkflowPolicies


class WorkflowSubMenuItem(_WorkflowSubMenuItem):

    """ Add extra status/classes to workflow status menu
when viewing cancelled/inactive objects """

    @property
    def extra(self):
        workflow = self.tools.workflow()
        state = self.context_state.workflow_state()
        stateTitle = self._currentStateTitle()

        if workflow.getInfoFor(self.context, 'cancellation_state', '') == 'cancelled':
            title2 = t(_('Cancelled'))
            # cater for bika_one_state_workflow (always Active)
            if not stateTitle or \
               workflow.getInfoFor(self.context, 'review_state', '') == 'active':
                stateTitle = t(_('Cancelled'))
            else:
                stateTitle = "%s (%s)" % (stateTitle, _(title2))
            return {'id': 'plone-contentmenu-workflow',
                    'class': 'state-cancelled',
                    'state': state,
                    'stateTitle': stateTitle, }
        elif workflow.getInfoFor(self.context, 'inactive_state', '') == 'inactive':
            title2 = t(_('Dormant'))
            # cater for bika_one_state_workflow (always Active)
            if not stateTitle or \
               (workflow.getInfoFor(self.context, 'review_state', '') in
                                                    ('active', 'current')):
                stateTitle = t(_('Dormant'))
            else:
                stateTitle = "%s (%s)" % (stateTitle, _(title2))
            return {'id': 'plone-contentmenu-workflow',
                    'class': 'state-inactive',
                    'state': state,
                    'stateTitle': stateTitle, }
        else:
            return {'id': 'plone-contentmenu-workflow',
                    'class': 'state-%s' % state,
                    'state': state,
                    'stateTitle': stateTitle, }

    def _transitions(self):
        workflow = getToolByName(self.context, 'portal_workflow')
        return workflow.listActionInfos(object=self.context, max=1)

    def get_workflow_actions(self):
        """ Compile a list of possible workflow transitions for items
        in this Table.
        """

        # return empty list if selecting checkboxes are disabled
        if not self.show_select_column:
            return []

        workflow = getToolByName(self.context, 'portal_workflow')

        state = self.request.get('review_state', 'default')
        review_state = [i for i in self.review_states if i['id'] == state][0]

        # get all transitions for all items.
        transitions = {}
        for obj in [i.get('obj', '') for i in self.items]:
            obj = hasattr(obj, 'getObject') and \
                obj.getObject() or \
                obj
            for t in workflow.getTransitionsFor(obj):
                transitions[t['id']] = t

        # if there is a review_state['some_state']['transitions'] attribute
        # on the BikaListingView, the list is restricted to and ordered by
        # these transitions
        if 'transitions' in review_state:
            ordered = []
            for transition_dict in review_state['transitions']:
                if transition_dict['id'] in transitions:
                    tid = transition_dict['id']
                    ordered.append(transitions[tid])
            transitions = ordered
        else:
            transitions = transitions.values()

        return transitions

# @memoize
# def _currentStateTitle(self):
# wtool = self.tools.workflow()
# workflows = wtool.getWorkflowsFor(self.context)
# titles = []
# if workflows:
# for w in workflows:
# state = wtool.getInfoFor(self.context, w.state_var, None)
# if state in w.states:
# title = w.states[state].title or state
# titles.append(t(title, domain="plone", context=self.request))
# return u", ".join(titles)
