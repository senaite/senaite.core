from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.public import *
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema

schema = BikaSchema.copy() + Schema((

    ReferenceField('Instrument',
        allowed_types=('Instrument',),
        relationship='InstrumentCertificationInstrument',
        widget=StringWidget(
            visible=False,
        )
    ),

    ComputedField('InstrumentUID',
        expression = 'context.getInstrument() and context.getInstrument().UID() or None',
        widget=ComputedWidget(
            visible=False,
        ),
    ),

    StringField('Agency',
        widget = StringWidget(
            label = _("Agency"),
            description = _("Organization responsible of granting the certification")
        ),
    ),

    DateTimeField('Date',
        widget = DateTimeWidget(
            label = _("Date"),
            description = _("Date when the certification was granted"),
        ),
    ),

    DateTimeField('ValidFrom',
        with_time = 1,
        with_date = 1,
        widget = DateTimeWidget(
            label = _("From"),
            description = _("Date from which the certification is valid"),
        ),
    ),

    DateTimeField('ValidTo',
        with_time = 1,
        with_date = 1,
        widget = DateTimeWidget(
            label = _("To"),
            description = _("Date until the certification is valid"),
        ),
    ),

    TextField('Remarks',
        default_content_type = 'text/plain',
        allowed_content_types= ('text/plain', ),
        default_output_type="text/plain",
        widget = TextAreaWidget(
            label = _("Remarks"),
        ),
    ),

))

class InstrumentCertification(BaseFolder):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

atapi.registerType(InstrumentCertification, PROJECTNAME)
