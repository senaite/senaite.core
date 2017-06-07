# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Products.ATExtensions.ateapi import RecordsField
from Products.Archetypes.Field import BooleanField, ComputedField, \
    DateTimeField, ReferenceField, StringField, TextField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import BooleanWidget, ComputedWidget, \
    FileWidget, ImageWidget, MultiSelectionWidget, ReferenceWidget, \
    StringWidget, TextAreaWidget
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.widgets import DateTimeWidget, SelectionWidget
from bika.lims.browser.widgets import RecordsWidget
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaFolderSchema, BikaSchema
from plone.app.blob.field import FileField as BlobFileField, ImageField

InstrumentType = ReferenceField(
    'InstrumentType',
    storage=Storage,
    vocabulary='getInstrumentTypes',
    allowed_types=('InstrumentType',),
    relationship='InstrumentInstrumentType',
    required=1,
    widget=SelectionWidget(
        format='select',
        label=_('Instrument type'),
        visible={'view': 'invisible', 'edit': 'visible'}
    ),
)

Manufacturer = ReferenceField(
    'Manufacturer',
    storage=Storage,
    vocabulary='getManufacturers',
    allowed_types=('Manufacturer',),
    relationship='InstrumentManufacturer',
    required=1,
    widget=SelectionWidget(
        format='select',
        label=_('Manufacturer'),
        visible={'view': 'invisible', 'edit': 'visible'}
    ),
)

Supplier = ReferenceField(
    'Supplier',
    storage=Storage,
    vocabulary='getSuppliers',
    allowed_types=('Supplier',),
    relationship='InstrumentSupplier',
    required=1,
    widget=SelectionWidget(
        format='select',
        label=_('Supplier'),
        visible={'view': 'invisible', 'edit': 'visible'}
    ),
)

Model = StringField(
    'Model',
    storage=Storage,
    widget=StringWidget(
        label=_('Model'),
        description=_("The instrument's model number")
    ),
)

SerialNo = StringField(
    'SerialNo',
    storage=Storage,
    widget=StringWidget(
        label=_('Serial No'),
        description=_(
            'The serial number that uniquely identifies the instrument')
    ),
)

Method = UIDReferenceField(
    'Method',
    storage=Storage,
    vocabulary='_getAvailableMethods',
    allowed_types=('Method',),
    required=0,
    widget=SelectionWidget(
        format='select',
        label=_('Method'),
        visible=False
    ),
)

Methods = ReferenceField(
    'Methods',
    storage=Storage,
    vocabulary='_getAvailableMethods',
    allowed_types=('Method',),
    relationship='InstrumentMethods',
    required=0,
    multiValued=1,
    widget=ReferenceWidget(
        checkbox_bound=0,
        format='select',
        label=_('Methods')
    ),
)

DisposeUntilNextCalibrationTest = BooleanField(
    'DisposeUntilNextCalibrationTest',
    storage=Storage,
    default=False,
    widget=BooleanWidget(
        label=_('De-activate until next calibration test'),
        description=_(
            'If checked, the instrument will be unavailable until the next '
            'valid calibration was performed. This checkbox will '
            'automatically be unchecked.')
    ),
)

# Procedures
InlabCalibrationProcedure = TextField(
    'InlabCalibrationProcedure',
    storage=Storage,
    schemata='Procedures',
    default_content_type='text/plain',
    allowed_content_types=('text/plain',),
    default_output_type='text/plain',
    widget=TextAreaWidget(
        label=_('In-lab calibration procedure'),
        description=_(
            'Instructions for in-lab regular calibration routines intended '
            'for analysts')
    ),
)

PreventiveMaintenanceProcedure = TextField(
    'PreventiveMaintenanceProcedure',
    storage=Storage,
    schemata='Procedures',
    default_content_type='text/plain',
    allowed_content_types=('text/plain',),
    default_output_type='text/plain',
    widget=TextAreaWidget(
        label=_('Preventive maintenance procedure'),
        description=_(
            'Instructions for regular preventive and maintenance routines '
            'intended for analysts')
    ),
)

DataInterface = StringField(
    'DataInterface',
    storage=Storage,
    vocabulary='getExportDataInterfacesList',
    widget=SelectionWidget(
        checkbox_bound=0,
        label=_('Data Interface'),
        description=_('Select an Export interface for this instrument.'),
        format='select',
        default='',
        visible=True
    ),
)

ImportDataInterface = StringField(
    'ImportDataInterface',
    storage=Storage,
    vocabulary='getImportDataInterfacesList',
    multiValued=1,
    widget=MultiSelectionWidget(
        checkbox_bound=0,
        label=_('Import Data Interface'),
        description=_('Select an Import interface for this instrument.'),
        format='select',
        default='',
        visible=True
    ),
)

ResultFilesFolder = RecordsField(
    'ResultFilesFolder',
    storage=Storage,
    subfields=('InterfaceName', 'Folder'),
    subfield_labels={'InterfaceName': _('Interface Code'),
                     'Folder': _('Folder that results will be saved')},
    subfield_readonly={'InterfaceName': True, 'Folder': False},
    widget=RecordsWidget(
        label=_('Result files folders'),
        description=_(
            'For each interface of this instrument,; you can define a folder '
            'where; the system should look for the results files while; '
            'automatically importing results. Having a folder for each '
            'Instrument and inside that folder creating; different folders '
            'for each of its Interfaces; can be a good approach. You can use '
            'Interface codes; to be sure that folder names are unique.'),
        visible=True
    ),
)

DataInterfaceOptions = RecordsField(
    'DataInterfaceOptions',
    storage=Storage,
    type='interfaceoptions',
    subfields=('Key', 'Value'),
    required_subfields=('Key', 'Value'),
    subfield_labels={'OptionValue': _('Key'),
                     'OptionText': _('Value'), },
    widget=RecordsWidget(
        label=_("Data Interface Options"),
        description=_(
            "Use this field to pass arbitrary parameters to the export/import "
            "modules."),
        visible=False
    ),
)

# References to all analyses performed with this instrument.
# Includes regular analyses, QC analyes and Calibration tests.
Analyses = UIDReferenceField(
    'Analyses',
    storage=Storage,
    required=0,
    multiValued=1,
    allowed_types=('ReferenceAnalysis', 'DuplicateAnalysis', 'Analysis'),
    widget=ReferenceWidget(
        visible=False
    ),
)

# Private method. Use getLatestReferenceAnalyses() instead.
# See getLatestReferenceAnalyses() method for further info.
_LatestReferenceAnalyses = ReferenceField(
    '_LatestReferenceAnalyses',
    storage=Storage,
    required=0,
    multiValued=1,
    allowed_types=('ReferenceAnalysis',),
    relationship='InstrumentLatestReferenceAnalyses',
    widget=ReferenceWidget(
        visible=False
    ),
)

Valid = ComputedField(
    'Valid',
    storage=Storage,
    expression="'1' if context.isValid() else '0'",
    widget=ComputedWidget(
        visible=False
    ),
)
# Needed since InstrumentType is sorted by its own object, not by its name.
InstrumentTypeName = ComputedField(
    'InstrumentTypeName',
    storage=Storage,
    expression="context.getInstrumentType().Title() "
               "if context.getInstrumentType() else ''",
    widget=ComputedWidget(
        label=_('Instrument Type'),
        visible=True
    ),
)

InstrumentLocationName = ComputedField(
    'InstrumentLocationName',
    storage=Storage,
    expression="context.getInstrumentLocation().Title() "
               "if context.getInstrumentLocation() else ''",
    widget=ComputedWidget(
        label=_('Instrument Location'),
        label_msgid='instrument_location',
        description=_(
            'The room and location where the instrument is installed'),
        description_msgid='help_instrument_location',
        visible=True
    ),
)

ManufacturerName = ComputedField(
    'ManufacturerName',
    storage=Storage,
    expression="context.getManufacturer().Title() "
               "if context.getManufacturer() else ''",
    widget=ComputedWidget(
        label=_('Manufacturer'),
        visible=True
    ),
)

SupplierName = ComputedField(
    'SupplierName',
    storage=Storage,
    expression='context.getSupplier().Title() '
               'if context.getSupplier() else ""',
    widget=ComputedWidget(
        label=_('Supplier'),
        visible=True
    ),
)

AssetNumber = StringField(
    'AssetNumber',
    storage=Storage,
    widget=StringWidget(
        label=_('Asset Number'),
        description=_("The instrument's ID in the lab's asset register")
    ),
)

InstrumentLocation = ReferenceField(
    'InstrumentLocation',
    storage=Storage,
    schemata='Additional info.',
    vocabulary='getInstrumentLocations',
    allowed_types=('InstrumentLocation',),
    relationship='InstrumentInstrumentLocation',
    required=0,
    widget=SelectionWidget(
        format='select',
        label=_('Instrument Location'),
        label_msgid='instrument_location',
        description=_(
            'The room and location where the instrument is installed'),
        description_msgid='help_instrument_location',
        visible={'view': 'invisible', 'edit': 'visible'}
    ),
)

Photo = ImageField(
    'Photo',
    storage=Storage,
    schemata='Additional info.',
    widget=ImageWidget(
        label=_('Photo image file'),
        description=_('Photo of the instrument')
    ),
)

InstallationDate = DateTimeField(
    'InstallationDate',
    storage=Storage,
    schemata='Additional info.',
    widget=DateTimeWidget(
        label=_('InstallationDate'),
        description=_('The date the instrument was installed')
    ),
)

InstallationCertificate = BlobFileField(
    'InstallationCertificate',
    storage=Storage,
    schemata='Additional info.',
    widget=FileWidget(
        label=_('Installation Certificate'),
        description=_('Installation certificate upload')
    ),
)

schema = BikaFolderSchema.copy() + BikaSchema.copy() + Schema((
    InstrumentType,
    Manufacturer,
    Supplier,
    Model,
    SerialNo,
    Method,
    Methods,
    DisposeUntilNextCalibrationTest,
    InlabCalibrationProcedure,
    PreventiveMaintenanceProcedure,
    DataInterface,
    ImportDataInterface,
    ResultFilesFolder,
    DataInterfaceOptions,
    Analyses,
    _LatestReferenceAnalyses,
    Valid,
    InstrumentTypeName,
    InstrumentLocationName,
    ManufacturerName,
    SupplierName,
    AssetNumber,
    InstrumentLocation,
    Photo,
    InstallationDate,
    InstallationCertificate
))

schema.moveField('AssetNumber', before='description')
schema.moveField('SupplierName', before='Model')
schema.moveField('ManufacturerName', before='SupplierName')
schema.moveField('InstrumentTypeName', before='ManufacturerName')

schema['description'].widget.visible = True
schema['description'].schemata = 'default'
