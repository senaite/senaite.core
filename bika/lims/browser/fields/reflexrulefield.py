from AccessControl import ClassSecurityInfo
from Products.ATExtensions.ateapi import RecordsField
from Products.Archetypes.Registry import registerField
from Products.Archetypes.interfaces import IVocabulary
from Products.Archetypes.public import DisplayList
from zope.interface import implements
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser.widgets import ReflexRuleWidget


class ReflexRuleField(RecordsField):

    """The field to manage reflex rule's data """
    _properties = RecordsField._properties.copy()
    _properties.update({
        'fixedSize': 0,
        'minimalSize': 0,
        'maximalSize': 9999,
        'type': 'ReflexRule',
        'subfields': ('rulesset',),
        'subfield_labels': {'rulesset': _('Define the sets of actions'), },
        'widget': ReflexRuleWidget,
        'subfield_validators': {'rulesset': 'reflexrulevalidator', },
        })
    security = ClassSecurityInfo()


registerField(ReflexRuleField,
              title="Reflex Rule Field",
              description="Used for storing Reflex Rules.",
              )
