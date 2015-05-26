from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser.widgets import DateTimeWidget, ReferenceWidget
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

    DateTimeField('DateIssued',
        with_time = 1,
        with_date = 1,
        widget = DateTimeWidget(
            label=_("Report Date"),
            description=_("Calibration report date"),
        ),
    ),

    DateTimeField('DownFrom',
        with_time = 1,
        with_date = 1,
        widget = DateTimeWidget(
            label=_("From"),
            description=_("Date from which the instrument is under calibration"),
        ),
    ),

    DateTimeField('DownTo',
        with_time = 1,
        with_date = 1,
        widget = DateTimeWidget(
            label=_("To"),
            description=_("Date until the instrument will not be available"),
        ),
    ),

    StringField('Calibrator',
        widget = StringWidget(
            label=_("Calibrator"),
            description=_("The analyst or agent responsible of the calibration"),
        )
    ),

    TextField('Considerations',
        default_content_type = 'text/plain',
        allowed_content_types= ('text/plain', ),
        default_output_type="text/plain",
        widget = TextAreaWidget(
            label=_("Considerations"),
            description=_("Remarks to take into account before calibration"),
        ),
    ),

    TextField('WorkPerformed',
        default_content_type = 'text/plain',
        allowed_content_types= ('text/plain', ),
        default_output_type="text/plain",
        widget = TextAreaWidget(
            label=_("Work Performed"),
            description=_("Description of the actions made during the calibration"),
        ),
    ),

    ReferenceField('Worker',
        vocabulary='getLabContacts',
        allowed_types=('LabContact',),
        relationship='LabContactInstrumentCalibration',
        widget=ReferenceWidget(
            checkbox_bound=0,
            label=_("Performed by"),
            description=_("The person at the supplier who performed the task"),
            size=30,
            base_query={'inactive_state': 'active'},
            showOn=True,
            colModel=[{'columnName': 'UID', 'hidden': True},
                      {'columnName': 'JobTitle', 'width': '20', 'label': _('Job Title')},
                      {'columnName': 'Title', 'width': '80', 'label': _('Name')}
                     ],
        ),
    ),

    StringField('ReportID',
        widget = StringWidget(
            label=_("Report ID"),
            description=_("Report identification number"),
        )
    ),

    TextField('Remarks',
        default_content_type = 'text/plain',
        allowed_content_types= ('text/plain', ),
        default_output_type="text/plain",
        widget = TextAreaWidget(
            label=_("Remarks"),
        ),
    ),

))

schema['title'].widget.label = 'Asset Number'


class InstrumentCalibration(BaseFolder):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getLabContacts(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        # fallback - all Lab Contacts
        pairs = []
        for contact in bsc(portal_type='LabContact',
                           inactive_state='active',
                           sort_on='sortable_title'):
            pairs.append((contact.UID, contact.Title))
        return DisplayList(pairs)

atapi.registerType(InstrumentCalibration, PROJECTNAME)
