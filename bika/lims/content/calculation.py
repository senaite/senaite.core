from AccessControl import ClassSecurityInfo
from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser.fields import HistoryAwareReferenceField
from bika.lims.browser.fields import InterimFieldsField
from bika.lims.browser.widgets import RecordsWidget as BikaRecordsWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import ICalculation
from bika.lims.utils import to_utf8
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.CMFCore.permissions import ModifyPortalContent, View
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from zExceptions import Redirect
from zope.interface import implements
import sys
import re
import transaction


schema = BikaSchema.copy() + Schema((
    InterimFieldsField('InterimFields',
        schemata='Calculation',
        widget=BikaRecordsWidget(
            label=_("Calculation Interim Fields"),
            description=_(
                "Define interim fields such as vessel mass, dilution factors, "
                "should your calculation require them. The field title specified "
                "here will be used as column headers and field descriptors where "
                "the interim fields are displayed. If 'Apply wide' is enabled "
                "the field ill be shown in a selection box on the top of the "
                "worksheet, allowing to apply a specific value to all the "
                "corresponding fields on the sheet."),
        )
    ),
    HistoryAwareReferenceField('DependentServices',
        schemata='Calculation',
        required=1,
        multiValued=1,
        vocabulary_display_path_bound=sys.maxsize,
        allowed_types=('AnalysisService',),
        relationship='CalculationAnalysisService',
        referenceClass=HoldingReference,
        widget=ReferenceWidget(
            checkbox_bound=0,
            visible=False,
            label=_("Dependent Analyses"),
        ),
    ),
    TextField('Formula',
        schemata='Calculation',
        validators=('formulavalidator',),
        default_content_type='text/plain',
        allowable_content_types=('text/plain',),
        widget = TextAreaWidget(
            label=_("Calculation Formula"),
            description=_(
                "calculation_formula_description",
                "<p>The formula you type here will be dynamically calculated "
                "when an analysis using this calculation is displayed.</p>"
                "<p>To enter a Calculation, use standard maths operators,  "
                "+ - * / ( ), and all keywords available, both from other "
                "Analysis Services and the Interim Fields specified here, "
                "as variables. Enclose them in square brackets [ ].</p>"
                "<p>E.g, the calculation for Total Hardness, the total of "
                "Calcium (ppm) and Magnesium (ppm) ions in water, is entered "
                "as [Ca] + [Mg], where Ca and MG are the keywords for those "
                "two Analysis Services.</p>"),
            )
    ),
))

schema['title'].widget.visible = True
schema['title'].schemata = 'Description'
schema['description'].widget.visible = True
schema['description'].schemata = 'Description'


class Calculation(BaseFolder, HistoryAwareMixin):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema
    implements(ICalculation)

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def setInterimFields(self, value):
        new_value = []

        for x in range(len(value)):
            row = dict(value[x])
            keys = row.keys()
            if 'value' not in keys:
                row['value'] = 0
            new_value.append(row)

        self.getField('InterimFields').set(self, new_value)

    def setFormula(self, Formula=None):
        """Set the Dependent Services from the text of the calculation Formula
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        if Formula is None:
            self.setDependentServices(None)
            self.getField('Formula').set(self, Formula)
        else:
            DependentServices = []
            keywords = re.compile(r"\[([^\.^\]]+)\]").findall(Formula)
            for keyword in keywords:
                service = bsc(portal_type="AnalysisService",
                              getKeyword=keyword)
                if service:
                    DependentServices.append(service[0].getObject())

            self.getField('DependentServices').set(self, DependentServices)
            self.getField('Formula').set(self, Formula)

    def getMinifiedFormula(self):
        """Return the current formula value as text.
        The result will have newlines and additional spaces stripped out.
        """
        value = " ".join(self.getFormula().splitlines())
        return value

    def getCalculationDependencies(self, flat=False, deps=None):
        """ Recursively calculates all dependencies of this calculation.
            The return value is dictionary of dictionaries (of dictionaries....)

            {service_UID1:
                {service_UID2:
                    {service_UID3: {},
                     service_UID4: {},
                    },
                },
            }

            set flat=True to get a simple list of AnalysisService objects
        """
        if deps == None:
            deps = [] if flat == True else {}

        for service in self.getDependentServices():
            calc = service.getCalculation()
            if calc:
                calc.getCalculationDependencies(flat, deps)
            if flat:
                deps.append(service)
            else:
                deps[service.UID()] = {}
        return deps

    def getCalculationDependants(self):
        """Return a flat list of services who's calculations depend on this."""
        deps = []
        for service in self.getBackReferences('AnalysisServiceCalculation'):
            calc = service.getCalculation()
            if calc and calc.UID() != self.UID():
                calc.getCalculationDependants(deps)
            deps.append(service)
        return deps

    def workflow_script_activate(self):
        wf = getToolByName(self, 'portal_workflow')
        pu = getToolByName(self, 'plone_utils')
        # A calculation cannot be re-activated if services it depends on
        # are deactivated.
        services = self.getDependentServices()
        inactive_services = []
        for service in services:
            if wf.getInfoFor(service, "inactive_state") == "inactive":
                inactive_services.append(service.Title())
        if inactive_services:
            msg = _("Cannot activate calculation, because the following "
                    "service dependencies are inactive: ${inactive_services}",
                    mapping={'inactive_services': safe_unicode(", ".join(inactive_services))})
            pu.addPortalMessage(msg, 'error')
            transaction.get().abort()
            raise WorkflowException

    def workflow_script_deactivate(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        pu = getToolByName(self, 'plone_utils')
        # A calculation cannot be deactivated if active services are using it.
        services = bsc(portal_type="AnalysisService", inactive_state="active")
        calc_services = []
        for service in services:
            service = service.getObject()
            calc = service.getCalculation()
            if calc and calc.UID() == self.UID():
                calc_services.append(service.Title())
        if calc_services:
            msg = _('Cannot deactivate calculation, because it is in use by the '
                    'following services: ${calc_services}',
                    mapping={'calc_services': safe_unicode(", ".join(calc_services))})
            pu.addPortalMessage(msg, 'error')
            transaction.get().abort()
            raise WorkflowException

registerType(Calculation, PROJECTNAME)
