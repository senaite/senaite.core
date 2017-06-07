# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from datetime import date

from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes.atapi import *
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims import deprecated
from bika.lims import logger
from bika.lims.config import PROJECTNAME
from bika.lims.config import QCANALYSIS_TYPES
from bika.lims.content.schema.instrument import schema
from bika.lims.interfaces import IInstrument
from bika.lims.utils import t
from bika.lims.utils import to_utf8
from plone.app.folder.folder import ATFolder
from zope.interface import implements


# noinspection PyUnusedLocal
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


# noinspection PyUnusedLocal
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


# noinspection PyUnusedLocal
def getMaintenanceTypes(context):
    types = [('preventive', 'Preventive'),
             ('repair', 'Repair'),
             ('enhance', 'Enhancement')]
    return DisplayList(types)


# noinspection PyUnusedLocal
def getCalibrationAgents(context):
    agents = [('analyst', 'Analyst'),
              ('maintainer', 'Maintainer')]
    return DisplayList(agents)


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
        manufacturers = bsc(portal_type='Manufacturer', inactive_state='active')
        items = [(c.UID, c.Title) for c in manufacturers]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(items)

    @deprecated('[1702] Orphan. No alternative')
    def getMethodUID(self):
        # TODO Avoid using this function. Returns first method's UID for now.
        if self.getMethods():
            return self.getMethods()[0].UID()

    def getMethodUIDs(self):
        uids = []
        if self.getMethods():
            uids = [m.UID() for m in self.getMethods()]
        return uids

    def getSuppliers(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        suppliers = bsc(portal_type='Supplier', inactive_state='active')
        items = [(c.UID, c.getName) for c in suppliers]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(items)

    def _getAvailableMethods(self):
        """ Returns the available (active) methods.
            One method can be done by multiple instruments, but one
            instrument can only be used in one method.
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        methods = bsc(portal_type='Method', inactive_state='active')
        items = [(c.UID, c.Title) for c in methods]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        items.insert(0, ('', t(_('None'))))
        return DisplayList(items)

    def getInstrumentTypes(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        instruments = bsc(portal_type='InstrumentType', inactive_state='active')
        items = [(c.UID, c.Title) for c in instruments]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(items)

    def getInstrumentLocations(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        locations = bsc(portal_type='InstrumentLocation',
                        inactive_state='active')
        items = [(c.UID, c.Title) for c in locations]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        items.insert(0, ('', t(_('None'))))
        return DisplayList(items)

    def getMaintenanceTasks(self):
        return self.objectValues('InstrumentMaintenanceTask')

    def getCalibrations(self):
        """
        Return all calibration objects related with the instrument
        """
        return self.objectValues('InstrumentCalibration')

    def getCertifications(self):
        """ Returns the certifications of the instrument. Both internal
            and external certifitions
        """
        return [c for c in self.objectValues('InstrumentCertification') if c]

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
            if today >= validfrom and today <= validto:
                certs.append(c)
        return certs

    def isValid(self):
        """ Returns if the current instrument is not out for verification, 
        calibration,
        out-of-date regards to its certificates and if the latest QC succeed
        """
        if self.isOutOfDate() is False \
                and self.isQCValid() is True \
                and self.getDisposeUntilNextCalibrationTest() is False \
                and self.isValidationInProgress() is False \
                and self.isCalibrationInProgress() is False:
            return True

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
            except (ValueError, TypeError):
                # This should never happen.
                # All Reference Analysis Results and QC Samples specs
                # must be floatable
                continue

        return True

    def isOutOfDate(self):
        """ Returns if the current instrument is out-of-date regards to
            its certifications
        """
        cert = self.getLatestValidCertification()
        today = date.today()
        if cert and cert.getValidTo():
            validto = cert.getValidTo().asdatetime().date()
            if validto > today:
                return False
        return True

    def isValidationInProgress(self):
        """ Returns if the current instrument is under validation progress
        """
        validation = self.getLatestValidValidation()
        today = date.today()
        if validation and validation.getDownTo():
            validfrom = validation.getDownFrom().asdatetime().date()
            validto = validation.getDownTo().asdatetime().date()
            if validfrom <= today <= validto:
                return True
        return False

    def isCalibrationInProgress(self):
        """ Returns if the current instrument is under calibration progress
        """
        calibration = self.getLatestValidCalibration()
        today = date.today()
        if calibration and calibration.getDownTo():
            validfrom = calibration.getDownFrom().asdatetime().date()
            validto = calibration.getDownTo().asdatetime().date()
            if validfrom <= today <= validto:
                return True
        return False

    def getCertificateExpireDate(self):
        """ Returns the current instrument's data expiration certificate
        """
        cert = self.getLatestValidCertification()
        if not cert:
            return ''
        d = cert.getValidTo()
        return d

    def getWeeksToExpire(self):
        """ Returns the amount of weeks untils it's certification expire
        """
        cert = self.getLatestValidCertification()
        if not cert:
            return ''
        d = cert.getValidTo().asdatetime().date()
        return d - d.today()

    def getLatestValidCertification(self):
        """ Returns the latest valid certification. If no latest valid
            certification found, returns None
        """
        cert = None
        lastfrom = None
        lastto = None
        for c in self.getCertifications():
            validfrom = c.getValidFrom() if c else None
            validto = c.getValidTo() if validfrom else None
            if not validfrom or not validto:
                continue
            validfrom = validfrom.asdatetime().date()
            validto = validto.asdatetime().date()
            if not cert \
                    or validto > lastto \
                    or (validto == lastto and validfrom > lastfrom):
                cert = c
                lastfrom = validfrom
                lastto = validto
        return cert

    def getLatestValidValidation(self):
        """ Returns the latest valid validation. If no latest valid
            validation found, returns None
        """
        validation = None
        lastfrom = None
        lastto = None
        for v in self.getValidations():
            validfrom = v.getDownFrom() if v else None
            validto = v.getDownTo() if validfrom else None
            if not validfrom or not validto:
                continue
            validfrom = validfrom.asdatetime().date()
            validto = validto.asdatetime().date()
            if not validation \
                    or validto > lastto \
                    or (validto == lastto and validfrom > lastfrom):
                validation = v
                lastfrom = validfrom
                lastto = validto
        return validation

    def getLatestValidCalibration(self):
        """ Returns the latest valid calibration. If no latest valid
            calibration found, returns None
        """
        calibration = None
        lastfrom = None
        lastto = None
        for c in self.getCalibrations():
            validfrom = c.getDownFrom() if c else None
            validto = c.getDownTo() if validfrom else None
            if not validfrom or not validto:
                continue
            validfrom = validfrom.asdatetime().date()
            validto = validto.asdatetime().date()
            if not calibration \
                    or validto > lastto \
                    or (validto == lastto and validfrom > lastfrom):
                calibration = c
                lastfrom = validfrom
                lastto = validto
        return calibration

    def getValidations(self):
        """
        Return all the validations objects related with the instrument
        """
        return self.objectValues('InstrumentValidation')

    def getDocuments(self):
        """
        Return all the multifile objects related with the instrument
        """
        return self.objectValues('Multifile')

    def getSchedule(self):
        return self.objectValues('InstrumentScheduledTask')

    #        pc = getToolByName(self, 'portal_catalog')
    #        uid = self.context.UID()
    #        return [p.getObject() for p in pc(
    # portal_type='InstrumentScheduleTask',
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
        postfix = 1
        for refa in reference.getReferenceAnalyses():
            grid = refa.getReferenceAnalysesGroupID()
            try:
                cand = int(grid.split('-')[2])
                if cand >= postfix:
                    postfix = cand + 1
            except (ValueError, TypeError):
                pass
        postfix = str(postfix).zfill(int(3))
        refgid = 'I%s-%s' % (reference.id, postfix)
        for service_uid in service_uids:
            # services with dependents don't belong in references
            brains = bsc(portal_type='AnalysisService', UID=service_uid)
            service = brains[0].getObject()
            calc = service.getCalculation()
            if calc and calc.getDependentServices():
                continue
            ref_uid = reference.addReferenceAnalysis(service_uid, ref_type)
            brains = bac(portal_type='ReferenceAnalysis', UID=ref_uid)
            ref_analysis = brains[0].getObject()

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

        # Initialize LatestReferenceAnalyses cache
        self.cleanReferenceAnalysesCache()

        # Set DisposeUntilNextCalibrationTest to False
        if len(addedanalyses) > 0:
            self.getField('DisposeUntilNextCalibrationTest').set(self, False)

        return addedanalyses

    # noinspection PyUnusedLocal
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


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)

registerType(Instrument, PROJECTNAME)
