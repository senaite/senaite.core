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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

import six
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.interfaces import IRoutineAnalysis
from Products.CMFCore.utils import getToolByName
from senaite.core.api import dtime
from senaite.core.catalog import ANALYSIS_CATALOG
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.catalog import SENAITE_CATALOG
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.exportimport.instruments.logger import Logger
from senaite.core.i18n import translate as t
from senaite.core.idserver import renameAfterCreation
from zope import deprecation

# BBB
from senaite.core.exportimport.instruments.parser import *  # noqa

deprecation.deprecated(
    "InstrumentResultsFileParser",
    "Moved to senaite.core.exportimport.instruments.parser")

deprecation.deprecated(
    "InstrumentCSVResultsFileParser",
    "Moved to senaite.core.exportimport.instruments.parser")

deprecation.deprecated(
    "InstrumentTXTResultsFileParser",
    "Moved to senaite.core.exportimport.instruments.parser")


class AnalysisResultsImporter(Logger):
    """Results importer
    """

    def __init__(self, parser, context,
                 override=[False, False],
                 allowed_ar_states=None,
                 allowed_analysis_states=None,
                 instrument_uid=None):
        Logger.__init__(self)
        self._parser = parser
        self.context = context
        self._allowed_ar_states = allowed_ar_states
        self._allowed_analysis_states = allowed_analysis_states
        self._override = override
        self._idsearch = ['getId', 'getClientSampleID']
        self._priorizedsearchcriteria = ''

        self.bsc = getToolByName(self.context, SETUP_CATALOG)
        self.bac = getToolByName(self.context, ANALYSIS_CATALOG)
        self.ar_catalog = getToolByName(self.context, SAMPLE_CATALOG)
        self.bc = getToolByName(self.context, SENAITE_CATALOG)
        self.wf = getToolByName(self.context, 'portal_workflow')

        if not self._allowed_ar_states:
            self._allowed_ar_states = ['sample_received',
                                       'to_be_verified']
        if not self._allowed_analysis_states:
            self._allowed_analysis_states = [
                'unassigned', 'assigned', 'to_be_verified'
            ]
        if not self._idsearch:
            self._idsearch = ['getId']
        self.instrument_uid = instrument_uid

    def getParser(self):
        """ Returns the parser that will be used for the importer
        """
        return self._parser

    def getAllowedARStates(self):
        """ The allowed Analysis Request states
            The results import will only take into account the analyses
            contained inside an Analysis Request which current state is one
            from these.
        """
        return self._allowed_ar_states

    def getAllowedAnalysisStates(self):
        """ The allowed Analysis states
            The results import will only take into account the analyses
            if its current state is in the allowed analysis states.
        """
        return self._allowed_analysis_states

    def getOverride(self):
        """ If the importer must override previously entered results.
            [False, False]: The results will not be overriden
            [True, False]: The results will be overriden only if there's no
                           result entered yet,
            [True, True]: The results will be always overriden, also if the
                          parsed result is empty.
        """
        return self._override

    def getKeywordsToBeExcluded(self):
        """ Returns an array with the analysis codes/keywords to be excluded
            by the importer. By default, an empty array
        """
        return []

    def process(self):
        self._parser.parse()
        parsed = self._parser.resume()
        self._errors = self._parser.errors
        self._warns = self._parser.warns
        self._logs = self._parser.logs
        self._priorizedsearchcriteria = ''

        if parsed is False:
            return False

        # Allowed analysis states
        allowed_ar_states_msg = [t(_(s)) for s in self.getAllowedARStates()]
        allowed_an_states_msg = [
                t(_(s)) for s in self.getAllowedAnalysisStates()]
        self.log("Allowed Sample states: ${allowed_states}",
                 mapping={'allowed_states': ', '.join(allowed_ar_states_msg)})
        self.log("Allowed analysis states: ${allowed_states}",
                 mapping={'allowed_states': ', '.join(allowed_an_states_msg)})

        # Exclude non existing ACODEs
        acodes = []
        ancount = 0
        instprocessed = []
        importedars = {}
        importedinsts = {}
        rawacodes = self._parser.getAnalysisKeywords()
        exclude = self.getKeywordsToBeExcluded()
        updated_analyses = []
        for acode in rawacodes:
            if acode in exclude or not acode:
                continue
            analysis_service = self.bsc(getKeyword=acode)
            if not analysis_service:
                self.warn('Service keyword ${analysis_keyword} not found',
                          mapping={"analysis_keyword": acode})
            else:
                acodes.append(acode)
        if len(acodes) == 0:
            self.warn("Service keywords: no matches found")

        # Attachments will be created in any worksheet that contains
        # analyses that are updated by this import
        attachments = {}
        infile = self._parser.getInputFile()

        for objid, results in six.iteritems(self._parser.getRawResults()):
            # Allowed more than one result for the same sample and analysis.
            # Needed for calibration tests
            for result in results:
                analyses = self._getZODBAnalyses(objid)
                inst = None
                if len(analyses) == 0 and self.instrument_uid:
                    # No registered analyses found, but maybe we need to
                    # create them first if an instruemnt id has been set in
                    insts = self.bsc(portal_type='Instrument',
                                     UID=self.instrument_uid)
                    if len(insts) == 0:
                        # No instrument found
                        self.warn("No Sample with "
                                  "'${allowed_ar_states}' "
                                  "states found, And no QC"
                                  "analyses found for ${object_id}",
                                  mapping={"allowed_ar_states": ', '.join(
                                      allowed_ar_states_msg),
                                          "object_id": objid})
                        self.warn("Instrument not found")
                        continue

                    inst = insts[0].getObject()

                    # Create a new ReferenceAnalysis and link it to
                    # the Instrument
                    # Here we have an objid (i.e. R01200012) and
                    # a dict with results (the key is the AS keyword).
                    # How can we create a ReferenceAnalysis if we don't know
                    # which ReferenceSample we might use?
                    # Ok. The objid HAS to be the ReferenceSample code.
                    refsample = self.bc(portal_type='ReferenceSample', id=objid)
                    if refsample and len(refsample) == 1:
                        refsample = refsample[0].getObject()

                    elif refsample and len(refsample) > 1:
                        # More than one reference sample found!
                        self.warn(
                            "More than one reference sample found for"
                            "'${object_id}'",
                            mapping={"object_id": objid})
                        continue

                    else:
                        # No reference sample found!
                        self.warn("No Reference Sample found for ${object_id}",
                                  mapping={"object_id": objid})
                        continue

                    # For each acode, create a ReferenceAnalysis and attach it
                    # to the Reference Sample
                    services = self.bsc(portal_type='AnalysisService')
                    service_uids = [service.UID for service in services
                                    if service.getObject().getKeyword()
                                    in result.keys()]
                    analyses = inst.addReferences(refsample, service_uids)

                elif len(analyses) == 0:
                    # No analyses found
                    self.warn("No Sample with "
                              "'${allowed_ar_states}' "
                              "states neither QC analyses found "
                              "for ${object_id}",
                              mapping={
                                 "allowed_ar_states": ', '.join(
                                     allowed_ar_states_msg),
                                 "object_id": objid})
                    continue

                # Look for timestamp
                capturedate = result.get('DateTime', {}).get('DateTime', None)
                if capturedate:
                    del result['DateTime']
                for acode, values in six.iteritems(result):
                    if acode not in acodes:
                        # Analysis keyword doesn't exist
                        continue

                    ans = [
                        a for a in analyses
                        if a.getKeyword() == acode
                           and api.get_workflow_status_of(a)
                           in self._allowed_analysis_states]

                    if len(ans) > 1:
                        self.warn("More than one analysis found for "
                                  "${object_id} and ${analysis_keyword}",
                                  mapping={"object_id": objid,
                                           "analysis_keyword": acode})
                        continue

                    elif len(ans) == 0:
                        self.warn("No analyses found for ${object_id} "
                                  "and ${analysis_keyword}",
                                  mapping={"object_id": objid,
                                           "analysis_keyword": acode})
                        continue

                    analysis = ans[0]

                    # Create attachment in worksheet linked to this analysis.
                    # Only if this import has not already created the
                    # attachment
                    # And only if the filename of the attachment is unique in
                    # this worksheet.  Otherwise we will attempt to use
                    # existing attachment.
                    ws = analysis.getWorksheet()
                    if ws:
                        if ws.getId() not in attachments:
                            fn = infile.filename
                            fn_attachments = self.get_attachment_filenames(ws)
                            if fn in fn_attachments.keys():
                                attachments[ws.getId()] = fn_attachments[fn]
                            else:
                                attachments[ws.getId()] = \
                                    self.create_attachment(ws, infile)

                    if capturedate:
                        values['DateTime'] = capturedate
                    processed = self._process_analysis(objid, analysis, values)
                    if processed:
                        updated_analyses.append(analysis)
                        ancount += 1
                        if inst:
                            # Calibration Test (import to Instrument)
                            instprocessed.append(inst.UID())
                            importedinst = inst.title in importedinsts.keys() \
                                and importedinsts[inst.title] or []
                            if acode not in importedinst:
                                importedinst.append(acode)
                            importedinsts[inst.title] = importedinst
                        else:
                            ar = analysis.portal_type == 'Analysis' \
                                and analysis.aq_parent or None
                            if ar and ar.UID:
                                importedar = ar.getId() in importedars.keys() \
                                            and importedars[ar.getId()] or []
                                if acode not in importedar:
                                    importedar.append(acode)
                                importedars[ar.getId()] = importedar

                        if ws:
                            self.attach_attachment(
                                analysis, attachments[ws.getId()])
                        else:
                            self.warn(
                                "Attachment cannot be linked to analysis as "
                                "it is not assigned to a worksheet (%s)" %
                                analysis)

        # recalculate analyses with calculations after all results are set
        for analysis in updated_analyses:
            # only routine analyses can be used in calculations
            if IRoutineAnalysis.providedBy(analysis):
                sample_id = analysis.getRequestID()
                self.calculateTotalResults(sample_id, analysis)

        # reindex sample to update progress (and other indexes/metadata)
        samples = set(map(api.get_parent, updated_analyses))
        for sample in samples:
            sample.reindexObject()

        for arid, acodes in six.iteritems(importedars):
            acodesmsg = "Analysis %s" % ', '.join(acodes)
            self.log(
                "${request_id}: ${analysis_keywords} imported sucessfully",
                mapping={"request_id": arid, "analysis_keywords": acodesmsg})

        for instid, acodes in six.iteritems(importedinsts):
            acodesmsg = "Analysis %s" % ', '.join(acodes)
            msg = "%s: %s %s" % (instid, acodesmsg, "imported sucessfully")
            self.log(msg)

        if self.instrument_uid:
            self.log(
                "Import finished successfully: ${nr_updated_ars} Samples, "
                "${nr_updated_instruments} Instruments and "
                "${nr_updated_results} "
                "results updated",
                mapping={"nr_updated_ars": str(len(importedars)),
                         "nr_updated_instruments": str(len(importedinsts)),
                         "nr_updated_results": str(ancount)})
        else:
            self.log(
                "Import finished successfully: ${nr_updated_ars} Samples and "
                "${nr_updated_results} results updated",
                mapping={"nr_updated_ars": str(len(importedars)),
                         "nr_updated_results": str(ancount)})

    def create_mime_attachmenttype(self):
        # Create the AttachmentType for mime type if not exists
        attachmentType = self.bsc(portal_type="AttachmentType",
                                  title=self._parser.getAttachmentFileType())
        if not attachmentType:
            folder = self.context.bika_setup.bika_attachmenttypes
            obj = api.create(folder, "AttachmentType")
            obj.edit(title=self._parser.getAttachmentFileType(),
                     description="Autogenerated file type")
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            attuid = obj.UID()
        else:
            attuid = attachmentType[0].UID
        return attuid

    def create_attachment(self, ws, infile):
        attuid = self.create_mime_attachmenttype()
        attachment = None
        filename = infile.filename
        if attuid and infile:
            attachment = api.create(ws, "Attachment")
            logger.info("Creating %s in %s" % (attachment, ws))
            attachment.edit(
                title=filename,
                AttachmentFile=infile,
                AttachmentType=attuid,
                AttachmentKeys='Results, Automatic import',
                RenderInReport=False,
            )
            attachment.reindexObject()
        return attachment

    def attach_attachment(self, analysis, attachment):
        """
        Attach a file or a given set of files to an analysis

        :param analysis: analysis where the files are to be attached
        :param attachment: files to be attached. This can be either a
        single file or a list of files
        :return: None
        """
        if not attachment:
            return
        if isinstance(attachment, list):
            for attach in attachment:
                self.attach_attachment(analysis, attach)
            return
        # current attachments
        an_atts = analysis.getAttachment()
        atts_filenames = [att.getAttachmentFile().filename for att in an_atts]
        filename = attachment.getAttachmentFile().filename
        if filename not in atts_filenames:
            an_atts.append(attachment)
            logger.info(
                "Attaching %s to %s" % (attachment.UID(), analysis))
            analysis.setAttachment([att.UID() for att in an_atts])
            analysis.reindexObject()
        else:
            self.log("Attachment %s was already linked to analysis %s" %
                     (filename, api.get_id(analysis)))

    def get_attachment_filenames(self, ws):
        fn_attachments = {}
        for att in ws.objectValues('Attachment'):
            fn = att.getAttachmentFile().filename
            if fn not in fn_attachments:
                fn_attachments[fn] = []
            fn_attachments[fn].append(att)
        return fn_attachments

    def _getObjects(self, objid, criteria, states):
        # self.log("Criteria: %s %s") % (criteria, obji))
        obj = []
        if criteria in ['arid']:
            obj = self.ar_catalog(
                           getId=objid,
                           review_state=states)
        elif criteria == 'csid':
            obj = self.ar_catalog(
                           getClientSampleID=objid,
                           review_state=states)
        elif criteria == 'aruid':
            obj = self.ar_catalog(
                           UID=objid,
                           review_state=states)
        elif criteria == 'rgid':
            obj = self.bac(portal_type=['ReferenceAnalysis',
                                        'DuplicateAnalysis'],
                           getReferenceAnalysesGroupID=objid)
        elif criteria == 'rid':
            obj = self.bac(portal_type=['ReferenceAnalysis',
                                        'DuplicateAnalysis'], id=objid)
        elif criteria == 'ruid':
            obj = self.bac(portal_type=['ReferenceAnalysis',
                                        'DuplicateAnalysis'], UID=objid)
        if obj and len(obj) > 0:
            self._priorizedsearchcriteria = criteria
        return obj

    def _getZODBAnalyses(self, objid):
        """ Searches for analyses from ZODB to be filled with results.
            objid can be either AR ID or Worksheet's Reference Sample IDs.
            Only analyses that matches with getAnallowedAnalysisStates() will
            be returned. If not a ReferenceAnalysis, getAllowedARStates() is
            also checked.
            Returns empty array if no analyses found
        """
        # ars = []
        analyses = []
        searchcriteria = ['getId', 'getClientSampleID']
        allowed_ar_states = self.getAllowedARStates()
        allowed_an_states = self.getAllowedAnalysisStates()
        # allowed_ar_states_msg = [_(s) for s in allowed_ar_states]
        allowed_an_states_msg = [_(s) for s in allowed_an_states]

        # Acceleration of searches using priorization
        if self._priorizedsearchcriteria in ['rgid', 'rid', 'ruid']:
            # Look from reference analyses
            analyses = self._getZODBAnalysesFromReferenceAnalyses(
                    objid, self._priorizedsearchcriteria)
        if len(analyses) == 0:
            # Look from ar and derived
            analyses = self._getZODBAnalysesFromAR(objid,
                                                   '',
                                                   searchcriteria,
                                                   allowed_ar_states)

        # Discard analyses that don't match with allowed_an_states
        analyses = [analysis for analysis in analyses
                    if analysis.portal_type != 'Analysis' or
                    self.wf.getInfoFor(analysis, 'review_state')
                    in allowed_an_states]

        if len(analyses) == 0:
            self.warn(
                "No analyses '${allowed_analysis_states}' "
                "states found for ${object_id}",
                mapping={"allowed_analysis_states": ', '.join(
                    allowed_an_states_msg),
                         "object_id": objid})

        return analyses

    def _getZODBAnalysesFromAR(self, objid, criteria,
                               allowedsearches, arstates):
        ars = []
        analyses = []
        if criteria:
            ars = self._getObjects(objid, criteria, arstates)
            if not ars or len(ars) == 0:
                return self._getZODBAnalysesFromAR(objid, None,
                                                   allowedsearches, arstates)
        else:
            sortorder = ['arid', 'csid', 'aruid']
            for crit in sortorder:
                if (crit == 'arid' and 'getId' in allowedsearches) \
                    or (crit == 'csid' and 'getClientSampleID'
                                in allowedsearches) \
                        or (crit == 'aruid' and 'getId' in allowedsearches):
                    ars = self._getObjects(objid, crit, arstates)
                    if ars and len(ars) > 0:
                        break

        if not ars or len(ars) == 0:
            return self._getZODBAnalysesFromReferenceAnalyses(objid, None)

        elif len(ars) > 1:
            self.err("More than one Sample found for ${object_id}",
                     mapping={"object_id": objid})
            return []

        ar = ars[0].getObject()
        analyses = [analysis.getObject() for analysis in ar.getAnalyses()]

        return analyses

    def _getZODBAnalysesFromReferenceAnalyses(self, objid, criteria):
        analyses = []
        if criteria:
            refans = self._getObjects(objid, criteria, [])
            if len(refans) == 0:
                return []

            elif criteria == 'rgid':
                return [an.getObject() for an in refans]

            elif len(refans) == 1:
                # The search has been made using the internal identifier
                # from a Reference Analysis (id or uid). That is not usual.
                an = refans[0].getObject()
                worksheet = an.getWorksheet()
                if worksheet:
                    # A regular QC test (assigned to a Worksheet)
                    return [an, ]
                elif an.getInstrument():
                    # An Internal Calibration Test
                    return [an, ]
                else:
                    # Oops. This should never happen!
                    # A ReferenceAnalysis must be always assigned to
                    # a Worksheet (Regular QC) or to an Instrument
                    # (Internal Calibration Test)
                    self.err("The Reference Analysis ${object_id} has neither "
                             "instrument nor worksheet assigned",
                             mapping={"object_id": objid})
                    return []
            else:
                # This should never happen!
                # Fetching ReferenceAnalysis for its id or uid should
                # *always* return a unique result
                self.err(
                    "More than one Reference Analysis found for ${obect_id}",
                    mapping={"object_id": objid})
                return []

        else:
            sortorder = ['rgid', 'rid', 'ruid']
            for crit in sortorder:
                analyses = self._getZODBAnalysesFromReferenceAnalyses(objid,
                                                                      crit)
                if len(analyses) > 0:
                    return analyses

        return analyses

    def calculateTotalResults(self, objid, analysis):
        """ If an AR(objid) has an analysis that has a calculation
        then check if param analysis is used on the calculations formula.
        Here we are dealing with two types of analysis.
        1. Calculated Analysis - Results are calculated.
        2. Analysis - Results are captured and not calculated
        :param objid: AR ID or Worksheet's Reference Sample IDs
        :param analysis: Analysis Object
        """
        for obj in self._getZODBAnalyses(objid):
            # skip analyses w/o calculations
            if not obj.getCalculation():
                continue
            # get the calculation
            calculation = obj.getCalculation()
            # get the dependent services of the calculation
            dependencies = calculation.getDependentServices()
            # get the analysis service of the passed in analysis
            service = analysis.getAnalysisService()
            # skip when service is not a dependency of the calculation
            if service not in dependencies:
                continue
            # recalculate analysis result
            success = obj.calculateResult(override=self._override[0])
            if success:
                self.save_submit_analysis(obj)
                obj.reindexObject(idxs=["Result"])
                self.log(
                    "${request_id}: calculated result for "
                    "'${analysis_keyword}': '${analysis_result}'",
                    mapping={"request_id": objid,
                             "analysis_keyword": obj.getKeyword(),
                             "analysis_result": str(obj.getResult())})
                # recursively recalculate analyses that have this analysis as
                # a dependent service
                self.calculateTotalResults(objid, obj)

    def save_submit_analysis(self, analysis):
        """Submit analysis and ignore errors
        """
        try:
            api.do_transition_for(analysis, "submit")
        except api.APIError:
            pass

    def override_analysis_result(self, analysis):
        """Checks if the result shall be overwritten or not
        """
        result = analysis.getResult()
        override = self.getOverride()
        # analysis has non-empty result, but it is not allowed to override
        if result and override[0] is False:
            return False
        return True

    def _process_analysis(self, objid, analysis, values):
        # Check if the current analysis result can be overwritten
        if not self.override_analysis_result(analysis):
            keyword = analysis.getKeyword()
            result = analysis.getResult()
            self.log(
                "Analysis '{keyword}' has existing result of {result}, which "
                "is kept due to the no-override option selected".format(
                    keyword=keyword, result=result))
            return False

        resultsaved = False
        acode = analysis.getKeyword()
        defresultkey = values.get("DefaultResult", "")
        capturedate = None

        if "DateTime" in values.keys():
            ts = values.get("DateTime")
            capturedate = dtime.to_DT(ts)
            if capturedate is None:
                del values["DateTime"]

        fields_to_reindex = []
        # get interims
        interimsout = []
        interims = hasattr(analysis, 'getInterimFields') \
            and analysis.getInterimFields() or []
        for interim in interims:
            keyword = interim['keyword']
            title = interim['title']
            if values.get(keyword, '') or values.get(keyword, '') == 0:
                res = values.get(keyword)
                self.log("${request_id} result for "
                         "'${analysis_keyword}:${interim_keyword}': "
                         "'${result}'",
                         mapping={"request_id": objid,
                                  "analysis_keyword": acode,
                                  "interim_keyword": keyword,
                                  "result": str(res)}
                         )
                ninterim = interim.copy()
                ninterim['value'] = res
                interimsout.append(ninterim)
                resultsaved = True
            elif values.get(title, '') or values.get(title, '') == 0:
                res = values.get(title)
                self.log("%s/'%s:%s': '%s'" % (objid, acode, title, str(res)))
                ninterim = interim.copy()
                ninterim['value'] = res
                interimsout.append(ninterim)
                resultsaved = True
            else:
                interimsout.append(interim)

        # write interims
        if len(interimsout) > 0:
            analysis.setInterimFields(interimsout)
            resultsaved = analysis.calculateResult(override=self._override[0])

        # Set result if present.
        res = values.get(defresultkey, '')
        calc = analysis.getCalculation()

        # don't set results on calculated analyses
        if not calc:
            if api.is_floatable(res) or self._override[1]:
                # handle non-floating values in result options
                result_options = analysis.getResultOptions()
                if result_options:
                    result_values = map(
                        lambda r: r.get("ResultValue"), result_options)
                    if "{:.0f}".format(res) in result_values:
                        res = int(res)
                analysis.setResult(res)
                if capturedate:
                    analysis.setResultCaptureDate(capturedate)
                resultsaved = True

        if resultsaved is False:
            self.log(
                "${request_id} result for '${analysis_keyword}' not set",
                mapping={"request_id": objid,
                         "analysis_keyword": acode})

        if resultsaved:
            self.save_submit_analysis(analysis)
            fields_to_reindex.append('Result')
            self.log(
                "${request_id} result for '${analysis_keyword}': '${result}'",
                mapping={"request_id": objid,
                         "analysis_keyword": acode,
                         "result": res})

        if (resultsaved) \
           and values.get('Remarks', '') \
           and analysis.portal_type == 'Analysis' \
           and (analysis.getRemarks() != '' or self._override[1] is True):
            analysis.setRemarks(values['Remarks'])
            fields_to_reindex.append('Remarks')

        if len(fields_to_reindex):
            analysis.reindexObject(idxs=fields_to_reindex)
        return resultsaved
