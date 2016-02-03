from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.interfaces import IVocabulary
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
try:
    from zope.component.hooks import getSite
except:
    # Plone < 4.3
    from zope.app.component.hooks import getSite


class RejectionWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/rejectionwidget",
        'helper_js': ("bika_widgets/rejectionwidget.js",),
        'helper_css': ("bika_widgets/rejectionwidget.css",),
    })

    security = ClassSecurityInfo()

    def rejectionOptionsList(self):
        "Return a sorted list with the options defined in bikasetup"
        plone = getSite()
        settings = plone.bika_setup
        # RejectionReasons will return something like:
        # [{'checkbox': u'on', 'textfield-2': u'b', 'textfield-1': u'c', 'textfield-0': u'a'}]
        if len(settings.RejectionReasons) > 0:
            reject_reasons = settings.RejectionReasons[0]
        else:
            return []
        sorted_keys = sorted(reject_reasons.keys())
        if 'checkbox' in sorted_keys:
            sorted_keys.remove('checkbox')
        # Building the list with the values only because the keys are not needed any more
        items = []
        for key in sorted_keys:
            items.append(reject_reasons[key])
        return items

registerWidget(RejectionWidget,
               title = "Rejection Widget",
               description = ('Widget to choose rejection reasons and set the rejection workflow'),
               )
