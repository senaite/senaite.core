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
        'subfields': ('analysisservice',),
        'required_subfields': ('analysisservice', ),
        'subfield_labels': {'analysisservice': _('Analysis Service'), },
        'subfield_types': {'analysisservice': 'selection', },
        'subfield_sizes': {'analysisservice': 1, },
        'subfield_validators': {},
        'subfield_vocabularies': {
            'analysisservice': DisplayList([('', '')]),
            },
        'widget': ReflexRuleWidget,
        'subfield_validators': {'analysisservice': 'reflexrulevalidator', },
        })
    security = ClassSecurityInfo()


registerField(ReflexRuleField,
              title="Reflex Rule Field",
              description="Used for storing Reflex Rules.",
              )
