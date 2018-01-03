# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from datetime import date

from AccessControl import ClassSecurityInfo

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Archetypes.atapi import DisplayList, PicklistWidget
from Products.Archetypes.atapi import registerType

from zope.interface import implements
from plone.app.folder.folder import ATFolder

# Schema and Fields
from Products.Archetypes.atapi import Schema
from Products.ATContentTypes.content import schemata
from Products.Archetypes.atapi import ReferenceField
from Products.Archetypes.atapi import ComputedField
from Products.Archetypes.atapi import DateTimeField
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import TextField
from Products.Archetypes.atapi import ImageField
from Products.Archetypes.atapi import BooleanField
from Products.ATExtensions.ateapi import RecordsField
from plone.app.blob.field import FileField as BlobFileField
from bika.lims.browser.fields import UIDReferenceField

# Widgets
from Products.Archetypes.atapi import ComputedWidget
from Products.Archetypes.atapi import StringWidget
from Products.Archetypes.atapi import TextAreaWidget
from Products.Archetypes.atapi import FileWidget
from Products.Archetypes.atapi import ImageWidget
from Products.Archetypes.atapi import BooleanWidget
from Products.Archetypes.atapi import SelectionWidget
from Products.Archetypes.atapi import ReferenceWidget
from Products.Archetypes.atapi import MultiSelectionWidget
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.browser.widgets import RecordsWidget

# bika.lims imports
from bika.lims import api
from bika.lims import logger
from bika.lims.utils import t
from bika.lims.utils import to_utf8
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IInstrument
from bika.lims.config import QCANALYSIS_TYPES
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims import bikaMessageFactory as _

schema = BikaFolderSchema.copy() + BikaSchema.copy() + Schema((

    ReferenceField(
        'InstrumentType',
        vocabulary='getInstrumentTypes',
        allowed_types=('InstrumentType',),
        relationship='InstrumentInstrumentType',
        required=1,
        widget=SelectionWidget(
            format='select',
            label=_("Instrument type"),
            visible={'view': 'invisible', 'edit': 'visible'}
        ),
    ),

    ReferenceField(
        'Manufacturer',
        vocabulary='getManufacturers',
        allowed_types=('Manufacturer',),
        relationship='InstrumentManufacturer',
        required=1,
        widget=SelectionWidget(
            format='select',
            label=_("Manufacturer"),
            visible={'view': 'invisible', 'edit': 'visible'}
        ),
    ),

    ReferenceField(
        'Supplier',
        vocabulary='getSuppliers',
        allowed_types=('Supplier',),
        relationship='InstrumentSupplier',
        required=1,
        widget=SelectionWidget(
            format='select',
            label=_("Supplier"),
            visible={'view': 'invisible', 'edit': 'visible'}
        ),
    ),

    StringField(
        'Model',
        widget=StringWidget(
            label=_("Model"),
            description=_("The instrument's model number"),
        )
    ),

    StringField(
        'SerialNo',
        widget=StringWidget(
            label=_("Serial No"),
            description=_("The serial number that uniquely identifies the instrument"),
        )
    ),

    UIDReferenceField(
        'Method',
        vocabulary='_getAvailableMethods',
        allowed_types=('Method',),
        required=0,
        widget=SelectionWidget(
            format='select',
            label=_("Method"),
            visible=False,
        ),
    ),

    ReferenceField(
        'Methods',
        vocabulary='_getAvailableMethods',
        allowed_types=('Method',),
        relationship='InstrumentMethods',
        required=0,
        multiValued=1,
        widget=PicklistWidget(
            size=10,
            label=_("Methods"),
        ),
    ),

    BooleanField(
        'DisposeUntilNextCalibrationTest',
        default=False,
        widget=BooleanWidget(
            label=_("De-activate until next calibration test"),
            description=_("If checked, the instrument will be unavailable until the next valid "
                          "calibration was performed. This checkbox will automatically be unchecked."),
        ),
    ),

    # Procedures
    TextField(
        'InlabCalibrationProcedure',
        schemata='Procedures',
        default_content_type='text/plain',
        allowed_content_types=('text/plain', ),
        default_output_type="text/plain",
        widget=TextAreaWidget(
            label=_("In-lab calibration procedure"),
            description=_("Instructions for in-lab regular calibration routines intended for analysts"),
        ),
    ),

    TextField(
        'PreventiveMaintenanceProcedure',
        schemata='Procedures',
        default_content_type='text/plain',
        allowed_content_types=('text/plain', ),
        default_output_type="text/plain",
        widget=TextAreaWidget(
            label=_("Preventive maintenance procedure"),
            description=_("Instructions for regular preventive and maintenance routines intended for analysts"),
        ),
    ),

    StringField(
        'DataInterface',
        vocabulary="getExportDataInterfacesList",
        widget=SelectionWidget(
            checkbox_bound=0,
            label=_("Data Interface"),
            description=_("Select an Export interface for this instrument."),
            format='select',
            default='',
            visible=True,
        ),
    ),

    StringField('ImportDataInterface',
                vocabulary="getImportDataInterfacesList",
                multiValued=1,
                widget=MultiSelectionWidget(
                    checkbox_bound=0,
                    label=_("Import Data Interface"),
                    description=_(
                        "Select an Import interface for this instrument."),
                    format='select',
                    default='',
                    visible=True,
                ),
                ),

    RecordsField(
        'ResultFilesFolder',
        subfields=('InterfaceName', 'Folder'),
        subfield_labels={'InterfaceName': _('Interface Code'),
                         'Folder': _('Folder that results will be saved')},
        subfield_readonly={'InterfaceName': True,
                           'Folder': False},
        widget=RecordsWidget(
            label=_("Result files folders"),
            description=_("For each interface of this instrument, \
                      you can define a folder where \
                      the system should look for the results files while \
                      automatically importing results. Having a folder \
                      for each Instrument and inside that folder creating \
                      different folders for each of its Interfaces \
                      can be a good approach. You can use Interface codes \
                      to be sure that folder names are unique."),
            visible=True,
        ),
    ),

    RecordsField(
        'DataInterfaceOptions',
        type='interfaceoptions',
        subfields=('Key', 'Value'),
        required_subfields=('Key', 'Value'),
        subfield_labels={
            'OptionValue': _('Key'),
            'OptionText': _('Value'),
        },
        widget=RecordsWidget(
            label=_("Data Interface Options"),
            description=_("Use this field to pass arbitrary parameters to the export/import modules."),
            visible=False,
        ),
    ),

    # References to all analyses performed with this instrument.
    # Includes regular analyses, QC analyes and Calibration tests.
    UIDReferenceField(
        'Analyses',
        required=0,
        multiValued=1,
        allowed_types=('ReferenceAnalysis', 'DuplicateAnalysis',
                       'Analysis'),
        widget=ReferenceWidget(
            visible=False,
        ),
    ),

    # Private method. Use getLatestReferenceAnalyses() instead.
    # See getLatestReferenceAnalyses() method for further info.
    ReferenceField(
        '_LatestReferenceAnalyses',
        required=0,
        multiValued=1,
        allowed_types=('ReferenceAnalysis'),
        relationship='InstrumentLatestReferenceAnalyses',
        widget=ReferenceWidget(
            visible=False,
        ),
    ),

    ComputedField(
        'Valid',
        expression="'1' if context.isValid() else '0'",
        widget=ComputedWidget(
            visible=False,
        ),
    ),

    # Needed since InstrumentType is sorted by its own object, not by its name.
    ComputedField(
        'InstrumentTypeName',
        expression='here.getInstrumentType().Title() if here.getInstrumentType() else ""',
        widget=ComputedWidget(
            label=_('Instrument Type'),
            visible=True,
        ),
    ),

    ComputedField(
        'InstrumentLocationName',
        expression='here.getInstrumentLocation().Title() if here.getInstrumentLocation() else ""',
        widget=ComputedWidget(
            label=_("Instrument Location"),
            label_msgid="instrument_location",
            description=_("The room and location where the instrument is installed"),
            description_msgid="help_instrument_location",
            visible=True,
        ),
    ),

    ComputedField(
        'ManufacturerName',
        expression='here.getManufacturer().Title() if here.getManufacturer() else ""',
        widget=ComputedWidget(
            label=_('Manufacturer'),
            visible=True,
        ),
    ),

    ComputedField(
        'SupplierName',
        expression='here.getSupplier().Title() if here.getSupplier() else ""',
        widget=ComputedWidget(
            label=_('Supplier'),
            visible=True,
        ),
    ),

    StringField(
        'AssetNumber',
        widget=StringWidget(
            label=_("Asset Number"),
            description=_("The instrument's ID in the lab's asset register"),
        )
    ),

    ReferenceField(
        'InstrumentLocation',
        schemata='Additional info.',
        vocabulary='getInstrumentLocations',
        allowed_types=('InstrumentLocation', ),
        relationship='InstrumentInstrumentLocation',
        required=0,
        widget=SelectionWidget(
            format='select',
            label=_("Instrument Location"),
            label_msgid="instrument_location",
            description=_("The room and location where the instrument is installed"),
            description_msgid="help_instrument_location",
            visible={'view': 'invisible', 'edit': 'visible'}
        )
    ),

    ImageField(
        'Photo',
        schemata='Additional info.',
        widget=ImageWidget(
            label=_("Photo image file"),
            description=_("Photo of the instrument"),
        ),
    ),

    DateTimeField(
        'InstallationDate',
        schemata='Additional info.',
        widget=DateTimeWidget(
            label=_("InstallationDate"),
            description=_("The date the instrument was installed"),
        )
    ),

    BlobFileField(
        'InstallationCertificate',
        schemata='Additional info.',
        widget=FileWidget(
            label=_("Installation Certificate"),
            description=_("Installation certificate upload"),
        )
    ),

))

schema.moveField('AssetNumber', before='description')
schema.moveField('SupplierName', before='Model')
schema.moveField('ManufacturerName', before='SupplierName')
schema.moveField('InstrumentTypeName', before='ManufacturerName')

schema['description'].widget.visible = True
schema['description'].schemata = 'default'


def getDataInterfaces(context, export_only=False):
    """ Return the current list of data interfaces
    """
    from bika.lims.exportimport import instruments
    exims = []
    for exim_id in instruments.__all__:
        exim = instruments.getExim(exim_id)
        if export_only and not hasattr(exim, 'Export'):
            pass
        else:
            exims.append((exim_id, exim.title))
    exims.sort(lambda x, y: cmp(x[1].lower(), y[1].lower()))
    exims.insert(0, ('', t(_('None'))))
    return DisplayList(exims)

def getImportDataInterfaces(context, import_only=False):
    """ Return the current list of import data interfaces
    """
    from bika.lims.exportimport import instruments
    exims = []
    for exim_id in instruments.__all__:
        exim = instruments.getExim(exim_id)
        if import_only and not hasattr(exim, 'Import'):
            pass
        else:
            exims.append((exim_id, exim.title))
    exims.sort(lambda x, y: cmp(x[1].lower(), y[1].lower()))
    exims.insert(0, ('', t(_('None'))))
    return DisplayList(exims)

def getMaintenanceTypes(context):
    types = [('preventive', 'Preventive'),
             ('repair', 'Repair'),
             ('enhance', 'Enhancement')]
    return DisplayList(types)


def getCalibrationAgents(context):
    agents = [('analyst', 'Analyst'),
              ('maintainer', 'Maintainer')]
    return DisplayList(agents)


class Instrument(ATFolder):
    """A physical gadget of the lab
    """
    implements(IInstrument)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        return to_utf8(safe_unicode(self.title))

    def getExportDataInterfacesList(self):
        return getDataInterfaces(self, export_only=True)

    def getImportDataInterfacesList(self):
        return getImportDataInterfaces(self, import_only=True)

    def getScheduleTaskTypesList(self):
        return getMaintenanceTypes(self)

    def getMaintenanceTypesList(self):
        return getMaintenanceTypes(self)

    def getCalibrationAgentsList(self):
        return getCalibrationAgents(self)

    def getManufacturers(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(c.UID, c.Title)
                 for c in bsc(portal_type='Manufacturer',
                              inactive_state='active')]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(items)

    def getMethodUIDs(self):
        uids = []
        if self.getMethods():
            uids = [m.UID() for m in self.getMethods()]
        return uids

    def getSuppliers(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(c.UID, c.getName)
                 for c in bsc(portal_type='Supplier',
                              inactive_state='active')]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(items)

    def _getAvailableMethods(self):
        """ Returns the available (active) methods.
            One method can be done by multiple instruments, but one
            instrument can only be used in one method.
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(c.UID, c.Title)
                 for c in bsc(portal_type='Method',
                              inactive_state='active')]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        items.insert(0, ('', t(_('None'))))
        return DisplayList(items)

    def getInstrumentTypes(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(c.UID, c.Title)
                 for c in bsc(portal_type='InstrumentType',
                              inactive_state='active')]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(items)

    def getInstrumentLocations(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(c.UID, c.Title)
                 for c in bsc(portal_type='InstrumentLocation',
                              inactive_state='active')]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        items.insert(0, ('', t(_('None'))))
        return DisplayList(items)

    def getMaintenanceTasks(self):
        return self.objectValues('InstrumentMaintenanceTask')

    def getCalibrations(self):
        """ Return all calibration objects related with the instrument
        """
        return self.objectValues('InstrumentCalibration')

    def getCertifications(self):
        """ Returns the certifications of the instrument. Both internal
            and external certifitions
        """
        return self.objectValues('InstrumentCertification')

    def getValidCertifications(self):
        """ Returns the certifications fully valid
        """
        certs = []
        today = date.today()
        for c in self.getCertifications():
            validfrom = c.getValidFrom() if c else None
            validto = c.getValidTo() if validfrom else None
            if not validfrom or not validto:
                continue
            validfrom = validfrom.asdatetime().date()
            validto = validto.asdatetime().date()
            if (today >= validfrom and today <= validto):
                certs.append(c)
        return certs

    def isValid(self):
        """ Returns if the current instrument is not out for verification, calibration,
        out-of-date regards to its certificates and if the latest QC succeed
        """
        return self.isOutOfDate() is False \
            and self.isQCValid() is True \
            and self.getDisposeUntilNextCalibrationTest() is False \
            and self.isValidationInProgress() is False \
            and self.isCalibrationInProgress() is False

    def getLatestReferenceAnalyses(self):
        """ Returns a list with the latest Reference analyses performed
            for this instrument and Analysis Service.
            References the latest ReferenceAnalysis done for this instrument.
            Duplicate Analyses and Regular Analyses are not included.
            Only contains the last ReferenceAnalysis done for this
            instrument, Analysis Service and Reference type (blank or control).
            The list is created 'on-fly' if the method hasn't been already
            called or a new ReferenceAnalysis has been added by using
            addReferences() since its last call. Otherwise, uses the
            private accessor _LatestReferenceAnalyses as a cache
            (prevents overload).
            As an example:
            [0]: RefAnalysis for Ethanol, QC-001 (Blank)
            [1]: RefAnalysis for Ethanol, QC-002 (Control)
            [2]: RefAnalysis for Methanol, QC-001 (Blank)
        """
        field = self.getField('_LatestReferenceAnalyses')
        refs = field and field.get(self) or []
        if len(refs) == 0:
            latest = {}
            # Since the results file importer uses Date from the results
            # file as Analysis 'Capture Date', we cannot assume the last
            # item from the list is the latest analysis done, so we must
            # pick up the latest analyses using the Results Capture Date
            for ref in self.getReferenceAnalyses():
                antype = QCANALYSIS_TYPES.getValue(ref.getReferenceType())
                key = '%s.%s' % (ref.getServiceUID(), antype)
                last = latest.get(key, ref)
                if ref.getResultCaptureDate() > last.getResultCaptureDate():
                    latest[key] = ref
                else:
                    latest[key] = last
            refs = [r for r in latest.itervalues()]
            # Add to the cache
            self.getField('_LatestReferenceAnalyses').set(self, refs)
        return refs

    def isQCValid(self):
        """ Returns True if the instrument succeed for all the latest
            Analysis QCs performed (for diferent types of AS)
        """
        for last in self.getLatestReferenceAnalyses():
            rr = last.aq_parent.getResultsRangeDict()
            uid = last.getServiceUID()
            if uid not in rr:
                # This should never happen.
                # All QC Samples must have specs for its own AS
                continue

            specs = rr[uid]
            try:
                smin = float(specs.get('min', 0))
                smax = float(specs.get('max', 0))
                error = float(specs.get('error', 0))
                target = float(specs.get('result', 0))
                result = float(last.getResult())
                error_amount = ((target / 100) * error) if target > 0 else 0
                upper = smax + error_amount
                lower = smin - error_amount
                if result < lower or result > upper:
                    return False
            except:
                # This should never happen.
                # All Reference Analysis Results and QC Samples specs
                # must be floatable
                continue

        return True

    def isOutOfDate(self):
        """ Returns if the current instrument is out-of-date regards to
            its certifications
        """
        certification = self.getLatestValidCertification()
        if certification:
            return not certification.isValid()
        return True

    def isValidationInProgress(self):
        """ Returns if the current instrument is under validation progress
        """
        validation = self.getLatestValidValidation()
        if validation:
            return validation.isValidationInProgress()
        return False

    def isCalibrationInProgress(self):
        """ Returns if the current instrument is under calibration progress
        """
        calibration = self.getLatestValidCalibration()
        if calibration is not None:
            return calibration.isCalibrationInProgress()
        return False

    def getCertificateExpireDate(self):
        """ Returns the current instrument's data expiration certificate
        """
        certification = self.getLatestValidCertification()
        if certification:
            return certification.getValidTo()
        return None

    def getWeeksToExpire(self):
        """ Returns the amount of weeks and days untils it's certification expire
        """
        certification = self.getLatestValidCertification()
        if certification:
            return certification.getWeeksAndDaysToExpire()
        return 0, 0

    def getLatestValidCertification(self):
        """Returns the certification with the most remaining days until expiration.
           If no certification was found, it returns None.
        """

        # 1. get all certifications
        certifications = self.getCertifications()

        # 2. filter out certifications, which are invalid
        valid_certifications = filter(lambda x: x.isValid(), certifications)

        # 3. sort by the remaining days to expire, e.g. [10, 7, 6, 1]
        def sort_func(x, y):
            return cmp(x.getDaysToExpire(), y.getDaysToExpire())
        sorted_certifications = sorted(valid_certifications, cmp=sort_func, reverse=True)

        # 4. return the certification with the most remaining days
        if len(sorted_certifications) > 0:
            return sorted_certifications[0]
        return None

    def getLatestValidValidation(self):
        """Returns the validation with the most remaining days in validation.
           If no validation was found, it returns None.
        """
        # 1. get all validations
        validations = self.getValidations()

        # 2. filter out validations, which are not in progress
        active_validations = filter(lambda x: x.isValidationInProgress(), validations)

        # 3. sort by the remaining days in validation, e.g. [10, 7, 6, 1]
        def sort_func(x, y):
            return cmp(x.getRemainingDaysInValidation(), y.getRemainingDaysInValidation())
        sorted_validations = sorted(active_validations, cmp=sort_func, reverse=True)

        # 4. return the validation with the most remaining days
        if len(sorted_validations) > 0:
            return sorted_validations[0]
        return None

    def getLatestValidCalibration(self):
        """Returns the calibration with the most remaining days in calibration.
           If no calibration was found, it returns None.
        """
        # 1. get all calibrations
        calibrations = self.getCalibrations()

        # 2. filter out calibrations, which are not in progress
        active_calibrations = filter(lambda x: x.isCalibrationInProgress(), calibrations)

        # 3. sort by the remaining days in calibration, e.g. [10, 7, 6, 1]
        def sort_func(x, y):
            return cmp(x.getRemainingDaysInCalibration(), y.getRemainingDaysInCalibration())
        sorted_calibrations = sorted(active_calibrations, cmp=sort_func, reverse=True)

        # 4. return the calibration with the most remaining days
        if len(sorted_calibrations) > 0:
            return sorted_calibrations[0]
        return None

    def getValidations(self):
        """ Return all the validations objects related with the instrument
        """
        return self.objectValues('InstrumentValidation')

    def getDocuments(self):
        """ Return all the multifile objects related with the instrument
        """
        return self.objectValues('Multifile')

    def getSchedule(self):
        return self.objectValues('InstrumentScheduledTask')
#        pc = getToolByName(self, 'portal_catalog')
#        uid = self.context.UID()
#        return [p.getObject() for p in pc(portal_type='InstrumentScheduleTask',
#                                          getInstrumentUID=uid)]

    def getReferenceAnalyses(self):
        """ Returns an array with the subset of Controls and Blanks
            analysis objects, performed using this instrument.
            Reference Analyses can be from a Worksheet or directly
            generated using Instrument import tools, without need to
            create a new Worksheet.
            The rest of the analyses (regular and duplicates) will not
            be returned.
        """
        bac = getToolByName(self, 'bika_analysis_catalog')
        brains = bac(portal_type='ReferenceAnalysis',
                     getInstrumentUID=self.UID())
        return [brain.getObject() for brain in brains]

    def addAnalysis(self, analysis):
        """ Add regular analysis (included WS QCs) to this instrument
            If the analysis has
        """
        targetuid = analysis.getInstrumentUID()
        if not targetuid:
            return
        if targetuid != self.UID():
            raise Exception("Invalid instrument")
        ans = self.getAnalyses() if self.getAnalyses() else []
        ans.append(analysis)
        self.setAnalyses(ans)
        self.cleanReferenceAnalysesCache()

    def removeAnalysis(self, analysis):
        """ Remove a regular analysis assigned to this instrument
        """
        targetuid = analysis.getInstrumentUID()
        if not targetuid:
            return
        if targetuid != self.UID():
            raise Exception("Invalid instrument")
        uid = analysis.UID()
        ans = [a for a in self.getAnalyses() if a.UID() != uid]
        self.setAnalyses(ans)
        self.cleanReferenceAnalysesCache()

    def cleanReferenceAnalysesCache(self):
        self.getField('_LatestReferenceAnalyses').set(self, [])

    def addReferences(self, reference, service_uids):
        """ Add reference analyses to reference
        """
        addedanalyses = []
        wf = getToolByName(self, 'portal_workflow')
        bsc = getToolByName(self, 'bika_setup_catalog')
        bac = getToolByName(self, 'bika_analysis_catalog')
        ref_type = reference.getBlank() and 'b' or 'c'
        ref_uid = reference.UID()
        postfix = 1
        for refa in reference.getReferenceAnalyses():
            grid = refa.getReferenceAnalysesGroupID()
            try:
                cand = int(grid.split('-')[2])
                if cand >= postfix:
                    postfix = cand + 1
            except:
                pass
        postfix = str(postfix).zfill(int(3))
        refgid = 'I%s-%s' % (reference.id, postfix)
        for service_uid in service_uids:
            # services with dependents don't belong in references
            service = bsc(portal_type='AnalysisService', UID=service_uid)[0].getObject()
            calc = service.getCalculation()
            if calc and calc.getDependentServices():
                continue
            ref_uid = reference.addReferenceAnalysis(service_uid, ref_type)
            ref_analysis = bac(portal_type='ReferenceAnalysis', UID=ref_uid)[0].getObject()

            # Set ReferenceAnalysesGroupID (same id for the analyses from
            # the same Reference Sample and same Worksheet)
            # https://github.com/bikalabs/Bika-LIMS/issues/931
            ref_analysis.setReferenceAnalysesGroupID(refgid)
            ref_analysis.reindexObject()

            # copy the interimfields
            if calc:
                ref_analysis.setInterimFields(calc.getInterimFields())

            # Comes from a worksheet or has been attached directly?
            ws = ref_analysis.getBackReferences('WorksheetAnalysis')
            if not ws or len(ws) == 0:
                # This is a reference analysis attached directly to the
                # Instrument, we apply the assign state
                wf.doActionFor(ref_analysis, 'assign')
            addedanalyses.append(ref_analysis)

        self.setAnalyses(self.getAnalyses() + addedanalyses)

        # Initialize LatestReferenceAnalyses cache
        self.cleanReferenceAnalysesCache()

        # Set DisposeUntilNextCalibrationTest to False
        if (len(addedanalyses) > 0):
            self.getField('DisposeUntilNextCalibrationTest').set(self, False)

        return addedanalyses

    def getAnalysesToRetract(self, allanalyses=True, outofdate=False):
        """ If the instrument is not valid due to fail on latest QC
            Tests or a Calibration Test, returns the validation-pending
            Analyses with this instrument assigned.
            If allanalyses is False, only returns the analyses from
            the same Analysis Service as the failed QC/s or Calibration
            Tests.
            Only regular and duplicate analyses are returned.
            By default, only checks if latest QCs for this instrument are
            valid. If the instrument is out of date but the latest QC
            is valid, the method will retorn an empty list.
            Use outofdate=True to take also into account if the
            instrument's calibration certificate is out of date.
        """
        isvalid = self.isQCValid() if outofdate else self.isValid()
        if isvalid:
            return []

        bac = getToolByName(self, 'bika_analysis_catalog')
        prox = bac(portal_type=['Analysis', 'DuplicateAnalysis'],
                   review_state='to_be_verified')
        ans = [p.getObject() for p in prox]
        return [a for a in ans if a.getInstrumentUID() == self.UID()]

    def setImportDataInterface(self, values):
        """ Return the current list of import data interfaces
        """
        exims = self.getImportDataInterfacesList()
        new_values = [value for value in values if value in exims]
        if len(new_values) < len(values):
            logger.warn("Some Interfaces weren't added...")
        self.Schema().getField('ImportDataInterface').set(self, new_values)

    def displayValue(self, vocab, value, widget):
        """Overwrite the Script (Python) `displayValue.py` located at
           `Products.Archetypes.skins.archetypes` to handle the references
           of our Picklist Widget (Methods) gracefully.
           This method gets called by the `picklist.pt` template like this:

           display python:context.displayValue(vocab, value, widget);"
        """
        # Taken from the Script (Python)
        t = self.restrictedTraverse('@@at_utils').translate

        # ensure we have strings, otherwise the `getValue` method of
        # Products.Archetypes.utils will raise a TypeError
        def to_string(v):
            if isinstance(v, basestring):
                return v
            return api.get_title(v)

        if isinstance(value, (list, tuple)):
            value = map(to_string, value)

        return t(vocab, value, widget)


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)

registerType(Instrument, PROJECTNAME)
