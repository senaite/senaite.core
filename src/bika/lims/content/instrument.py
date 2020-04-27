# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from datetime import date

from AccessControl import ClassSecurityInfo

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Archetypes.atapi import DisplayList, PicklistWidget
from Products.Archetypes.atapi import registerType
from bika.lims.api.analysis import is_out_of_range
from bika.lims.catalog.analysis_catalog import CATALOG_ANALYSIS_LISTING

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
from Products.Archetypes.atapi import MultiSelectionWidget
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.browser.widgets import RecordsWidget
from bika.lims.browser.widgets import ReferenceWidget

# bika.lims imports
from bika.lims import api
from bika.lims import logger
from bika.lims.utils import t
from bika.lims.utils import to_utf8
from bika.lims.config import PROJECTNAME
from bika.lims.exportimport import instruments
from bika.lims.interfaces import IInstrument, IDeactivable
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
        widget=ReferenceWidget(
            label=_("Instrument type"),
            showOn=True,
            catalog_name='bika_setup_catalog',
            base_query={
                "is_active": True,
                "sort_on": "sortable_title",
                "sort_order": "ascending",
            },
        ),
    ),

    ReferenceField(
        'Manufacturer',
        allowed_types=('Manufacturer',),
        relationship='InstrumentManufacturer',
        required=1,
        widget=ReferenceWidget(
            label=_("Manufacturer"),
            showOn=True,
            catalog_name='bika_setup_catalog',
            base_query={
                "is_active": True,
                "sort_on": "sortable_title",
                "sort_order": "ascending",
            },
        ),
    ),

    ReferenceField(
        'Supplier',
        allowed_types=('Supplier',),
        relationship='InstrumentSupplier',
        required=1,
        widget=ReferenceWidget(
            label=_("Supplier"),
            showOn=True,
            catalog_name='bika_setup_catalog',
            base_query={
                "is_active": True,
                "sort_on": "sortable_title",
                "sort_order": "ascending",
            },
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

    # TODO Remove Instrument.Method field (functionality provided by 'Methods')
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

    ComputedField(
        'Valid',
        expression="'1' if context.isValid() else '0'",
        widget=ComputedWidget(
            visible=False,
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
        allowed_types=('InstrumentLocation', ),
        relationship='InstrumentInstrumentLocation',
        required=0,
        widget=ReferenceWidget(
            label=_("Instrument Location"),
            description=_("The room and location where the instrument is installed"),
            showOn=True,
            catalog_name='bika_setup_catalog',
            base_query={
                "is_active": True,
                "sort_on": "sortable_title",
                "sort_order": "ascending",
            },
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

schema['description'].widget.visible = True
schema['description'].schemata = 'default'

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
    implements(IInstrument, IDeactivable)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        return to_utf8(safe_unicode(self.title))

    def getDataInterfacesList(self, type_interface="import"):
        interfaces = list()
        if type_interface == "export":
            interfaces = instruments.get_instrument_export_interfaces()
        elif type_interface == "import":
            interfaces = instruments.get_instrument_import_interfaces()
        interfaces = map(lambda imp: (imp[0], imp[1].title), interfaces)
        interfaces.sort(lambda x, y: cmp(x[1].lower(), y[1].lower()))
        interfaces.insert(0, ('', t(_('None'))))
        return DisplayList(interfaces)

    def getExportDataInterfacesList(self):
        return self.getDataInterfacesList("export")

    def getImportDataInterfacesList(self):
        return self.getDataInterfacesList("import")

    def getScheduleTaskTypesList(self):
        return getMaintenanceTypes(self)

    def getMaintenanceTypesList(self):
        return getMaintenanceTypes(self)

    def getCalibrationAgentsList(self):
        return getCalibrationAgents(self)

    def getMethodUIDs(self):
        uids = []
        if self.getMethods():
            uids = [m.UID() for m in self.getMethods()]
        return uids

    def _getAvailableMethods(self):
        """ Returns the available (active) methods.
            One method can be done by multiple instruments, but one
            instrument can only be used in one method.
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(c.UID, c.Title)
                 for c in bsc(portal_type='Method',
                              is_active=True)]
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

    def isQCValid(self):
        """ Returns True if the results of the last batch of QC Analyses
        performed against this instrument was within the valid range.

        For a given Reference Sample, more than one Reference Analyses assigned
        to this same instrument can be performed and the Results Capture Date
        might slightly differ amongst them. Thus, this function gets the latest
        QC Analysis performed, looks for siblings (through RefAnalysisGroupID)
        and if the results for all them are valid, then returns True. If there
        is one single Reference Analysis from the group with an out-of-range
        result, the function returns False
        """
        query = {"portal_type": "ReferenceAnalysis",
                 "getInstrumentUID": self.UID(),
                 "sort_on": "getResultCaptureDate",
                 "sort_order": "reverse",
                 "sort_limit": 1,}
        brains = api.search(query, CATALOG_ANALYSIS_LISTING)
        if len(brains) == 0:
            # There are no Reference Analyses assigned to this instrument yet
            return True

        # Look for siblings. These are the QC Analyses that were created
        # together with this last ReferenceAnalysis and for the same Reference
        # Sample. If they were added through "Add Reference Analyses" in a
        # Worksheet, they typically appear in the same slot.
        group_id = brains[0].getReferenceAnalysesGroupID
        query = {"portal_type": "ReferenceAnalysis",
                 "getInstrumentUID": self.UID(),
                 "getReferenceAnalysesGroupID": group_id,}
        brains = api.search(query, CATALOG_ANALYSIS_LISTING)
        for brain in brains:
            analysis = api.get_object(brain)
            results_range = analysis.getResultsRange()
            if not results_range:
                continue
            # Is out of range?
            out_of_range = is_out_of_range(analysis)[0]
            if out_of_range:
                return False

        # By default, in range
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

    def addReferences(self, reference, service_uids):
        """ Add reference analyses to reference
        """
        # TODO Workflow - Analyses. Assignment of refanalysis to Instrument
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
            ref_analysis = reference.addReferenceAnalysis(service)

            # Set ReferenceAnalysesGroupID (same id for the analyses from
            # the same Reference Sample and same Worksheet)
            # https://github.com/bikalabs/Bika-LIMS/issues/931
            ref_analysis.setReferenceAnalysesGroupID(refgid)
            ref_analysis.setInstrument(self)
            ref_analysis.reindexObject()
            addedanalyses.append(ref_analysis)

        # Set DisposeUntilNextCalibrationTest to False
        if (len(addedanalyses) > 0):
            self.getField('DisposeUntilNextCalibrationTest').set(self, False)

        return addedanalyses

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
