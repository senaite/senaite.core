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
        relationship='InstrumentCalibrationInstrument',
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

    DateTimeField('DownFrom',
        with_time = 1,
        with_date = 1,
        widget = DateTimeWidget(
            label = _("From"),
            description = _("Date from which the instrument is under calibration"),
        ),
    ),

    DateTimeField('DownTo',
        with_time = 1,
        with_date = 1,
        widget = DateTimeWidget(
            label = _("To"),
            description = _("Date until the instrument will not be available"),
        ),
    ),

    StringField('Calibrator',
        widget = StringWidget(
            label = _("Calibrator"),
            description = _("The analyst or agent responsible of the calibration"),
        )
    ),

    TextField('Considerations',
        default_content_type = 'text/plain',
        allowed_content_types= ('text/plain', ),
        default_output_type="text/plain",
        widget = TextAreaWidget(
            label = _("Considerations"),
            description = _("Remarks to take into account before calibration"),
        ),
    ),

    TextField('WorkPerformed',
        default_content_type = 'text/plain',
        allowed_content_types= ('text/plain', ),
        default_output_type="text/plain",
        widget = TextAreaWidget(
            label = _("Work Performed"),
            description = _("Description of the actions made during the calibration"),
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

class InstrumentCalibration(BaseFolder):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

atapi.registerType(InstrumentCalibration, PROJECTNAME)
