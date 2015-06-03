from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import ModifyPortalContent, View
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.ATExtensions.ateapi import RecordsField as RecordsField
from bika.lims.browser.fields import HistoryAwareReferenceField
from bika.lims.browser.widgets import RecordsWidget
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import PROJECTNAME
import sys
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.interfaces import IMethod
from bika.lims.utils import to_utf8
from zope.interface import implements

schema = BikaSchema.copy() + Schema((
    # Method ID should be unique, specified on MethodSchemaModifier
    StringField('MethodID',
        searchable=1,
        required=0,
        validators=('uniquefieldvalidator',),
        widget=StringWidget(
            visible={'view': 'visible', 'edit': 'visible'},
            label=_('Method ID'),
            description=_('Define an identifier code for the method. It must be unique.'),
        ),
    ),
    TextField('Instructions',
        default_content_type = 'text/plain',
        allowed_content_types= ('text/plain', ),
        default_output_type="text/plain",
        widget = TextAreaWidget(
            label = _("Method Instructions",
                      "Instructions"),
            description=_("Technical description and instructions intended for analysts"),
        ),
    ),
    FileField('MethodDocument',  # XXX Multiple Method documents please
        widget = FileWidget(
            label=_("Method Document"),
            description=_("Load documents describing the method here"),
        )
    ),

    # The instruments linked to this method. Don't use this
    # method, use getInstrumentUIDs() or getInstruments() instead
    LinesField('_Instruments',
        vocabulary='getInstrumentsDisplayList',
        widget=MultiSelectionWidget(
            modes = ('edit'),
            label=_("Instruments"),
            description =_(
                "The selected instruments have support for this method. "
                "Use the Instrument edit view to assign "
                "the method to a specific instrument"),
        ),
    ),

    # All the instruments available in the system. Don't use this
    # method to retrieve the instruments linked to this method, use
    # getInstruments() or getInstrumentUIDs() instead.
    LinesField('_AvailableInstruments',
        vocabulary='_getAvailableInstrumentsDisplayList',
        widget=MultiSelectionWidget(
            modes = ('edit'),
        )
    ),

    # If no instrument selected, always True. Otherwise, the user will
    # be able to set or unset the value. The behavior for this field
    # is controlled with javascript.
    BooleanField('ManualEntryOfResults',
        default=False,
        widget=BooleanWidget(
            label=_("Manual entry of results"),
            description=_("The results for the Analysis Services that use this method can be set manually"),
            modes = ('edit'),
        )
    ),

    # Only shown in readonly view. Not in edit view
    ComputedField('ManualEntryOfResultsViewField',
        expression = "context.isManualEntryOfResults()",
        widget = BooleanWidget(
            label=_("Manual entry of results"),
            description=_("The results for the Analysis Services that use this method can be set manually"),
            modes = ('view'),
        ),
    ),

    # Calculations associated to this method. The analyses services
    # with this method assigned will use the calculation selected here.
    HistoryAwareReferenceField('Calculation',
        required = 0,
        vocabulary_display_path_bound = sys.maxint,
        vocabulary = '_getCalculations',
        allowed_types = ('Calculation',),
        relationship = 'MethodCalculation',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 0,
            label=_("Calculation"),
            description =_("If required, select a calculation for the "
                           "The analysis services linked to this "
                           "method. Calculations can be configured "
                           "under the calculations item in the LIMS "
                           "set-up"),
            catalog_name='bika_setup_catalog',
            base_query={'inactive_state': 'active'},
        )
    ),
    BooleanField('Accredited',
        schemata="default",
        default=True,
        widget=BooleanWidget(
            label=_("Accredited"),
            description=_("Check if the method has been accredited"))
    ),
))

schema['description'].schemata = 'default'
schema['description'].widget.visible = True
schema['description'].widget.label = _("Description")
schema['description'].widget.description = _("Describes the method in layman terms. This information is made available to lab clients")

class Method(BaseFolder):
    implements(IMethod)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def isManualEntryOfResults(self):
        """ Indicates if manual entry of results is allowed.
            If no instrument is selected for this method, returns True.
            Otherwise, returns False by default, but its value can be
            modified using the ManualEntryOfResults Boolean Field
        """
        return len(self.getInstruments()) == 0 or self.getManualEntryOfResults()

    def _getCalculations(self):
        """ Returns a DisplayList with the available Calculations
            registered in Bika-Setup. Used to fill the Calculation
            ReferenceWidget.
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(c.UID, c.Title) \
                for c in bsc(portal_type='Calculation',
                             inactive_state = 'active')]
        items.sort(lambda x,y: cmp(x[1], y[1]))
        items.insert(0, ('', t(_('None'))))
        return DisplayList(list(items))

    def getInstruments(self):
        """ Instruments capable to perform this method
        """
        return self.getBackReferences('InstrumentMethod')

    def getInstrumentUIDs(self):
        """ UIDs of the instruments capable to perform this method
        """
        return [i.UID() for i in self.getInstruments()]

    def getInstrumentsDisplayList(self):
        """ DisplayList containing the Instruments capable to perform
            this method.
        """
        items = [(i.UID(), i.Title()) for i in self.getInstruments()]
        return DisplayList(list(items))

    def _getAvailableInstrumentsDisplayList(self):
        """ Available instruments registered in the system
            Only instruments with state=active will be fetched
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(i.UID, i.Title) \
                for i in bsc(portal_type='Instrument',
                             inactive_state = 'active')]
        items.sort(lambda x,y: cmp(x[1], y[1]))
        return DisplayList(list(items))


registerType(Method, PROJECTNAME)
