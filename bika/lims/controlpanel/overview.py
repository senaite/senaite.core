from bika.lims import bikaMessageFactory as _
from bika.lims import PMF

def categories(self):
    """see ../configure.zcml
    This adds the bika.lims category to controlpanel-overview.
    """
    return [
        {'id': 'Plone', 'title': PMF(u'Plone Configuration')},
        {'id': 'bika', 'title': _(u'Bika LIMS Configuration')},
        {'id': 'Products', 'title': PMF(u'Add-on Configuration')},
    ]
