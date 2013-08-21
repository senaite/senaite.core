from AccessControl import getSecurityManager
from AccessControl import Unauthorized
from bika.lims.permissions import AccessJSONAPI
from bika.lims.utils import tmpID
from bika.lims.workflow import doActionFor
from plone.jsonapi import router
from plone.jsonapi.interfaces import IRouteProvider
from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFCore.utils import getToolByName
from zope import event
from zope import interface


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
        object found will be sent to the mutator.

        """
        ret = {}
        schema = obj.Schema()
        fieldnames = [f for f in request.keys() if f in schema]
        for fieldname in fieldnames:
            brains = []
            if fieldname.split("_", 1)[-1] in ("id", "Title", "UID"):
                field, index = fieldname.split("_", 1)
                uc = getToolByName(obj, "uid_catalog")
                brains = uc({index: request[fieldname]})
                if not brains:
                    raise ValueError("Object lookup failed: {0}.{1}".format(
                            obj, fieldname))
            value = brains[0].getObject() if brains else request[fieldname]
            field = schema[fieldname]
            mutator = field.getMutator(obj)
            if mutator and callable(mutator):
                mutator(value)
            accessor = field.getAccessor(obj)
            if accessor and callable(accessor):
                ret[fieldname] = accessor()
        return ret

    def _create_ar(self, context, request, client):
        """Creates AnalysisRequest object, with supporting Sample, Partition
        and Analysis objects.  The client is retrieved from the obj_path
        key in the request.

        Required request parameters:

            - Contact: One client contact Fullname.  The contact must exist
              in the specified client.  The first Contact with the specified
              value in it's Fullname field will be used.

            - SampleType_id - Must be an ID of an existing sample type.

        Optional request parameters:

        - CCContacts: A list of contact Fullnames, which will be copied on
          all messages related to this AR and it's sample or results.

        - CCEmails: A list of email addresses to include as above.

        - Sample_id: Create a secondary AR with an existing sample.  If
          unspecified, a new sample is created.

        """
        wftool = getToolByName(context, 'portal_workflow')
        bc = getToolByName(context, 'bika_catalog')
        ret = {
            "url": router.url_for("create", force_external=True),
            "success": True
        }
        SamplingWorkflowEnabled = \
            context.bika_setup.getSamplingWorkflowEnabled()
        values = {}
        values['Contact'] = request.get('Contact', '')
        values['CCContacts'] = [x.strip() for x in
                                request.get('cc_uids', '').split(",")]
        values['CCEmails'] = [x.strip() for x in
                              request.get('CCEmails', '').split(",")]
        values['Sample_id'] = request.get('Sample_id', '')

        if values['Sample_id']:
            # Secondary AR on existing sample
            sample = bc(id=values['Sample_id'])[0].getObject()
        else:
            # Primary AR, create new sample.
            _id = client.invokeFactory('Sample', id=tmpID())
            sample = client[_id]
            sample.unmarkCreationFlag()
            ret.update(self.set_fields_from_request(sample, request))
            sample.setSampleID(sample.getId())
            sample._renameAfterCreation()
            event.notify(ObjectInitializedEvent(self))
            self.at_post_create_script()

            if SamplingWorkflowEnabled:
                wftool.doActionFor(sample, 'sampling_workflow')
            else:
                wftool.doActionFor(sample, 'no_sampling_workflow')

        values['Sample'] = sample
        values['Sample_uid'] = sample.UID()
        parts = [{'services': [],
                 'container':[],
                 'preservation':'',
                 'separate':False}]

        # create the AR
        Analyses = values['Analyses']

        _id = client.invokeFactory('AnalysisRequest', tmpID())
        ar = client[_id]
        ret.update(self.set_fields_from_request(ar, request))
        ar.processForm()

        # Object has been renamed
        ar.edit(RequestID=ar.getId())
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

        new_analyses = ar.setAnalyses(Analyses)

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

        # receive secondary AR
        if values.get('Sample_uid', ''):
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
