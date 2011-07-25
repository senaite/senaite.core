from cgi import escape

from plone.memoize.instance import memoize
from plone.app.content.browser.folderfactories import _allowedTypes
from plone.app.content.browser.interfaces import IContentsPage
from zope.interface import implements
from zope.component import getMultiAdapter, queryMultiAdapter

from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.interface import ISelectableBrowserDefault
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

##class FactoriesMenu(BrowserMenu):
##    implements(IFactoriesMenu)
##
##    def getMenuItems(self, context, request):
##
##        return ()
