from plone.app.contentmenu.interfaces import IContentMenuItem
from plone.app.contentmenu.menu import WorkflowSubMenuItem
from plone.memoize.instance import memoize
from zope.i18n import translate
from zope.interface import Interface
from bika.lims.interfaces import IBikaLIMS
from bika.lims import bikaMessageFactory as _



from cgi import escape

from plone.memoize.instance import memoize
from plone.app.content.browser.folderfactories import _allowedTypes
from plone.app.content.browser.interfaces import IContentsPage
from zope.interface import implements
from zope.component import getMultiAdapter, queryMultiAdapter

from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName, _checkPermission
from Products.CMFDynamicViewFTI.interface import ISelectableBrowserDefault
from Products.CMFPlone import PloneMessageFactory as PMF
from Products.CMFPlone import utils
from Products.CMFPlone.interfaces.structure import INonStructuralFolder
from Products.CMFPlone.interfaces.constrains import IConstrainTypes
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes

from plone.app.contentmenu import PloneMessageFactory as _
from plone.app.contentmenu.interfaces import IActionsMenu
from plone.app.contentmenu.interfaces import IActionsSubMenuItem
from plone.app.contentmenu.interfaces import IDisplayMenu
from plone.app.contentmenu.interfaces import IDisplaySubMenuItem
from plone.app.contentmenu.interfaces import IFactoriesMenu
from plone.app.contentmenu.interfaces import IFactoriesSubMenuItem
from plone.app.contentmenu.interfaces import IWorkflowMenu
from plone.app.contentmenu.interfaces import IWorkflowSubMenuItem

# BBB Zope 2.12
try:
    from zope.browsermenu.menu import BrowserMenu
    from zope.browsermenu.menu import BrowserSubMenuItem
except ImportError:
    from zope.app.publisher.browser.menu import BrowserMenu
    from zope.app.publisher.browser.menu import BrowserSubMenuItem

try:
    from Products.CMFPlacefulWorkflow import ManageWorkflowPolicies
except ImportError:
    from Products.CMFCore.permissions import ManagePortal as ManageWorkflowPolicies


class WorkflowSubMenuItem(WorkflowSubMenuItem):
    """ Add extra status/classes to workflow status menu
        when viewing cancelled/inactive objects """

    @property
    def extra(self):
        workflow = self.tools.workflow()
        state = self.context_state.workflow_state()
        stateTitle = self._currentStateTitle()

        if workflow.getInfoFor(self.context, 'cancellation_state', '') == 'cancelled':
            title2 = self.context.translate(_('Cancelled'))
            # cater for bika_one_state_workflow (always Active)
            if not stateTitle or \
               workflow.getInfoFor(self.context, 'review_state', '') == 'active':
                stateTitle = self.context.translate(_('Cancelled'))
            else:
                stateTitle = "%s (%s)" % (stateTitle,_(title2))
            return {'id'         : 'plone-contentmenu-workflow',
                    'class'      : 'state-cancelled',
                    'state'      : state,
                    'stateTitle' : stateTitle,}
        elif workflow.getInfoFor(self.context, 'inactive_state', '') == 'inactive':
            title2 = self.context.translate(_('Dormant'))
            # cater for bika_one_state_workflow (always Active)
            if not stateTitle or \
               (workflow.getInfoFor(self.context, 'review_state', '') in \
                                                    ('active', 'current')):
                stateTitle = self.context.translate(_('Dormant'))
            else:
                stateTitle = "%s (%s)" % (stateTitle,_(title2))
            return {'id'         : 'plone-contentmenu-workflow',
                    'class'      : 'state-inactive',
                    'state'      : state,
                    'stateTitle' : stateTitle,}
        else:
            return {'id'         : 'plone-contentmenu-workflow',
                    'class'      : 'state-%s' % state,
                    'state'      : state,
                    'stateTitle' : stateTitle,}

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
                    ordered.append(transitions[tid])
            transitions = ordered
        else:
            transitions = transitions.values()

        return transitions

##    @memoize
##    def _currentStateTitle(self):
##        wtool = self.tools.workflow()
##        workflows = wtool.getWorkflowsFor(self.context)
##        titles = []
##        if workflows:
##            for w in workflows:
##                state = wtool.getInfoFor(self.context, w.state_var, None)
##                if state in w.states:
##                    title = w.states[state].title or state
##                    titles.append(self.context.translate(title, domain="plone", context=self.request))
##        return u", ".join(titles)

class WorkflowMenu(BrowserMenu):
    implements(IWorkflowMenu)

    # BBB: These actions (url's) existed in old workflow definitions
    # but were never used. The scripts they reference don't exist in
    # a standard installation. We allow the menu to fail gracefully
    # if these are encountered.

    BOGUS_WORKFLOW_ACTIONS = (
        'content_hide_form',
        'content_publish_form',
        'content_reject_form',
        'content_retract_form',
        'content_show_form',
        'content_submit_form',
    )

    def getMenuItems(self, context, request):
        """Return menu item entries in a TAL-friendly form."""
        results = []

        locking_info = queryMultiAdapter((context, request), name='plone_lock_info')
        if locking_info and locking_info.is_locked_for_current_user():
            return []

        workflow = getToolByName(context, 'portal_workflow')
        workflowActions = workflow.listActionInfos(object=context)

        for action in workflowActions:
            if action['category'] != 'workflow':
                continue

            cssClass = 'kssIgnore'
            actionUrl = action['url']
            if actionUrl == "":
                actionUrl = '%s/content_status_modify?workflow_action=%s' % (context.absolute_url(), action['id'])
                cssClass = ''

            description = ''

            transition = action.get('transition', None)
            if transition is not None:
                description = transition.description

            for bogus in self.BOGUS_WORKFLOW_ACTIONS:
                if actionUrl.endswith(bogus):
                    if getattr(context, bogus, None) is None:
                        actionUrl = '%s/content_status_modify?workflow_action=%s' % (context.absolute_url(), action['id'],)
                        cssClass =''
                    break

            if action['allowed']:
                results.append({ 'title'       : action['title'],
                                 'description' : description,
                                 'action'      : actionUrl,
                                 'selected'    : False,
                                 'icon'        : None,
                                 'extra'       : {'id': 'workflow-transition-%s' % action['id'], 'separator': None, 'class': cssClass},
                                 'submenu'     : None,
                                 })

        url = context.absolute_url()

        if len(results) > 0:
            results.append({ 'title'        : PMF(u'label_advanced', default=u'Advanced...'),
                             'description'  : '',
                             'action'       : url + '/content_status_history',
                             'selected'     : False,
                             'icon'         : None,
                             'extra'        : {'id': 'advanced', 'separator': 'actionSeparator', 'class': 'kssIgnore'},
                             'submenu'      : None,
                            })

        if getToolByName(context, 'portal_placeful_workflow', None) is not None:
            if _checkPermission(ManageWorkflowPolicies, context):
                results.append({'title': PMF(u'workflow_policy',
                                           default=u'Policy...'),
                                'description': '',
                                'action': url + '/placeful_workflow_configuration',
                                'selected': False,
                                'icon': None,
                                'extra': {'id': 'policy', 'separator': None,
                                          'class': 'kssIgnore'},
                                'submenu': None,
                            })

        return results
