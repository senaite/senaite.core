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
from bika.lims.interfaces import IReferenceAnalysis
from bika.lims.interfaces import IRoutineAnalysis
from plone.memoize.view import memoize_contextless
from senaite.core.api import dtime
from senaite.core.catalog import ANALYSIS_CATALOG
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.catalog import SENAITE_CATALOG
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.exportimport.instruments.logger import Logger
from senaite.core.i18n import translate as t
from zope.cachedescriptors.property import Lazy as lazy_property
from zope.deprecation import deprecate

ALLOWED_SAMPLE_STATES = ["sample_received", "to_be_verified"]
ALLOWED_ANALYSIS_STATES = ["unassigned", "assigned", "to_be_verified"]
DEFAULT_RESULT_KEY = "DefaultResult"
EMPTY_MARKER = object()


class AnalysisResultsImporter(Logger):
    """Results importer
    """
    def __init__(self, parser, context,
                 override=None,
                 allowed_sample_states=None,
                 allowed_analysis_states=None,
                 instrument_uid=None):
        super(AnalysisResultsImporter, self).__init__()

        self.context = context

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
        # Search Indexes for Sample IDs
        self.searchcriteria = ["getId", "getClientSampleID"]

        # BBB
        self._parser = parser
        self.allowed_ar_states = self.allowed_sample_states
        self._allowed_analysis_states = self.allowed_analysis_states
        self._override = self.override
        self._idsearch = ["getId", "getClientSampleID"]
        self._priorizedsearchcriteria = self.priorizedsearchcriteria

    @property
    @deprecate("Please use self.wf_tool instead")
    def wf(self):
        # BBB
        return self.wf_tool

    @property
    @deprecate("Please use self.sample_catalog instead")
    def ar_catalog(self):
        # BBB
        return self.sample_catalog

    @property
    @deprecate("Please use self.analysis_catalog instead")
    def bac(self):
        # BBB
        return self.analysis_catalog

    @property
    @deprecate("Please use self.senaite_catalog instead")
    def bc(self):
        # BBB
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

    @lazy_property
    def bika_setup(self):
        """Get the bika setup object
        """
        return api.get_bika_setup()

    @lazy_property
    def setup(self):
        """Get the Senaite setup object
        """
        return api.get_senaite_setup()

    @lazy_property
    def attachment_types(self):
        """Get the senaite setup object
        """
        return self.setup.attachmenttypes

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

    @property
    def parser(self):
        """Returns the parser that is used for the import
        """
        # Maybe we can use an adapter lookup here?
        return self._parser

    @parser.setter
    def parser(self, value):
        self._parser = value

    @deprecate("Please use self.parser instead")
    def getParser(self):
        return self.parser

    def get_automatic_importer(self, instrument, parser, **kw):
        """Return the automatic importer
        """
        raise NotImplementedError("Must be provided by Adapter Implementation")

    def get_automatic_parser(self, infile, **kw):
        """Return the automatic parser
        """
        raise NotImplementedError("Must be provided by Adapter Implementation")

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

    @property
    def override_non_empty(self):
        """Returns if the value can be written
        """
        return self.override[0] is True

    @property
    def override_with_empty(self):
        """Returns if the value can be written
        """
        return self.override[1] is True

    def can_override_analysis_result(self, analysis, result):
        """Checks if the result can be overwritten or not

        :returns: True if exisiting results can be overwritten
        """
        analysis_result = analysis.getResult()
        empty_result = False
        if not result:
            empty_result = len(str(result).strip()) == 0
        if analysis_result and not self.override_non_empty:
            return False
        elif empty_result and not self.override_with_empty:
            return False
        return True

    def convert_analysis_result(self, analysis, result):
        """Convert the analysis result

        :returns: Converted analysis result
        """

        result_options = analysis.getResultOptions()
        result_type = analysis.getResultType()

        if result_options:
            # Handle result options as integer values
            result_values = map(
                lambda r: r.get("ResultValue"), result_options)

            # NOTE: The method `setResult` converts numeric result to a float.
            # However, result options can be set as integer or float values.
            # Even if we import the result from as an integer, e.g. `1`, the
            # result is set as `1.0`.
            if result_type == "select":
                # check if an integer result value is set in the result options
                if "{:.0f}".format(result) in result_values:
                    # convert the result to an integer value to avoid further
                    # processing in `setResult`
                    return int(result)

        return result

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

    @memoize_contextless
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

    def get_attachment_type_by_title(self, title):
        """Get an attachment type by title

        :param title: Attachment type title
        :returns: Attachment object or None
        """
        query = {
            "portal_type": "AttachmentType",
            "title": title,
            "is_active": True,
        }
        results = self.setup_catalog(query)
        if not len(results) > 0:
            return None
        return api.get_object(results[0])

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
        if not any([self.override_non_empty, self.override_with_empty]):
            self.log(_("Don't override analysis results"))
        if self.override_non_empty:
            self.log(_("Override non-empty analysis results"))
        if self.override_with_empty:
            self.log(_("Override non-empty analysis results, also with empty"))

        # Attachments will be created in any worksheet that contains
        # analyses that are updated by this import
        attachments = {}
        infile = self.parser.getInputFile()

        ancount = 0
        updated_analyses = []
        importedinsts = {}
        importedars = {}

        for sid, results in parsed_results.items():
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
                    self.warn(_("No Sample found for ${sid}",
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
                self.warn(_("No analyses found for ${sid} "
                            "in the states '${allowed_sample_states}' ",
                            mapping={
                                "allowed_sample_states": ", ".join(
                                    self.allowed_sample_states_msg),
                                "sid": sid,
                            }))
                continue

            # import the results
            for result in results:

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

                    # Process the analysis
                    processed = self.process_analysis(sid, analysis, values)

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

    @deprecate("Please use self.process_analysis instead")
    def _process_analysis(self, sid, analysis, values):
        return self.process_analysis(sid, analysis, values)

    def process_analysis(self, sid, analysis, values):
        """Process a single analysis result

        :param sid: Sample ID
        :param analysis: Analysis object
        :param values: Dictionary of values, including the result to set
        :returns: True if the interims has been set
        """

        # set the analysis interim fields
        interims_updated = self.set_analysis_interims(sid, analysis, values)

        # set the analysis result
        result_updated = self.set_analysis_result(sid, analysis, values)

        # set additional field values
        fields_updated = self.set_analysis_fields(sid, analysis, values)

        # Nothing updated
        if not any([result_updated, interims_updated, fields_updated]):
            return False

        # submit the result
        self.save_submit_analysis(analysis)
        analysis.reindexObject()

        return True

    def set_analysis_interims(self, sid, analysis, values):
        """Set the analysis interim fields

        :param sid: Sample ID
        :param analysis: Analysis object
        :param values: Dictionary of values, including the result to set
        :returns: True if the interims were written
        """
        updated = False
        keys = values.keys()
        interims = self.get_interim_fields(analysis)
        interims_out = []

        for interim in interims:
            value = EMPTY_MARKER
            keyword = interim.get("keyword")
            title = interim.get("title")
            interim_copy = interim.copy()
            # Check if we have an interim value set
            if keyword in keys:
                value = values.get(keyword)
            elif title in keys:
                value = values.get(title)
            if value is not EMPTY_MARKER:
                # set the value
                interim_copy["value"] = value
                updated = True
                # TODO: change test not to rely on this logline!
                self.log(_("${sid} result for '${analysis_keyword}:"
                           "${interim_keyword}': '${value}'",
                         mapping={
                             "sid": sid,
                             "analysis_keyword": analysis.getKeyword(),
                             "interim_keyword": keyword,
                             "value": str(value),
                         }))
            interims_out.append(interim_copy)

        # write back interims
        if len(interims_out) > 0:
            analysis.setInterimFields(interims_out)
            analysis.calculateResult(override=self.override[0])

        return updated

    def set_analysis_result(self, sid, analysis, values):
        """Set the analysis result field

        Results can be only set for Analyses with no calculation assigned.

        If the Analysis has already a result, it is only overridden
        when the right override option is set.

        :param sid: Sample ID
        :param analysis: Analysis object
        :param values: Dictionary of values, including the result to set
        :returns: True if the result was written
        """
        keyword = analysis.getKeyword()
        result_key = values.get(DEFAULT_RESULT_KEY, "")
        result = values.get(result_key, "")
        calculation = analysis.getCalculation()

        # check if analysis has a calculation set
        if calculation:
            self.log(_("Skipping result for analysis '${keyword}' of sample "
                       "'${sid}' with calculation '${calculation}'",
                       mapping={
                           "keyword": keyword,
                           "sid": sid,
                           "calculation": calculation.Title(),
                       }))
            return False

        # check if non-empty result can be overwritten
        if not self.can_override_analysis_result(analysis, result):
            self.log(_("Analysis '${keyword}' of sample '${sid}' has the "
                       "result '${result}' set, which is kept due to the "
                       "selected override option",
                       mapping={
                           "sid": sid,
                           "result": result,
                           "keyword": keyword,
                       }))
            return False

        # convert result for result options
        result = self.convert_analysis_result(analysis, result)

        # convert capture date if set
        date_captured = values.get("DateTime")
        if date_captured:
            date_captured = dtime.to_DT(date_captured)

        # set the analysis result
        analysis.setResult(result)

        # set the result capture date
        if date_captured:
            analysis.setResultCaptureDate(date_captured)

        self.log(_("${sid} result for '${keyword}': '${result}'",
                   mapping={
                       "sid": sid,
                       "keyword": keyword,
                       "result": result,
                   }))

        return True

    def set_analysis_fields(self, sid, analysis, values):
        """Set additional analysis fields

        This allows to set additional analysis fields like
        Remarks, Uncertainty LDL/UDL etc.

        :param sid: Sample ID
        :param analysis: Analysis object
        :param values: Dictionary of values, including the result to set
        :returns: True if the result was written
        """
        updated = False

        fields = api.get_fields(analysis)
        interim_fields = self.get_interim_fields(analysis)

        for key, value in values.items():
            if key not in fields:
                # skip nonexisting fields
                continue
            elif key == "Result":
                # skip the result field
                continue
            elif key in interim_fields:
                # skip the interim fields
                continue

            field = fields.get(key)
            field_value = field.get(analysis)

            if field_value and not self.override_non_empty:
                # skip fields with existing values
                continue

            # set the new field value, preferrably with the setter
            setter = "set{}".format(field.getName().capitalize())
            mutator = getattr(analysis, setter, None)
            if mutator:
                # we have a setter
                mutator(value)
            else:
                # set with the field's set method
                field.set(analysis, value)

            updated = True
            self.log(_("${sid} Updated field '${field}' with '${value}'",
                       mapping={
                           "sid": sid,
                           "field": key,
                           "value": value,
                       }))

        return updated

    def save_submit_analysis(self, analysis):
        """Submit analysis and ignore errors
        """
        try:
            api.do_transition_for(analysis, "submit")
        except api.APIError:
            pass

    def get_interim_fields(self, analysis):
        """Return the interim fields of the analysis
        """
        interim_fields = getattr(analysis, "getInterimFields", None)
        if not callable(interim_fields):
            return []
        return interim_fields()

    def calculateTotalResults(self, objid, analysis):
        """ If an AR(objid) has an analysis that has a calculation
        then check if param analysis is used on the calculations formula.
        Here we are dealing with two types of analysis.
        1. Calculated Analysis - Results are calculated.
        2. Analysis - Results are captured and not calculated
        :param objid: AR ID or Worksheet's Reference Sample IDs
        :param analysis: Analysis Object
        """
        for obj in self.get_analyses_for(objid):
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

    def create_attachment(self, ws, infile):
        """Create a new attachment in the attachment

        :param ws: Worksheet
        :param infile: upload file wrapper
        :returns: Attachment object
        """
        if not infile:
            return None

        att_type = self.create_mime_attachmenttype()
        filename = infile.filename

        attachment = api.create(ws, "Attachment")
        attachment.edit(
            title=filename,
            AttachmentFile=infile,
            AttachmentType=api.get_uid(att_type),
            AttachmentKeys="Results, Automatic import",
            RenderInReport=False,
        )
        attachment.reindexObject()

        logger.info(_(
            "Attached file '%{filename}' to worksheet ${worksheet}",
            mapping={
                "filename": filename,
                "worksheet": ws.getId(),
            }))

        return attachment

    def create_mime_attachmenttype(self):
        """Create (or get) an attachment filetype
        """
        file_type = self.parser.getAttachmentFileType()
        obj = self.get_attachment_type_by_title(file_type)
        if not obj:
            obj = api.create(self.attachment_types, "AttachmentType")
            obj.edit(title=file_type,
                     description="Auto generated")
        return obj

    def attach_attachment(self, analysis, attachment):
        """Attach a file or a given set of files to an analysis

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
                _("Attaching '${attachment}' to Analysis '${analysis}'",
                  mapping={
                      "attachment": filename,
                      "analysis": analysis.getKeyword(),
                  }))
            analysis.setAttachment([att.UID() for att in an_atts])
            analysis.reindexObject()
        else:
            self.log(_("Attachment '${attachment}' was already linked "
                       "to analysis ${analysis}",
                       mapping={
                           "attachment": filename,
                           "analysis": analysis.getKeyword(),
                       }))

    def get_attachment_filenames(self, ws):
        """Returns all attachment filenames in the given worksheet
        """
        fn_attachments = {}
        for att in ws.objectValues("Attachment"):
            fn = att.getAttachmentFile().filename
            if fn not in fn_attachments:
                fn_attachments[fn] = []
            fn_attachments[fn].append(att)
        return fn_attachments

    def is_analysis_allowed(self, analysis):
        """Filter analyses that match the import criteria
        """
        if IReferenceAnalysis.providedBy(analysis):
            return True
        # Routine Analyses must be in the allowed WF states
        status = api.get_workflow_status_of(analysis)
        if status in self.allowed_analysis_states:
            return True
        return False

    def get_analyses_for(self, sid):
        """Get analyses for the given sample ID

        Only analyses that in the allowed analyses states are returned.
        If not a ReferenceAnalysis, allowed sample states are also checked.

        :param sid: sample ID or Worksheet Reference Sample ID
        :returns: list of analyses / empty list if no alanyses were found
        """
        analyses = []

        # Acceleration of searches using priorization
        if self.priorizedsearchcriteria in ["rgid", "rid", "ruid"]:
            # Look from reference analyses
            analyses = self._getZODBAnalysesFromReferenceAnalyses(
                    sid, self.priorizedsearchcriteria)

        if len(analyses) == 0:
            # Look from ar and derived
            analyses = self._getZODBAnalysesFromAR(
                sid, "", self.searchcriteria, self.allowed_sample_states)

        return list(filter(self.is_analysis_allowed, analyses))

    @deprecate("Please use self.find_objects instead")
    def _getObjects(self, oid, criteria, states):
        return self.find_objects(oid, criteria, states)

    def find_objects(self, oid, criteria, states):
        """Find objects

        :param oid: Primary search ID
        """
        results = []

        if criteria in ["arid"]:
            query = {"getId": oid, "review_state": states}
            results = self.sample_catalog(query)
        elif criteria == "csid":
            query = {"getClientSampleID": oid, "review_state": states}
            results = self.sample_catalog(query)
        elif criteria == "aruid":
            query = {"UID": oid, "review_state": states}
            results = self.sample_catalog(query)
        elif criteria == "rgid":
            query = {
                "portal_type": ["ReferenceAnalysis", "DuplicateAnalysis"],
                "getReferenceAnalysesGroupID": oid,
            }
            results = self.analysis_catalog(query)
        elif criteria == "rid":
            query = {
                "portal_type": ["ReferenceAnalysis", "DuplicateAnalysis"],
                "getId": oid,
            }
            results = self.analysis_catalog(query)
        elif criteria == "ruid":
            query = {
                "portal_type": ["ReferenceAnalysis", "DuplicateAnalysis"],
                "UID": oid,
            }
            results = self.analysis_catalog(query)

        if len(results) > 0:
            self.priorizedsearchcriteria = criteria

        return results

    @deprecate("Please use self.get_analyses_for instead")
    def _getZODBAnalyses(self, sid):
        return self.get_analyses_for(sid)

    def _getZODBAnalysesFromAR(self, objid, criteria,
                               allowedsearches, arstates):
        ars = []
        analyses = []
        if criteria:
            ars = self.find_objects(objid, criteria, arstates)
            if not ars or len(ars) == 0:
                return self._getZODBAnalysesFromAR(objid, None,
                                                   allowedsearches, arstates)
        else:
            sortorder = ["arid", "csid", "aruid"]
            for crit in sortorder:
                if (crit == "arid" and "getId" in allowedsearches) \
                    or (crit == "csid" and "getClientSampleID"
                                in allowedsearches) \
                        or (crit == "aruid" and "getId" in allowedsearches):
                    ars = self.find_objects(objid, crit, arstates)
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
            refans = self.find_objects(objid, criteria, [])
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
