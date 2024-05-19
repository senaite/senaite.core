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
from senaite.core.api import dtime
from senaite.core.catalog import ANALYSIS_CATALOG
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.catalog import SENAITE_CATALOG
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.exportimport.instruments.logger import Logger
from senaite.core.exportimport.instruments.parser import *  # noqa
from senaite.core.i18n import translate as t
from senaite.core.idserver import renameAfterCreation
from zope import deprecation
from zope.cachedescriptors.property import Lazy as lazy_property
from zope.deprecation import deprecate

ALLOWED_SAMPLE_STATES = ["sample_received", "to_be_verified"]
ALLOWED_ANALYSIS_STATES = ["unassigned", "assigned", "to_be_verified"]

deprecation.deprecated(
    "InstrumentResultsFileParser",
    "Moved to senaite.core.exportimport.instruments.parser")

deprecation.deprecated(
    "InstrumentCSVResultsFileParser",
    "Moved to senaite.core.exportimport.instruments.parser")

deprecation.deprecated(
    "InstrumentTXTResultsFileParser",
    "Moved to senaite.core.exportimport.instruments.parser")


class BaseResultsImporter(Logger):
    """Backwards compatible base results importer
    """
    def __init__(self):
        super(BaseResultsImporter, self).__init__()

    @property
    @deprecate("Please use self.wf_tool instead")
    def wf(self):
        return self.wf_tool

    @property
    @deprecate("Please use self.sample_catalog instead")
    def ar_catalog(self):
        return self.sample_catalog

    @property
    @deprecate("Please use self.analysis_catalog instead")
    def bac(self):
        return self.analysis_catalog

    @property
    @deprecate("Please use self.senaite_catalog instead")
    def bc(self):
        return self.senaite_catalog

    @property
    @deprecate("Please use self.setup_catalog instead")
    def bsc(self):
        # BBB
        return self.setup_catalog

    @lazy_property
    def sample_catalog(self):
        return api.get_tool(SAMPLE_CATALOG)

    @lazy_property
    def analysis_catalog(self):
        return api.get_tool(ANALYSIS_CATALOG)

    @lazy_property
    def setup_catalog(self):
        return api.get_tool(SETUP_CATALOG)

    @lazy_property
    def senaite_catalog(self):
        return api.get_tool(SENAITE_CATALOG)

    @lazy_property
    def wf_tool(self):
        return api.get_tool("portal_workflow")


class AnalysisResultsImporter(BaseResultsImporter):
    """Results importer
    """
    def __init__(self, parser, context,
                 override=None,
                 allowed_sample_states=None,
                 allowed_analysis_states=None,
                 instrument_uid=None):
        super(AnalysisResultsImporter, self).__init__()

        self.context = context

        # see lazy property below
        self._parser = parser

        # results override settings
        self.override = override
        if override is None:
            self.override = [False, False]

        # allowed sample states
        self.allowed_sample_states = allowed_sample_states
        if not allowed_sample_states:
            self.allowed_sample_states = ALLOWED_SAMPLE_STATES
        # translated states
        self.allowed_sample_states_msg = [
            t(_(s)) for s in self.allowed_sample_states]

        # allowed analyses states
        self.allowed_analysis_states = allowed_analysis_states
        if not allowed_analysis_states:
            self.allowed_analysis_states = ALLOWED_ANALYSIS_STATES
        self.allowed_analysis_states_msg = [
            t(_(s)) for s in self.allowed_analysis_states]

        # instrument UID
        self.instrument_uid = instrument_uid
        self.priorizedsearchcriteria = ""

        # BBB
        self._parser = parser
        self.allowed_ar_states = self.allowed_sample_states
        self._allowed_analysis_states = self.allowed_analysis_states
        self._override = self.override
        self._idsearch = ["getId", "getClientSampleID"]
        self._priorizedsearchcriteria = self.priorizedsearchcriteria

    @lazy_property
    def instrument(self):
        if not self.instrument_uid:
            return None
        return api.get_object(self.instrument_uid, None)

    @lazy_property
    def services(self):
        """Return all services
        """
        services = self.setup_catalog(portal_type="AnalysisService")
        return list(map(api.get_object, services))

    @lazy_property
    def parser(self):
        """Returns the parser that is used for the import
        """
        # Maybe we can use an adapter lookup here?
        return self._parser

    @deprecate("Please use self.parser instead")
    def getParser(self):
        return self.parser

    @deprecate("Please use self.allowed_sample_states instead")
    def getAllowedARStates(self):
        """BBB: Return allowed sample states

        The results import will only take into account the analyses contained
        inside an Samples which current state is one from these.
        """
        return self.allowed_sample_states

    @deprecate("Please use self.allowed_sample_states instead")
    def getAllowedAnalysisStates(self):
        """BBB: Return allowed analysis states

        The results import will only take into account the analyses if its
        current state is in the allowed analysis states.
        """
        return self.allowed_analysis_states

    @deprecate("Please use self.override instead")
    def getOverride(self):
        """BBB: Return result override flags

        Flags if the importer can override previously entered results.

        [False, False]: Results are not overriden (default)
        [True, False]:  Results are overriden, but only when empty
        [True, True]:   Results are always overriden, also with empties
        """
        return self.override

    def getKeywordsToBeExcluded(self):
        """Returns a list of analysis keywords to be excluded
        """
        return []

    def parse_results(self):
        """Parse the results file and return the raw results
        """
        parsed = self.parser.parse()

        if not parsed:
            return {}

        self.errors = self.parser.errors
        self.warns = self.parser.warns
        self.logs = self.parser.logs

        return self.parser.getRawResults()

    @lazy_property
    def keywords(self):
        """Return the parsed keywords
        """
        keywords = []
        for keyword in self.parser.getAnalysisKeywords():
            if not keyword:
                continue
            if keyword in self.getKeywordsToBeExcluded():
                continue
            # check if keyword is valid
            if not self.is_valid_keyword(keyword):
                self.warn(_("Service keyword ${analysis_keyword} not found",
                            mapping={"analysis_keyword": keyword}))
                continue
            # remember the valid service keyword
            keywords.append(keyword)

        if len(keywords) == 0:
            self.warn(_("No services could be found for parsed keywords"))

        return keywords

    def is_valid_keyword(self, keyword):
        """Check if the keyword is valid
        """
        results = self.setup_catalog(getKeyword=keyword)
        if not results:
            return False
        return True

    def get_reference_sample_by_id(self, sid):
        """Get a reference sample by ID
        """
        query = {"portal_type": "ReferenceSample", "getId": sid}
        results = api.search(query, SENAITE_CATALOG)
        if len(results) == 0:
            return None
        return api.get_object(results[0])

    def get_sample_by_id(self, sid):
        """Get a  sample by ID
        """
        query = {"portal_type": "AnalysisRequest", "getId": sid}
        results = api.search(query, SAMPLE_CATALOG)
        if len(results) == 0:
            return None
        return api.get_object(results[0])

    def get_analyses_for(self, sid):
        """Get analyses for the given sample ID
        """
        return self._getZODBAnalyses(sid)

    def process(self):
        parsed_results = self.parse_results()

        # no parsed results, return
        if not parsed_results:
            return False

        # Log allowed sample and analyses states
        self.log(_("Allowed sample states: ${allowed_states}", mapping={
            "allowed_states": ", ".join(self.allowed_sample_states_msg)
        }))
        self.log(_("Allowed analysis states: ${allowed_states}", mapping={
            "allowed_states": ", ".join(self.allowed_analysis_states_msg)
        }))

        # Attachments will be created in any worksheet that contains
        # analyses that are updated by this import
        attachments = {}
        infile = self.parser.getInputFile()

        ancount = 0
        updated_analyses = []
        importedinsts = {}
        importedars = {}

        for sid, results in parsed_results.items():
            # get the sample
            sample = self.get_sample_by_id(sid)
            refsample = None

            # fetch all analyses for the given sample ID
            analyses = self.get_analyses_for(sid)

            # No registered analyses found, but maybe we need to
            # create them first if we have an instrument
            if len(analyses) == 0 and not self.instrument:
                self.warn(_("Instrument not found"))
                self.warn(_("No Sample with '${allowed_ar_states}' states"
                            "found, and no QC analyses found for ${sid}",
                            mapping={
                                "allowed_ar_states": ", ".join(
                                    self.allowed_sample_states_msg),
                                "sid": sid}))
                continue

            # we have an instrument
            elif len(analyses) == 0 and self.instrument:
                # Create a new ReferenceAnalysis and link it to the Instrument.
                refsample = self.get_reference_sample_by_id(sid)
                if not refsample:
                    self.warn(_("No Reference Sample found for ${sid}",
                                mapping={"sid": sid}))
                    continue

                # Allowed are more than one result for the same sample and
                # analysis. Needed for calibration tests.
                service_uids = []
                for result in results:
                    # For each keyword, create a ReferenceAnalysis and attach
                    # it to the ReferenceSample
                    service_uids.extend([
                        api.get_uid(service) for service in self.services
                        if service.getKeyword() in result.keys()])

                analyses = self.instrument.addReferences(
                    refsample, list(set(service_uids)))

            # No analyses found
            elif len(analyses) == 0:
                self.warn(_("No Sample or Reference Sample found for ${sid} "
                            "in the states '${allowed_sample_states}' ",
                            mapping={
                                "allowed_sample_states": ", ".join(
                                    self.allowed_sample_states_msg),
                                "sid": sid,
                            }))
                continue

            # import the results
            for result in results:

                # XXX: Why this nested lookup and why delete it?
                # Look for timestamp
                capturedate = result.get("DateTime", {}).get("DateTime", None)
                if capturedate:
                    del result["DateTime"]

                for keyword, values in result.items():
                    if keyword not in self.keywords:
                        # Analysis keyword doesn't exist
                        continue

                    ans = [a for a in analyses if a.getKeyword() == keyword
                           and api.get_workflow_status_of(a)
                           in self.allowed_analysis_states]

                    analysis = None

                    if len(ans) == 0:
                        # no analysis found for keyword
                        self.warn(_("No analyses found for ${sid} "
                                    "and keyword '${keyword}'",
                                  mapping={"sid": sid,
                                           "keyword": keyword}))
                        continue
                    elif len(ans) > 1:
                        # multiple analyses found for keyword
                        self.warn(_("More than one analysis found for "
                                    "${sid} and keyword '${keyword}'",
                                  mapping={"sid": sid,
                                           "keyword": keyword}))
                        continue
                    else:
                        analysis = ans[0]

                    # Create attachment in worksheet linked to this analysis.
                    # Only if this import has not already created the
                    # attachment And only if the filename of the attachment is
                    # unique in this worksheet.
                    # Otherwise we will attempt to use existing attachment.
                    ws = analysis.getWorksheet()
                    if ws:
                        wsid = ws.getId()
                        if wsid not in attachments:
                            fn = infile.filename
                            fn_attachments = self.get_attachment_filenames(ws)
                            if fn in fn_attachments.keys():
                                attachments[wsid] = fn_attachments[fn]
                            else:
                                attachments[wsid] = self.create_attachment(
                                    ws, infile)

                    if capturedate:
                        values["DateTime"] = capturedate

                    processed = self._process_analysis(sid, analysis, values)
                    if processed:
                        updated_analyses.append(analysis)
                        ancount += 1

                        if refsample and self.instrument:
                            inst = self.instrument
                            # Calibration Test (import to Instrument)
                            importedinst = inst.title in importedinsts.keys() \
                                and importedinsts[inst.title] or []
                            if keyword not in importedinst:
                                importedinst.append(keyword)
                            importedinsts[inst.title] = importedinst
                        else:
                            ar = analysis.portal_type == "Analysis" \
                                and analysis.aq_parent or None
                            if ar and ar.UID:
                                importedar = ar.getId() in importedars.keys() \
                                            and importedars[ar.getId()] or []
                                if keyword not in importedar:
                                    importedar.append(keyword)
                                importedars[ar.getId()] = importedar

                        if ws:
                            # attach import file
                            self.attach_attachment(
                                analysis, attachments[ws.getId()])

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
            self.log(_("${request_id}: ${keywords} imported sucessfully",
                       mapping={"request_id": arid, "keywords": acodesmsg}))

        for instid, acodes in six.iteritems(importedinsts):
            acodesmsg = "Analysis %s" % ', '.join(acodes)
            msg = "%s: %s %s" % (instid, acodesmsg, "imported sucessfully")
            self.log(msg)

        if refsample and self.instrument:
            self.log(_("Import finished successfully: ${updated_ars} Samples, "
                       "${updated_instruments} Instruments and "
                       "${updated_results} results updated",
                       mapping={"updated_ars": str(len(importedars)),
                                "updated_instruments": str(len(importedinsts)),
                                "updated_results": str(ancount)}))
        else:
            self.log(_("Import finished successfully: ${updated_ars} Samples "
                       "and ${updated_results} results updated",
                       mapping={"updated_ars": str(len(importedars)),
                                "updated_results": str(ancount)}))

    def _process_analysis(self, objid, analysis, values):
        """Process a single analysis result
        """
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
            resultsaved = analysis.calculateResult(override=self.override[0])

        # Set result if present.
        res = values.get(defresultkey, '')
        calc = analysis.getCalculation()

        # don't set results on calculated analyses
        if not calc:
            if api.is_floatable(res) or self.override[1]:
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
           and (analysis.getRemarks() != '' or self.override[1] is True):
            analysis.setRemarks(values['Remarks'])
            fields_to_reindex.append('Remarks')

        if len(fields_to_reindex):
            analysis.reindexObject(idxs=fields_to_reindex)
        return resultsaved

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
            success = obj.calculateResult(override=self.override[0])
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

    def create_mime_attachmenttype(self):
        # Create the AttachmentType for mime type if not exists
        attachmentType = self.bsc(portal_type="AttachmentType",
                                  title=self.parser.getAttachmentFileType())
        if not attachmentType:
            folder = self.context.bika_setup.bika_attachmenttypes
            obj = api.create(folder, "AttachmentType")
            obj.edit(title=self.parser.getAttachmentFileType(),
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
        if self.priorizedsearchcriteria in ['rgid', 'rid', 'ruid']:
            # Look from reference analyses
            analyses = self._getZODBAnalysesFromReferenceAnalyses(
                    objid, self.priorizedsearchcriteria)
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
            self.priorizedsearchcriteria = criteria
        return obj
