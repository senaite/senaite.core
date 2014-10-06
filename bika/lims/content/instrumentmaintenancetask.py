from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema

schema = BikaSchema.copy() + Schema((

    ReferenceField('Instrument',
        allowed_types=('Instrument',),
        relationship='InstrumentMaintenanceTaskInstrument',
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

    StringField('Type',
        vocabulary = "getMaintenanceTypes",
        widget = ReferenceWidget(
            checkbox_bound = 0,
            label = _("Maintenance type",
                      "Type"),
        ),
    ),

    DateTimeField('DownFrom',
        with_time = 1,
        with_date = 1,
        required = 1,
        widget = DateTimeWidget(
            label=_("From"),
            description=_("Date from which the instrument is under maintenance"),
            show_hm = True,
        ),
    ),

    DateTimeField('DownTo',
        with_time = 1,
        with_date = 1,
        widget = DateTimeWidget(
            label=_("To"),
            description=_("Date until the instrument will not be available"),
            show_hm = True,
        ),
    ),

    StringField('Maintainer',
        widget = StringWidget(
            label=_("Maintainer"),
            description=_("The analyst or agent responsible of the maintenance"),
        )
    ),

    TextField('Considerations',
        default_content_type = 'text/plain',
        allowed_content_types= ('text/plain', ),
        default_output_type="text/plain",
        widget = TextAreaWidget(
            label=_("Considerations"),
            description=_("Remarks to take into account for maintenance process"),
        ),
    ),

    TextField('WorkPerformed',
        default_content_type = 'text/plain',
        allowed_content_types= ('text/plain', ),
        default_output_type="text/plain",
        widget = TextAreaWidget(
            label=_("Work Performed"),
            description=_("Description of the actions made during the maintenance process"),
        ),
    ),

    TextField('Remarks',
        default_content_type = 'text/plain',
        allowed_content_types= ('text/plain', ),
        default_output_type="text/plain",
        widget = TextAreaWidget(
            label=_("Remarks"),
        ),
    ),

    FixedPointField('Cost',
        default = '0.00',
        widget = DecimalWidget(
            label=_("Price"),
        ),
    ),

    BooleanField('Closed',
        default = '0',
        widget = BooleanWidget(
            label=_("Closed"),
            description=_("Set the maintenance task as closed.")
        ),
    ),
))

IdField = schema['id']
schema['description'].required = False
schema['description'].widget.visible = True
schema['description'].schemata = 'default'

# Title is not needed to be unique
schema['title'].validators = ()
schema['title']._validationLayer()

class InstrumentMaintenanceTaskStatuses:
    CLOSED = 'Closed'
    CANCELLED = 'Cancelled'
    OVERDUE = "Overdue"
    PENDING = "Pending"
    INQUEUE = "In queue"

class InstrumentMaintenanceTask(BaseFolder):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getMaintenanceTypes(self):
        """ Return the current list of maintenance types
        """
        types = [('Preventive',safe_unicode(_('Preventive')).encode('utf-8')),
                 ('Repair', safe_unicode(_('Repair')).encode('utf-8')),
                 ('Enhancement', safe_unicode(_('Enhancement')).encode('utf-8'))]
        return DisplayList(types)

    def getCurrentStateI18n(self):
        return safe_unicode(_(self.getCurrentState()).encode('utf-8'))

    def getCurrentState(self):
        workflow = getToolByName(self, 'portal_workflow')
        if self.getClosed():
            return InstrumentMaintenanceTaskStatuses.CLOSED
        elif workflow.getInfoFor(self, 'cancellation_state', '') == 'cancelled':
            return InstrumentMaintenanceTaskStatuses.CANCELLED
        else:
            now = DateTime()
            dfrom = self.getDownFrom()
            dto = self.getDownTo() and self.getDownTo() or DateTime(9999, 12, 31)
            if (now > dto):
                return InstrumentMaintenanceTaskStatuses.OVERDUE
            if (now >= dfrom):
                return InstrumentMaintenanceTaskStatuses.PENDING
            else:
                return InstrumentMaintenanceTaskStatuses.INQUEUE

atapi.registerType(InstrumentMaintenanceTask, PROJECTNAME)
