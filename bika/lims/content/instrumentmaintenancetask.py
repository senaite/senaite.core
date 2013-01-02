from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.public import *
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema

schema = BikaSchema.copy() + Schema((
    
    StringField('Type',
        vocabulary = "getMaintenanceTypes",
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = _("Maintenance type",
                      "Type"),
        ),
    ),
                                     
    DateTimeField('DownFrom',
        with_time = 1,
        with_date = 1,
        widget = DateTimeWidget(
            label = _("From"),
            description = _("Date from which the instrument is under maintenance"),
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
                                     
    StringField('Maintainer',
        widget = StringWidget(
            label = _("Maintainer"),
            description = _("The analyst or agent responsible of the maintenance"),
        )
    ),
                                     
    TextField('Considerations',
        default_content_type = 'text/x-web-intelligent',
        allowable_content_types = ('text/x-web-intelligent',),
        default_output_type="text/html",
        widget = TextAreaWidget(
            label = _("Considerations"),
            description = _("Remarks to take into account for maintenance process"),
        ),
    ),
                                     
    TextField('WorkPerformed',
        default_content_type = 'text/x-web-intelligent',
        allowable_content_types = ('text/x-web-intelligent',),
        default_output_type="text/html",
        widget = TextAreaWidget(
            label = _("Work Performed"),
            description = _("Description of the actions made during the maintenance process"),
        ),
    ),
                                     
    TextField('Remarks',
        default_content_type = 'text/x-web-intelligent',
        allowable_content_types = ('text/x-web-intelligent',),
        default_output_type="text/html",
        widget = TextAreaWidget(
            label = _("Remarks"),
        ),
    ),
    
    FixedPointField('Cost',
        default = '0.00',
        widget = DecimalWidget(
            label = _("Price"),
        ),
    ),   
                                       
))

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
        types = [('preventive',_('Preventive')),
                 ('repair', _('Repair')),
                 ('enhancement', _('Enhancement'))]
        return DisplayList(types)
    
atapi.registerType(InstrumentMaintenanceTask, PROJECTNAME)