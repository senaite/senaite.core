from zope.component import getMultiAdapter
from plone.app.contentmenu.menu import FactoriesMenu
from plone.app.portlets.portlets.navigation import Renderer
from bika.lims import PMF
from bika.lims import bikaMessageFactory as _


def overview_controlpanel_categories(self):
    """see ../configure.zcml
    This adds the bika.lims category to controlpanel-overview.
    """
    return [
        {'id': 'Plone', 'title': PMF(u'Plone Configuration')},
        {'id': 'bika', 'title': _(u'Bika LIMS Configuration')},
        {'id': 'Products', 'title': PMF(u'Add-on Configuration')},
    ]


from plone.app.portlets.portlets.navigation import Renderer
from bika.lims import PMF

def createNavTree(self):
    """see ./configure.zcml
    This chops translated strings (from plone domain) into navtree titles.
    Only goes 2 levels down the tree.
    """
    data = self.getNavTree()

    q = ["data['children']"]
    while q:
        for i in range(len(eval(q[0]))):
            try:
                exec("%s[%s]['Title'] = "
                     "self.context.translate(PMF(%s[%s]['Title']))" %(
                         q[0], i, q[0], i))
            except:
                pass
            if eval("%s[%s]" % (q[0], i)).get('children', []):
                q.append(q[0] + "[%s]['children']"%i)
        del(q[0])

    bottomLevel = self.data.bottomLevel or self.properties.getProperty('bottomLevel', 0)

    if bottomLevel < 0:
        # Special case where navigation tree depth is negative
        # meaning that the admin does not want the listing to be displayed
        return self.recurse([], level=1, bottomLevel=bottomLevel)
    else:
        return self.recurse(children=data.get('children', []), level=1, bottomLevel=bottomLevel)


def contentmenu_factories_available(self):
    if hasattr(self._addContext(), 'portal_type') \
    and self._addContext().portal_type in [
        'Batch',
        'Client',
        'AnalysisRequest',
        'Worksheet',
        'Sample',
        'AnalysisCategory',
        'AnalysisProfile',
        'ARTemplate',
        'AnalysisService',
        'AnalysisSpec',
        'Attachment',
        'Calculation',
        'Instrument',
        'LabContact',
        'Laboratory',
        'Method',
        'Department',
        'ReferenceDefinition',
        'ReportFolder',
        'SampleType',
        'SamplePoint',
        'WorksheetTemplate',
        'LabProduct',
        'ReferenceSample',
        'Preservation'
    ]:
        return False
    else:
        itemsToAdd = self._itemsToAdd()
        showConstrainOptions = self._showConstrainOptions()
        if self._addingToParent() and not self.context_state.is_default_page():
            return False
        return (len(itemsToAdd) > 0 or showConstrainOptions)
