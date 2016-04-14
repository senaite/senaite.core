from AccessControl import ClassSecurityInfo
from Products.ATExtensions.ateapi import RecordsField
from Products.Archetypes.Registry import registerField
from Products.Archetypes.interfaces import IVocabulary
from Products.Archetypes.public import DisplayList
from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser.widgets import ReflexRuleWidget
import json


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
        })
    security = ClassSecurityInfo()

    def getAnalysisServiceForMethod(self):
        """
        Return a json dict with the different analysis services related
        to each method
        """
        # Getting all the matheods from the system
        relations = {}
        pc = getToolByName(self, 'portal_catalog')
        methods = [obj.getObject() for obj in pc(
                    portal_type='Method',
                    inactive_state='active')]
        for method in methods:
            # Get the analysis related to each method
            br = method.getBackReferences('AnalysisServiceMethods')
            analysiservices = {}
            for analysiservice in br:
                analysiservices[analysiservice.UID()] = {
                    'as_id': analysiservice.id,
                    'as_title': analysiservice.Title(),
                }
            # Make the json dict
            relations[method.UID()] = {
                'method_id': method.id,
                'method_tile': method.Title(),
                'analysisservices': analysiservices,
                'as_keys': analysiservices.keys(),
            }
        return json.dumps(relations)


registerField(ReflexRuleField,
              title="Reflex Rule Field",
              description="Used for storing Reflex Rules.",
              )
