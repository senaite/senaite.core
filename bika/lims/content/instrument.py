from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.CMFCore.permissions import View, ModifyPortalContent
from bika.lims import bikaMessageFactory as _
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema, BikaFolderSchema
from bika.lims.interfaces import IInstrument
from bika.lims.browser.widgets import DateTimeWidget
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from plone.app.folder.folder import ATFolder
from Products.ATContentTypes.content import schemata
from Products.Archetypes.references import HoldingReference

schema = BikaFolderSchema.copy() + BikaSchema.copy() + Schema((
                                     
    ReferenceField('InstrumentType',
        vocabulary='getInstrumentTypes',
        allowed_types=('InstrumentType',),
        relationship='InstrumentInstrumentType',        
        required=1,
        widget=SelectionWidget(
            format='select',
            label=_('Instrument type'),
        ),
    ),
                                     
    ReferenceField('Manufacturer',
        vocabulary='getManufacturers',
        allowed_types=('Manufacturer',),
        relationship='InstrumentManufacturer',
        required=1,
        widget=SelectionWidget(
            format='select',
            label=_('Manufacturer'),
        ),
    ),        
                                     
    ReferenceField('Supplier',
        vocabulary='getSuppliers',
        allowed_types=('Supplier',),
        relationship='InstrumentSupplier',
        required=1,
        widget=SelectionWidget(
            format='select',
            label=_('Supplier'),
        ),
    ),

    StringField('Model',
        widget = StringWidget(
            label = _("Model"),
            description = _("The instrument's model number"),
        )
    ),
                                                                      
    StringField('SerialNo',
        widget = StringWidget(
            label = _("Serial No"),
            description = _("The serial number that uniquely identifies the instrument"),
        )
    ),  

    # Procedures
    TextField('InlabCalibrationProcedure',
        schemata = 'Procedures',
        default_content_type = 'text/x-web-intelligent',
        allowable_content_types = ('text/x-web-intelligent',),
        default_output_type="text/html",
        widget = TextAreaWidget(
            label = _("In-lab calibration procedure"),
            description = _("Instructions for in-lab regular calibration routines intended for analysts"),
        ),
    ),
    TextField('PreventiveMaintenanceProcedure',
        schemata = 'Procedures',
        default_content_type = 'text/x-web-intelligent',
        allowable_content_types = ('text/x-web-intelligent',),
        default_output_type="text/html",
        widget = TextAreaWidget(
            label = _("Preventive maintenance procedure"),
            description = _("Instructions for regular preventive and maintenance routines intended for analysts"),
        ),
    ),     
                                                                              
#    ComputedField('InstrumentTypeUID',
#        expression='here.getInstrumentType() and here.getInstrumentType().UID() or None',
#        widget=ComputedWidget(
#        ),
#    ),
                                                                      
                                                              
#    ComputedField('Brand',
#        expession='here.getManufacturer() and here.getManufacturer().Title() or ""',
#        widget=ComputedWidget(
#        ),
#    ),
#
#    ComputedField('ManufacturerUID',
#        expression='here.getManufacturer() and here.getManufacturer().UID() or None',
#        widget=ComputedWidget(
#        ),
#    ),   


                                                                      
#    ComputedField('SupplierUID',
#        expression='here.getSupplier() and here.getSupplier().UID() or None',
#        widget=ComputedWidget(
#        ),
#    ),
                                                                                                                                          
 

#    StringField('DataInterface',
#        vocabulary = "getDataInterfacesList",
#        widget = ReferenceWidget(
#            checkbox_bound = 1,
#            label = _("Data Interface"),
#            description = _("Select an Import/Export interface for this instrument."),
#        ),
#    ),
#    RecordsField('DataInterfaceOptions',
#        type = 'interfaceoptions',
#        subfields = ('Key','Value'),
#        required_subfields = ('Key','Value'),
#        subfield_labels = {'OptionValue': _('Key'),
#                           'OptionText': _('Value'),},
#        widget = RecordsWidget(
#            label = _("Data Interface Options"),
#            description = _("Use this field to pass arbitrary parameters to the export/import "
#                            "modules."),
#        ),
#    ),
                                                                      
    # Old stuff, for setup import compatibility
#    StringField('Brand',
#        widget = StringWidget(
#            label = _("Brand"),
#            description = _("The commercial 'make' of the instrument"),
#        )
#    ),
#    StringField('Type',
#        widget = StringWidget(
#            label = _("Instrument type"),
#        )
#    ),
#    StringField('CalibrationCertificate',
#        widget = StringWidget(
#            label = _("Calibration Certificate"),
#            description = _("The instrument's calibration certificate and number"),
#        )
#    ),
#    DateTimeField('CalibrationExpiryDate',
#        with_time = 0,
#        with_date = 1,
#        widget = DateTimeWidget(
#            label = _("Calibration Expiry Date"),
#            description = _("Due Date for next calibration"),
#        ),
#    ),








#                                     
#    # Schedule tab
#    StringField('ScheduleTaskType',
#        schemata = 'Schedule',
#        vocabulary='getScheduleTaskTypesList',
#        widget = ReferenceWidget(
#            checkbox_bound = 1,
#            label = _('Task type'),
#            description = _("Select the type of the maintenance task"),
#        ),
#    ),    
#    StringField('ScheduleTaskTitle',
#        schemata = 'Schedule',
#        widget = StringWidget(
#            label = _("Title"),
#            description = _("The title of the scheduled task"),
#        )
#    ),
#    TextField('ScheduleTaskDescription',
#        schemata = 'Schedule',
#        default_content_type = 'text/x-web-intelligent',
#        allowable_content_types = ('text/x-web-intelligent',),
#        default_output_type="text/html",
#        widget = TextAreaWidget(
#            label = _("Description"),
#        ),
#    ),
#    DateTimeField('ScheduleTaskFrom',
#        schemata = 'Schedule',
#        with_time = 0,
#        with_date = 1,
#        widget = DateTimeWidget(
#            label = _("From"),
#            description = _("Date when the task starts"),
#        ),
#    ), 
#    DateTimeField('ScheduleTaskTo',
#        schemata = 'Schedule',
#        with_time = 0,
#        with_date = 1,
#        widget = DateTimeWidget(
#            label = _("To"),
#            description = _("Date when the task ends"),
#        ),
#    ),
#
#    # Maintenance tab
#    StringField('MaintenanceHistoryType',
#        schemata = 'MaintenanceHistory',
#        vocabulary='getMaintenanceTypesList',
#        widget = ReferenceWidget(
#            checkbox_bound = 1,
#            label = _('Maintenance type'),
#            description = _("Select the type of the maintenance task"),
#        ),
#    ),
#    TextField('MaintenanceHistoryDescription',
#        schemata = 'MaintenanceHistory',
#        default_content_type = 'text/x-web-intelligent',
#        allowable_content_types = ('text/x-web-intelligent',),
#        default_output_type="text/html",
#        widget = TextAreaWidget(
#            label = _("Description"),
#        ),
#    ),     
#    DateTimeField('MaintenanceHistoryDownFrom',
#        schemata = 'MaintenanceHistory',
#        with_time = 0,
#        with_date = 1,
#        widget = DateTimeWidget(
#            label = _("Down from date"),
#            description = _("Date from which the instrument will not be available"),
#        ),
#    ),
#    DateTimeField('MaintenanceHistoryDownTo',
#        schemata = 'MaintenanceHistory',
#        with_time = 0,
#        with_date = 1,
#        widget = DateTimeWidget(
#            label = _("Down to date"),
#            description = _("Date until the instrument will not be available"),
#        ),
#    ),
#    TextField('MaintenanceHistoryConsiderations',
#        schemata = 'MaintenanceHistory',
#        default_content_type = 'text/x-web-intelligent',
#        allowable_content_types = ('text/x-web-intelligent',),
#        default_output_type="text/html",
#        widget = TextAreaWidget(
#            label = _("Considerations"),
#        ),
#    ),
#    TextField('MaintenanceHistoryRemarks',
#        schemata = 'MaintenanceHistory',
#        default_content_type = 'text/x-web-intelligent',
#        allowable_content_types = ('text/x-web-intelligent',),
#        default_output_type="text/html",
#        widget = TextAreaWidget(
#            label = _("Remarks"),
#        ),
#    ),
#    TextField('MaintenanceHistoryWorkPerformed',
#        schemata = 'MaintenanceHistory',
#        default_content_type = 'text/x-web-intelligent',
#        allowable_content_types = ('text/x-web-intelligent',),
#        default_output_type="text/html",
#        widget = TextAreaWidget(
#            label = _("Work performed"),
#        ),
#    ),
#    DateTimeField('MaintenanceHistoryCompletionDate',
#        schemata = 'MaintenanceHistory',
#        with_time = 0,
#        with_date = 1,
#        widget = DateTimeWidget(
#            label = _("Completion date"),
#            description = _("Date when the instrument maintenance finished"),
#        ),
#    ),
#    FixedPointField('MaintenanceHistoryPrice',
#        schemata = "MaintenanceHistory",
#        default = '0.00',
#        widget = DecimalWidget(
#            label = _("Price (excluding VAT)"),
#        ),
#    ),
#
#    # Calibrations tab
#    StringField('CalibrationAgent',
#        schemata = 'Calibrations',
#        vocabulary='getCalibrationAgentsList',
#        widget = ReferenceWidget(
#            checkbox_bound = 1,
#            label = _('Calibration agent'),
#        ),
#    ),    
#    DateTimeField('CalibrationFrom',
#        schemata = 'Calibrations',
#        with_time = 0,
#        with_date = 1,
#        widget = DateTimeWidget(
#            label = _("From"),
#            description = _("Date from which the instrument will not be available"),
#        ),
#    ),
#    DateTimeField('CalibrationTo',
#        schemata = 'Calibrations',
#        with_time = 0,
#        with_date = 1,
#        widget = DateTimeWidget(
#            label = _("To"),
#            description = _("Date until the instrument will not be available"),
#        ),
#    ),
#    TextField('CalibrationConsiderations',
#        schemata = 'Calibrations',
#        default_content_type = 'text/x-web-intelligent',
#        allowable_content_types = ('text/x-web-intelligent',),
#        default_output_type="text/html",
#        widget = TextAreaWidget(
#            label = _("Considerations"),
#        ),
#    ),
#    TextField('CalibrationRemarks',
#        schemata = 'Calibrations',
#        default_content_type = 'text/x-web-intelligent',
#        allowable_content_types = ('text/x-web-intelligent',),
#        default_output_type="text/html",
#        widget = TextAreaWidget(
#            label = _("Remarks"),
#        ),
#    ),
#    TextField('CalibrationWorkPerformed',
#        schemata = 'Calibrations',
#        default_content_type = 'text/x-web-intelligent',
#        allowable_content_types = ('text/x-web-intelligent',),
#        default_output_type="text/html",
#        widget = TextAreaWidget(
#            label = _("Work performed"),
#        ),
#    ),
#    DateTimeField('CalibrationsCompletionDate',
#        schemata = 'Calibrations',
#        with_time = 0,
#        with_date = 1,
#        widget = DateTimeWidget(
#            label = _("Completion date"),
#            description = _("Date when the instrument calibration finished"),
#        ),
#    ),
#
#    # Certification tab
#    StringField('CertificationNumber',
#        schemata = 'Certification',
#        widget = StringWidget(
#            label = _("Certification number"),
#            description = _("The number/code of the certification provided by a certification agency"),
#        )
#    ),
#    StringField('CertificationAgency',
#        schemata = 'Certification',
#        widget = StringWidget(
#            label = _("Certification agency"),
#            description = _("Organization responsible of the instrument validation in order to grant a certification for it"),
#        )
#    ),
#    DateTimeField('CertificationApplicationDate',
#        schemata = 'Certification',
#        with_time = 0,
#        with_date = 1,
#        widget = DateTimeWidget(
#            label = _("Application date"),
#            description = _("Date in which the lab made the request for obtaining the certificate"),
#        ),
#    ),
#    DateTimeField('CertificationDate',
#        schemata = 'Certification',
#        with_time = 0,
#        with_date = 1,
#        widget = DateTimeWidget(
#            label = _("Certification date"),
#            description = _("Date when the certification was granted by the certification agency"),
#        ),
#    ),
#    DateTimeField('CertificationValidFrom',
#        schemata = 'Certification',
#        with_time = 0,
#        with_date = 1,
#        widget = DateTimeWidget(
#            label = _("Valid from"),
#            description = _("Date from which the instrument certification is valid"),
#        ),
#    ),
#    DateTimeField('CertificationValidTo',
#        schemata = 'Certification',
#        with_time = 0,
#        with_date = 1,
#        widget = DateTimeWidget(
#            label = _("Valid to"),
#            description = _("Date until the instrument certification is valid"),
#        ),
#    ),
#    TextField('CertificationRemarks',
#        schemata = 'Certification',
#        default_content_type = 'text/x-web-intelligent',
#        allowable_content_types = ('text/x-web-intelligent',),
#        default_output_type="text/html",
#        widget = TextAreaWidget(
#            label = _("Remarks"),
#        ),
#    ),
))
schema['description'].widget.visible = True
schema['description'].schemata = 'default'

def getDataInterfaces(context):
    """ Return the current list of data interfaces
    """
    from bika.lims.exportimport import instruments
    exims = [('',context.translate(_('None')))]
    for exim_id in instruments.__all__:
        exim = getattr(instruments, exim_id)
        exims.append((exim_id, exim.title))
    return DisplayList(exims)

def getMaintenanceTypes(context):
    types = [('preventive', 'Preventive'),
             ('repair', 'Repair'),
             ('enhance', 'Enhancement')]
    return DisplayList(types);

def getCalibrationAgents(context):
    agents = [('analyst', 'Analyst'),
             ('maintainer', 'Maintainer')]
    return DisplayList(agents);

class Instrument(ATFolder):
    implements(IInstrument)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        return self.title

    def getDataInterfacesList(self):
        return getDataInterfaces(self)
    
    def getScheduleTaskTypesList(self):
        return getMaintenanceTypes(self)
    
    def getMaintenanceTypesList(self):
        return getMaintenanceTypes(self)
    
    def getCalibrationAgentsList(self):
        return getCalibrationAgents(self)
    
    def getManufacturers(self):        
        manufacturers = []
        bsc = getToolByName(self, "bika_setup_catalog")
        for manufacturer in bsc(portal_type = 'Manufacturer',
                                inactive_state = 'active'):
            manufacturers.append([manufacturer.UID, manufacturer.Title])
        manufacturers.sort(lambda x,y:cmp(x[1], y[1]))
        return DisplayList(manufacturers)

    def getSuppliers(self):        
        suppliers = []
        bsc = getToolByName(self, "bika_setup_catalog")
        for supplier in bsc(portal_type = 'Supplier',
                                inactive_state = 'active'):
            suppliers.append([supplier.UID, supplier.getName])
        suppliers.sort(lambda x,y:cmp(x[1], y[1]))        
        return DisplayList(suppliers)
    
    def getInstrumentTypes(self):        
        its = []
        bsc = getToolByName(self, "bika_setup_catalog")
        for it in bsc(portal_type = 'InstrumentType',
                                inactive_state = 'active'):
            its.append([it.UID, it.Title])
        its.sort(lambda x,y:cmp(x[1], y[1]))
        return DisplayList(its)
    
    def getMaintenanceTasks(self):
        return self.objectValues('InstrumentMaintenanceTask')
    
    def getCalibrations(self):
        return self.objectValues('InstrumentCalibration')
    
    def getCertifications(self):
        return self.objectValues('InstrumentCertification')

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)

registerType(Instrument, PROJECTNAME)
