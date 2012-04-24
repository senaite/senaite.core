from bika.lims import bikaMessageFactory as _
from bika.lims import PMF

def categories(self):
    """Monkey patch
    see ../configure.zcml
    """
    return [
        {'id': 'Plone', 'title': PMF(u'Plone Configuration')},
        {'id': 'bika', 'title': _(u'Bika LIMS Configuration')},
        {'id': 'Products', 'title': PMF(u'Add-on Configuration')},
    ]
