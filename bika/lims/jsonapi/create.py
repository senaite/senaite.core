from AccessControl import getSecurityManager
from AccessControl import Unauthorized
from bika.lims.idserver import renameAfterCreation
from bika.lims.jsonapi import set_fields_from_request
from bika.lims.jsonapi import resolve_request_lookup
from bika.lims.permissions import AccessJSONAPI
from bika.lims.utils import tmpID, dicts_to_dict
from bika.lims.workflow import doActionFor
from plone.jsonapi.core import router
from plone.jsonapi.core.interfaces import IRouteProvider
from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from zExceptions import BadRequest
from zope import event
from zope import interface

import json
import transaction

class Create(object):
    interface.implements(IRouteProvider)

    def initialize(self, context, request):
        self.context = context
        self.request = request

    @property
    def routes(self):
        return (
            ("/create", "create", self.create, dict(methods=['GET', 'POST'])),
        )


    def create(self, context, request):
        """/@@API/create: Create new object.

        Required parameters:

            - obj_type = portal_type of new object.
            - obj_path = path of new object, from plone site root. - Not required for
             obj_type=AnalysisRequest

        Optionally:

            - obj_id = ID of new object.

        All other parameters in the request are matched against the object's
        Schema.  If a matching field is found in the schema, then the value is
        taken from the request and sent to the field's mutator.

        Reference fields may have their target value(s) specified with a
        delimited string query syntax, containing the portal_catalog search:

            <FieldName>=index1:value1|index2:value2

        eg to set the Client of a batch:

            ...@@API/update?obj_path=<path>...
            ...&Client=title:<client_title>&...

        And, to set a multi-valued reference, these both work:

            ...@@API/update?obj_path=<path>...
            ...&InheritedObjects:list=title:AR1...
            ...&InheritedObjects:list=title:AR2...

            ...@@API/update?obj_path=<path>...
            ...&InheritedObjects[]=title:AR1...
            ...&InheritedObjects[]=title:AR2...

        The Analysis_Specification parameter is special, it mimics
        the format of the python dictionaries, and only service Keyword
        can be used to reference services.  Even if the keyword is not
        actively required, it must be supplied:

            <service_keyword>:min:max:error tolerance

        The function returns a dictionary as a json string:

        {
            runtime: Function running time.
            error: true or string(message) if error. false if no error.
            success: true or string(message) if success. false if no success.
        }

        >>> portal = layer['portal']
        >>> portal_url = portal.absolute_url()
        >>> from plone.app.testing import SITE_OWNER_NAME
        >>> from plone.app.testing import SITE_OWNER_PASSWORD

        Simple AR creation, no obj_path parameter is required:

        >>> browser = layer['getBrowser'](portal, loggedIn=True, username=SITE_OWNER_NAME, password=SITE_OWNER_PASSWORD)
        >>> browser.open(portal_url+"/@@API/create", "&".join([
        ... "obj_type=AnalysisRequest",
        ... "Client=portal_type:Client|id:client-1",
        ... "SampleType=portal_type:SampleType|title:Apple Pulp",
        ... "Contact=portal_type:Contact|getFullname:Rita Mohale",
        ... "Services:list=portal_type:AnalysisService|title:Calcium",
        ... "Services:list=portal_type:AnalysisService|title:Copper",
        ... "Services:list=portal_type:AnalysisService|title:Magnesium",
        ... "SamplingDate=2013-09-29",
        ... "Specification=portal_type:AnalysisSpec|title:Apple Pulp",
        ... ]))
        >>> browser.contents
        '{..."success": true...}'

        If some parameters are specified and are not located as existing fields or properties
        of the created instance, the create should fail:

        >>> browser = layer['getBrowser'](portal, loggedIn=True, username=SITE_OWNER_NAME, password=SITE_OWNER_PASSWORD)
        >>> browser.open(portal_url+"/@@API/create?", "&".join([
        ... "obj_type=Batch",
        ... "obj_path=/batches",
        ... "title=Test",
        ... "Thing=Fish"
        ... ]))
        >>> browser.contents
        '{...The following request fields were not used: ...Thing...}'

        Now we test that the AR create also fails if some fields are spelled wrong

        >>> browser = layer['getBrowser'](portal, loggedIn=True, username=SITE_OWNER_NAME, password=SITE_OWNER_PASSWORD)
        >>> browser.open(portal_url+"/@@API/create", "&".join([
        ... "obj_type=AnalysisRequest",
        ... "thing=Fish",
        ... "Client=portal_type:Client|id:client-1",
        ... "SampleType=portal_type:SampleType|title:Apple Pulp",
        ... "Contact=portal_type:Contact|getFullname:Rita Mohale",
        ... "Services:list=portal_type:AnalysisService|title:Calcium",
        ... "Services:list=portal_type:AnalysisService|title:Copper",
        ... "Services:list=portal_type:AnalysisService|title:Magnesium",
        ... "SamplingDate=2013-09-29"
        ... ]))
        >>> browser.contents
        '{...The following request fields were not used: ...thing...}'

        """
        savepoint = transaction.savepoint()
        self.context = context
        self.request = request
        self.unused = [x for x in self.request.form.keys()]
        self.used("form.submitted")
        self.used("__ac_name")
        self.used("__ac_password")
        # always require obj_type
        self.require("obj_type")
        obj_type = self.request['obj_type']
        self.used("obj_type")
        # AnalysisRequest shortcut: creates Sample, Partition, AR, Analyses.
        if obj_type == "AnalysisRequest":
            try:
                return self._create_ar(context, request)
            except:
                savepoint.rollback()
                raise
        # Other object types require explicit path as their parent
        self.require("obj_path")
        obj_path = self.request['obj_path']
        if not obj_path.startswith("/"):
            obj_path = "/" + obj_path
        self.used("obj_path")
        site_path = request['PATH_INFO'].replace("/@@API/create", "")
        parent = context.restrictedTraverse(str(site_path + obj_path))
        # normal permissions still apply for this user
        if not getSecurityManager().checkPermission(AccessJSONAPI, parent):
            msg = "You don't have the '{0}' permission on {1}".format(
                AccessJSONAPI, parent.absolute_url())
            raise Unauthorized(msg)

        obj_id = request.get("obj_id", "")
        _renameAfterCreation = False
        if not obj_id:
            _renameAfterCreation = True
            obj_id = tmpID()
        self.used(obj_id)

        ret = {
            "url": router.url_for("create", force_external=True),
            "success": True,
            "error": False,
        }

        try:
            obj = _createObjectByType(obj_type, parent, obj_id)
            obj.unmarkCreationFlag()
            if _renameAfterCreation:
                renameAfterCreation(obj)
            ret['obj_id'] = obj.getId()
            used_fields = set_fields_from_request(obj, request)
            for field in used_fields:
                self.used(field)
            obj.reindexObject()
            obj.aq_parent.reindexObject()
            event.notify(ObjectInitializedEvent(obj))
            obj.at_post_create_script()
        except:
            savepoint.rollback()
            raise

        if self.unused:
            raise BadRequest("The following request fields were not used: %s.  Request aborted." % self.unused)

        return ret

    def get_specs_from_request(self, dicts_to_dict_rr=None):
        """Specifications for analyses are given on the request in *Spec

        >>> portal = layer['portal']
        >>> portal_url = portal.absolute_url()
        >>> from plone.app.testing import SITE_OWNER_NAME
        >>> from plone.app.testing import SITE_OWNER_PASSWORD

        >>> browser = layer['getBrowser'](portal, loggedIn=True, username=SITE_OWNER_NAME, password=SITE_OWNER_PASSWORD)
        >>> browser.open(portal_url+"/@@API/create", "&".join([
        ... "obj_type=AnalysisRequest",
        ... "Client=portal_type:Client|id:client-1",
        ... "SampleType=portal_type:SampleType|title:Apple Pulp",
        ... "Contact=portal_type:Contact|getFullname:Rita Mohale",
        ... "Services:list=portal_type:AnalysisService|title:Calcium",
        ... "Services:list=portal_type:AnalysisService|title:Copper",
        ... "Services:list=portal_type:AnalysisService|title:Magnesium",
        ... "SamplingDate=2013-09-29",
        ... "Specification=portal_type:AnalysisSpec|title:Apple Pulp",
        ... 'ResultsRange=[{"keyword":"Cu","min":5,"max":10,"error":10},{"keyword":"Mg","min":6,"max":11,"error":11}]',
        ... ]))
        >>> browser.contents
        '{..."success": true...}'

        """

        # valid output for ResultsRange goes here.
        specs = []

        context = self.context
        request = self.request
        brains = resolve_request_lookup(context, request, "Specification")
        spec_rr = brains[0].getObject().getResultsRange() if brains else {}
        spec_rr = dicts_to_dict(spec_rr, 'keyword')
        #
        bsc = getToolByName(context, "bika_setup_catalog")
        req_rr = request.get('ResultsRange', "[]")
        try:
            req_rr = json.loads(req_rr)
        except:
            raise BadRequest("Invalid value for ResultsRange (%s)"%req_rr)
        req_rr = dicts_to_dict(req_rr, 'keyword')
        #
        spec_rr.update(req_rr)

        return spec_rr.values()

    def require(self, fieldname, allow_blank=False):
        """fieldname is required"""
        if self.request.form and fieldname not in self.request.form.keys():
            raise Exception("Required field not found in request: %s" % fieldname)
        if self.request.form and (not self.request.form[fieldname] or allow_blank):
            raise Exception("Required field %s may not have blank value")

    def used(self, fieldname):
        """fieldname is used, remove from list of unused fields"""
        if fieldname in self.unused:
            self.unused.remove(fieldname)

    def _create_ar(self, context, request):
        """Creates AnalysisRequest object, with supporting Sample, Partition
        and Analysis objects.  The client is retrieved from the obj_path
        key in the request.

        Required request parameters:

            - Contact: One client contact Fullname.  The contact must exist
              in the specified client.  The first Contact with the specified
              value in it's Fullname field will be used.

            - SampleType_<index> - Must be an existing sample type.

        Optional request parameters:

        - CCContacts: A list of contact Fullnames, which will be copied on
          all messages related to this AR and it's sample or results.

        - CCEmails: A list of email addresses to include as above.

        - Sample_id: Create a secondary AR with an existing sample.  If
          unspecified, a new sample is created.

        - Specification: a lookup to set Analysis specs default values
          for all analyses

        - Analysis_Specification: specs (or overrides) per analysis, using
          a special lookup format.

            &Analysis_Specification:list=<Keyword>:min:max:error&...


        """

        wftool = getToolByName(context, 'portal_workflow')
        bc = getToolByName(context, 'bika_catalog')
        bsc = getToolByName(context, 'bika_setup_catalog')
        pc = getToolByName(context, 'portal_catalog')
        ret = {
            "url": router.url_for("create", force_external=True),
            "success": True,
            "error": False,
        }
        SamplingWorkflowEnabled = context.bika_setup.getSamplingWorkflowEnabled()
        for field in [
            'Client',
            'SampleType',
            'Contact',
            'SamplingDate',
            'Services']:
            self.require(field)
            self.used(field)

        try:
            client = resolve_request_lookup(context, request, 'Client')[0].getObject()
        except IndexError:
            raise Exception("Client not found")

        # Sample_id
        if 'Sample' in request:
            try:
                sample = resolve_request_lookup(context, request, 'Sample')[0].getObject()
            except IndexError:
                raise Exception("Sample not found")
        else:
            # Primary AR
            sample = _createObjectByType("Sample", client, tmpID())
            sample.unmarkCreationFlag()
            fields = set_fields_from_request(sample, request)
            for field in fields:
                self.used(field)
            sample._renameAfterCreation()
            sample.setSampleID(sample.getId())
            event.notify(ObjectInitializedEvent(sample))
            sample.at_post_create_script()

            if SamplingWorkflowEnabled:
                wftool.doActionFor(sample, 'sampling_workflow')
            else:
                wftool.doActionFor(sample, 'no_sampling_workflow')

        ret['sample_id'] = sample.getId()

        parts = [{'services': [],
                  'container': [],
                  'preservation': '',
                  'separate': False}]

        specs = self.get_specs_from_request()
        ar = _createObjectByType("AnalysisRequest", client, tmpID())
        ar.unmarkCreationFlag()
        fields = set_fields_from_request(ar, request)
        for field in fields:
            self.used(field)
        ar.setSample(sample.UID())
        ar._renameAfterCreation()
        ret['ar_id'] = ar.getId()
        brains = resolve_request_lookup(context, request, 'Services')
        service_uids = [p.UID for p in brains]
        new_analyses = ar.setAnalyses(service_uids, specs=specs)
        ar.setRequestID(ar.getId())
        ar.reindexObject()
        event.notify(ObjectInitializedEvent(ar))
        ar.at_post_create_script()

        # Create sample partitions
        parts_and_services = {}
        for _i in range(len(parts)):
            p = parts[_i]
            part_prefix = sample.getId() + "-P"
            if '%s%s' % (part_prefix, _i + 1) in sample.objectIds():
                parts[_i]['object'] = sample['%s%s' % (part_prefix, _i + 1)]
                parts_and_services['%s%s' % (part_prefix, _i + 1)] = p['services']
                part = parts[_i]['object']
            else:
                part = _createObjectByType("SamplePartition", sample, tmpID())
                parts[_i]['object'] = part
                container = None
                preservation = p['preservation']
                parts[_i]['prepreserved'] = False
                part.edit(
                    Container=container,
                    Preservation=preservation,
                )
                part.processForm()
                if SamplingWorkflowEnabled:
                    wftool.doActionFor(part, 'sampling_workflow')
                else:
                    wftool.doActionFor(part, 'no_sampling_workflow')
                parts_and_services[part.id] = p['services']

        if SamplingWorkflowEnabled:
            wftool.doActionFor(ar, 'sampling_workflow')
        else:
            wftool.doActionFor(ar, 'no_sampling_workflow')

        # Add analyses to sample partitions
        # XXX jsonapi create AR: right now, all new analyses are linked to the first samplepartition
        if new_analyses:
            analyses = list(part.getAnalyses())
            analyses.extend(new_analyses)
            part.edit(
                Analyses=analyses,
            )
            for analysis in new_analyses:
                analysis.setSamplePartition(part)

        # If Preservation is required for some partitions,
        # and the SamplingWorkflow is disabled, we need
        # to transition to to_be_preserved manually.
        if not SamplingWorkflowEnabled:
            to_be_preserved = []
            sample_due = []
            lowest_state = 'sample_due'
            for p in sample.objectValues('SamplePartition'):
                if p.getPreservation():
                    lowest_state = 'to_be_preserved'
                    to_be_preserved.append(p)
                else:
                    sample_due.append(p)
            for p in to_be_preserved:
                doActionFor(p, 'to_be_preserved')
            for p in sample_due:
                doActionFor(p, 'sample_due')
            doActionFor(sample, lowest_state)
            for analysis in ar.objectValues('Analysis'):
                doActionFor(analysis, lowest_state)
            doActionFor(ar, lowest_state)

        # receive secondary AR
        if request.get('Sample_id', ''):
            doActionFor(ar, 'sampled')
            doActionFor(ar, 'sample_due')
            not_receive = ['to_be_sampled', 'sample_due', 'sampled',
                           'to_be_preserved']
            sample_state = wftool.getInfoFor(sample, 'review_state')
            if sample_state not in not_receive:
                doActionFor(ar, 'receive')
            for analysis in ar.getAnalyses(full_objects=1):
                doActionFor(analysis, 'sampled')
                doActionFor(analysis, 'sample_due')
                if sample_state not in not_receive:
                    doActionFor(analysis, 'receive')

        if self.unused:
            raise BadRequest("The following request fields were not used: %s.  Request aborted." % self.unused)

        return ret
