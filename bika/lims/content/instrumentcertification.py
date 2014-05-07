from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.public import *
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from Products.CMFCore import permissions

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

    # Set the Certificate as Internal
    # When selected, the 'Agency' field is hidden
    BooleanField('Internal',
        default=False,
        widget=BooleanWidget(
            label=_("Internal Certificate"),
            description=_("Select if is an in-house calibration certificate")
        )
    ),

    StringField('Agency',
        widget = StringWidget(
            label = _("Agency"),
            description = _("Organization responsible of granting the calibration certificate")
        ),
    ),

    DateTimeField('Date',
        widget = DateTimeWidget(
            label = _("Date"),
            description = _("Date when the calibration certificate was granted"),
        ),
    ),

    DateTimeField('ValidFrom',
        with_time = 1,
        with_date = 1,
        required = 1,
        widget = DateTimeWidget(
            label = _("From"),
            description = _("Date from which the calibration certificate is valid"),
        ),
    ),

    DateTimeField('ValidTo',
        with_time = 1,
        with_date = 1,
        required = 1,
        widget = DateTimeWidget(
            label = _("To"),
            description = _("Date until the certificate is valid"),
        ),
    ),

    FileField('Document',
        widget = FileWidget(
            label = _("Certificate Document"),
            description = _("Load the certificate document here"),
        )
    ),

    TextField('Remarks',
        searchable=True,
        default_content_type='text/x-web-intelligent',
        allowable_content_types = ('text/plain', ),
        default_output_type="text/plain",
        mode="rw",
        widget=TextAreaWidget(
            macro="bika_widgets/remarks",
            label=_('Remarks'),
            append_only=True,
        ),
    ),

))

schema['title'].widget.label=_("Certificate Code")

class InstrumentCertification(BaseFolder):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

atapi.registerType(InstrumentCertification, PROJECTNAME)
