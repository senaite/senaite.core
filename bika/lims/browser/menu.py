from plone.app.contentmenu.interfaces import IContentMenuItem
from plone.app.contentmenu.menu import WorkflowSubMenuItem
from plone.memoize.instance import memoize
from zope.i18n import translate
from zope.interface import Interface
from bika.lims.interfaces import IBikaLIMS
from bika.lims import bikaMessageFactory as _

class WorkflowSubMenuItem(WorkflowSubMenuItem):
    """ Add extra status/classes to workflow status menu
        when viewing cancelled/inactive objects """

    @property
    def extra(self):
        workflow = self.tools.workflow()
        state = self.context_state.workflow_state()
        stateTitle = self._currentStateTitle()

        if workflow.getInfoFor(self.context, 'cancellation_state', '') == 'cancelled':
            title2 = workflow.getTitleForStateOnType('cancelled', self.context.portal_type)
            return {'id'         : 'plone-contentmenu-workflow',
                    'class'      : 'state-cancelled',
                    'state'      : state,
                    'stateTitle' : "%s (%s)" % (stateTitle,_(title2)),}
        elif workflow.getInfoFor(self.context, 'inactive_state', '') == 'inactive':
            title2 = workflow.getTitleForStateOnType('inactive', self.context.portal_type)
            return {'id'         : 'plone-contentmenu-workflow',
                    'class'      : 'state-inactive',
                    'state'      : state,
                    'stateTitle' : "%s (%s)" % (stateTitle,_(title2)),}
        else:
            return {'id'         : 'plone-contentmenu-workflow',
                    'class'      : 'state-%s' % state,
                    'state'      : state,
                    'stateTitle' : stateTitle,}

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
##                    titles.append(translate(title, domain="plone", context=self.request))
##        return u", ".join(titles)
