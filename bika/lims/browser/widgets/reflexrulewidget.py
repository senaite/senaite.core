from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.interfaces import IVocabulary
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from bika.lims.browser.widgets import RecordsWidget
import json

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

    def getReflexRuleSetup(self):
        """
        Return a json dict with all the setup data necessary to build the
        relations:
        - Relations between methods and analysis services options.
        - The current saved data
        """
        relations = {}
        # Getting all the methods from the system
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
        # Get the data saved in the object
        relations['saved_actions'] = {
            'method_uid': self.aq_parent.getMethod().UID(),
            'method_id': self.aq_parent.getMethod().id,
            'method_tile': self.aq_parent.getMethod().Title(),
            'actions': self.aq_parent.getReflexRules(),
            }
        return json.dumps(relations)

registerWidget(
    ReflexRuleWidget,
    title="Reflex Rule Widget",
    description=(
        'Widget to define different actions for an analysis services result'),
    )
