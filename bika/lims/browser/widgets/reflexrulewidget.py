from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.interfaces import IVocabulary
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from bika.lims.browser.widgets import RecordsWidget

try:
    from zope.component.hooks import getSite
except:
    # Plone < 4.3
    from zope.app.component.hooks import getSite


class ReflexRuleWidget(RecordsWidget):
    _properties = RecordsWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/reflexrulewidget",
        'helper_js': (
            "bika_widgets/recordswidget.js",
            "bika_widgets/reflexrulewidget.js",),
        'helper_css': (
            "bika_widgets/recordswidget.css",
            "bika_widgets/reflexrulewidget.css",),
        'label': '',
        'description':
            'Add actions for each analysis service belonging to the'
            ' selected method',
        'allowDelete': True,
    })

    security = ClassSecurityInfo()


registerWidget(
    ReflexRuleWidget,
    title="Reflex Rule Widget",
    description=(
        'Widget to define different actions for an analysis services result'),
    )
