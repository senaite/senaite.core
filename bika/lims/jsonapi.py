from AccessControl import getSecurityManager
from AccessControl import Unauthorized
from bika.lims.permissions import AccessJSONAPI
from bika.lims.utils import tmpID
from bika.lims.workflow import doActionFor
from plone.jsonapi import router
from plone.jsonapi.interfaces import IRouteProvider
from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest
from zope import event
from zope import interface

import App
import logging


class JSONAPI(object):
    interface.implements(IRouteProvider)

    def initialize(self, context, request):
        pass

    @property
    def routes(self):
        return (
            ("/create", "create", self.create, dict(methods=['GET'])),
        )

    def set_fields_from_request(self, obj, request):
        """Search request for keys that match field names in obj.

        - Calls field mutator with request value
        - Calls Accessor to retrieve value
        - Returns a dict of fields and current values

        If the field name in the request ends in any of these:

            _id
            _Titles
            _UID

        Then the corrosponding index will be used to look up the object
        from the uid_catalog.  This is for setting reference fields, and the
        UID of the object found will be sent to the mutator.

        """
        debug_mode = App.config.getConfiguration().debug_mode
        logger = logging.getLogger('bika.jsonapi')
        schema = obj.Schema()
        # fields contains all schema-valid field values from the request.
        fields = {}
        for key, value in request.items():
            if "_" in key:
                fieldname, index = key.split("_", 1)
                if fieldname not in schema:
                    continue
                pc = getToolByName(obj, "portal_catalog")
                brains = pc({index: request[key]})
                if not brains:
                    # object lookup failure need not be fatal;
                    # XXX for now we silently ignore lookup failure here,
                    continue
                value = brains[0].UID if brains else request[fieldname]
            else:
                fieldname = key
                if fieldname not in schema:
                    continue
                value = request[fieldname]
            fields[fieldname] = value
        if debug_mode:
            logger.info("Found schema fields for {0} in request: {1}".format(obj, fields))
        # write and then read each field.
        ret = {}
        for fieldname, value in fields.items():
            field = schema[fieldname]
            mutator = field.getMutator(obj)
            if mutator and callable(mutator):
                mutator(value)
            accessor = field.getAccessor(obj)
            if accessor and callable(accessor):
                val = accessor()
                if hasattr(val, 'Title') and callable(val.Title):
                    val = val.Title()
                ret[fieldname] = val
        return ret

    def _create_ar(self, context, request, client):
        """Creates AnalysisRequest object, with supporting Sample, Partition
        and Analysis objects.  The client is retrieved from the obj_path
        key in the request.

        Required request parameters:

            - Contact: One client contact Fullname.  The contact must exist
              in the specified client.  The first Contact with the specified
              value in it's Fullname field will be used.

            - SampleType_Title - Must be an existing sample type.

        Optional request parameters:

        - CCContacts: A list of contact Fullnames, which will be copied on
          all messages related to this AR and it's sample or results.

        - CCEmails: A list of email addresses to include as above.

        - Sample_id: Create a secondary AR with an existing sample.  If
          unspecified, a new sample is created.

        """

        wftool = getToolByName(context, 'portal_workflow')
        bc = getToolByName(context, 'bika_catalog')
        bsc = getToolByName(context, 'bika_setup_catalog')
        pc = getToolByName(context, 'portal_catalog')
        ret = {
            "url": router.url_for("create", force_external=True),
            "success": True
        }
        SamplingWorkflowEnabled = \
            context.bika_setup.getSamplingWorkflowEnabled()
        required_fields = ['Contact', 'SampleType_Title', 'Services']
        for field in required_fields:
            if field not in request:
                raise BadRequest("Missing field {0} in request".format(field))
        # Fields which we munge/save manually.
        try:
            contact_uid = pc(portal_type='Contact', getFullname=request.get('Contact'))[0].UID
            request['Contact'] = contact_uid
        except:
            raise BadRequest("Contact not found: getFullname="+request.get('Contact'))
        try:
            cc_contacts = [x.strip() for x in request.get('CCContacts', '').split(",")]
            cc_contact_uids = []
            for cc_contact in cc_contacts:
                cc_contact_uid = pc(portal_type='Contact', getFullname=cc_contact)[0].UID
                if cc_contact_uid not in cc_contact_uids:
                    cc_contact_uids.append(cc_contact_uid)
            request['CCContacts'] = cc_contact_uids
        except:
            raise BadRequest("CC Contact not found: getFullname="+cc_contact)
        request['CCEmails'] = [x.strip() for x in request.get('CCEmails', '').split(",")]

        service_titles = [x.strip() for x in request.get('Services', '').split(",")]
        services = []
        try:
            for service_title in service_titles:
                service = bsc({'portal_type': 'AnalysisService',
                              'title': service_title})[0].getObject()
                if service not in services:
                    services.append(service)
        except IndexError:
            raise IndexError("Service not found: {0}".format(service_title))
        service_uids = [service.UID() for service in services]

        request['Sample_id'] = request.get('Sample_id', '')
        if request['Sample_id']:
            # Secondary AR on existing sample
            sample = bc(id=request['Sample_id'])[0].getObject()
        else:
            # Primary AR, create new sample.
            _id = client.invokeFactory('Sample', id=tmpID())
            sample = client[_id]
            sample.unmarkCreationFlag()
            ret.update(self.set_fields_from_request(sample, request))
            sample._renameAfterCreation()
            sample.setSampleID(sample.getId())
            event.notify(ObjectInitializedEvent(sample))
            sample.at_post_create_script()

            if SamplingWorkflowEnabled:
                wftool.doActionFor(sample, 'sampling_workflow')
            else:
                wftool.doActionFor(sample, 'no_sampling_workflow')

        parts = [{'services': [],
                 'container':[],
                 'preservation':'',
                 'separate':False}]

        _id = client.invokeFactory('AnalysisRequest', tmpID())
        ar = client[_id]
        ar.unmarkCreationFlag()
        ret.update(self.set_fields_from_request(ar, request))
        ar.setSample(sample)
        ar._renameAfterCreation()
        new_analyses = ar.setAnalyses(service_uids)
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
            else:
                _id = sample.invokeFactory('SamplePartition', id='tmp')
                part = sample[_id]
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
        for part in sample.objectValues("SamplePartition"):
            part_services = parts_and_services[part.id]
            analyses = [a for a in new_analyses
                        if a.getServiceUID() in part_services]
            if analyses:
                part.edit(
                    Analyses=analyses,
                )
                for analysis in analyses:
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

        return ret

    def create(self, context, request):
        """/@@API/create: Create new object.

        Required parameters:

            - obj_path = path of new object, from plone site root.
            - obj_id = ID of new object.
            - obj_type = portal_type of new object.

        All other parameters in the request are matched against the object's
        Schema.  If a matching field is found in the schema, then the value is
        taken from the request and sent to the field's mutator.

        The function returns a dictionary as a json string:

        {
            runtime: Function running time.
            error: true or string(message) if error. false if no error.
            success: true or string(message) if success. false if no success.
        }

        All fields which were automatically matched in the request, and which
        were successfully completed with the request value, are also included
        in the return value, for verification.
        """

        obj_path = request.get("obj_path", "")
        if not obj_path:
            raise ValueError("bad or missing obj_path: " + obj_path)
        if not obj_path.startswith("/"):
            obj_path = "/" + obj_path
        site_path = request['PATH_INFO'].replace("/@@API/create", "")
        parent = context.restrictedTraverse(site_path + obj_path)

        if not getSecurityManager().checkPermission("AccessJSONAPI", parent):
            msg = "You don't have the '{0}' permission on {1}".format(
                AccessJSONAPI, parent.absolute_url())
            raise Unauthorized(msg)

        obj_type = request.get("obj_type", "")
        if not obj_type:
            raise ValueError("bad or missing obj_type: " + obj_type)

        if obj_type == "AnalysisRequest":
            return self._create_ar(context, request, parent)

        obj_id = request.get("obj_id", "")
        if not obj_id:
            raise ValueError("bad or missing obj_id: " + obj_id)

        if obj_type == "AnalysisRequest":
            return self._create_ar(context, request, parent, obj_id)

        parent.invokeFactory(obj_type, obj_id)
        obj = parent[obj_id].Schema()
        obj.unmarkCreationFlag()
        ret = {"url": router.url_for("create", force_external=True),
               "success": True}
        ret.update(self.set_fields_from_request(obj, request))
        return ret
