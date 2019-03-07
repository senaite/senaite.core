Analysis Request sample guard and event
=======================================

Running this test from the buildout directory:

    bin/test test_textual_doctests -t WorkflowAnalysisRequestSample

Test Setup
----------

Needed Imports:

    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from bika.lims.workflow import isTransitionAllowed
    >>> from bika.lims.workflow import getAllowedTransitions
    >>> from DateTime import DateTime
    >>> from plone import api as ploneapi
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD

Functional Helpers:

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

    >>> def timestamp(format="%Y-%m-%d"):
    ...     return DateTime().strftime(format)

    >>> def try_transition(object, transition_id, target_state_id):
    ...      success = do_action_for(object, transition_id)[0]
    ...      state = api.get_workflow_status_of(object)
    ...      return success and state == target_state_id

    >>> def new_ar(services, ar_template=None):
    ...     values = {
    ...         'Client': client.UID(),
    ...         'Contact': contact.UID(),
    ...         'SampleType': sampletype.UID(),
    ...         'Template': ar_template,
    ...     }
    ...     date_key = "DateSampled"
    ...     if ar_template and ar_template.getSamplingRequired():
    ...         date_key = "SamplingDate"
    ...     elif bikasetup.getSamplingWorkflowEnabled():
    ...         date_key = "SamplingDate"
    ...     values[date_key] = timestamp()
    ...     service_uids = map(api.get_uid, services)
    ...     ar = create_analysisrequest(client, request, values, service_uids)
    ...     return ar

    >>> def get_roles_for_permission(permission, context):
    ...     allowed = set(rolesForPermissionOn(permission, context))
    ...     return sorted(allowed)

    >>> def roles_for_transition_check(transition_id, roles, object):
    ...     granted = list()
    ...     ungranted = list()
    ...     for role in roles:
    ...         setRoles(portal, TEST_USER_ID, [role])
    ...         if isTransitionAllowed(object, transition_id):
    ...             granted.append(role)
    ...         else:
    ...             ungranted.append(role)
    ...     setRoles(portal, TEST_USER_ID, ['LabManager',])
    ...     return granted, ungranted

    >>> def are_roles_for_transition_granted(transition_id, roles, object):
    ...     gr, ungr = roles_for_transition_check(transition_id, roles, object)
    ...     return len(ungr) == 0 and len(gr) > 0

    >>> def are_roles_for_transition_ungranted(transition_id, roles, object):
    ...     gr, ungr = roles_for_transition_check(transition_id, roles, object)
    ...     return len(gr) == 0 and len(ungr) > 0

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> bikasetup = portal.bika_setup
    >>> date_now = timestamp()

We need to create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(bikasetup.bika_sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(bikasetup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(bikasetup.bika_departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(bikasetup.bika_analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> Cu = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category.UID(), Accredited=True)
    >>> Fe = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Price="10", Category=category.UID())
    >>> Au = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Gold", Keyword="Au", Price="20", Category=category.UID())
    >>> ar_template = api.create(bikasetup.bika_artemplates, "ARTemplate", title="Test Template", SampleType=sampletype)
    >>> sampler_user = ploneapi.user.create(email="sampler1@example.com", username="sampler1", password="secret", properties=dict(fullname="Sampler 1"))
    >>> setRoles(portal, "sampler1", ['Authenticated', 'Member', 'Sampler'])


Sample transition and guard basic constraints
---------------------------------------------

Create an Analysis Request:

    >>> ar = new_ar([Cu])

By default, the Analysis Request transitions to "sample_due" status:

    >>> api.get_workflow_status_of(ar)
    'sample_due'

And from this status, the transition "sample" is not possible:

    >>> isTransitionAllowed(ar, "sample")
    False

If the value for setup setting "SamplingWorkflowEnabled" is True, the status
of the Analysis Request once created is "to_be_sampled":

    >>> bikasetup.setSamplingWorkflowEnabled(True)
    >>> ar = new_ar([Cu])
    >>> api.get_workflow_status_of(ar)
    'to_be_sampled'

But the transition is still not possible:

    >>> isTransitionAllowed(ar, "sample")
    False

Because we haven't set neither a Sampler nor the date the sample was collected:

    >>> date_sampled = timestamp()
    >>> ar.setDateSampled(date_sampled)
    >>> isTransitionAllowed(ar, "sample")
    False
    >>> ar.setSampler(sampler_user.id)
    >>> isTransitionAllowed(ar, "sample")
    True

When "sample" transition is performed, the status becomes "sample_due":

    >>> success = do_action_for(ar, "sample")
    >>> api.get_workflow_status_of(ar)
    'sample_due'

And the values for DateSampled and Sampler are kept:

    >>> ar.getSampler() == sampler_user.id
    True
    >>> ar.getDateSampled().strftime("%Y-%m-%d") == date_sampled
    True


Check permissions for sample transition
---------------------------------------

Declare the roles allowed and not allowed to perform the "sample" transition:

    >>> all_roles = portal.acl_users.portal_role_manager.validRoles()
    >>> allowed = ["LabManager", "Manager", "Sampler", "SamplingCoordinator"]
    >>> not_allowed = filter(lambda role: role not in allowed, all_roles)

Create an Analysis Request by using a template with Sampling workflow enabled:

    >>> bikasetup.setSamplingWorkflowEnabled(False)
    >>> ar_template.setSamplingRequired(True)
    >>> ar = new_ar([Cu], ar_template)
    >>> ar.setDateSampled(timestamp())
    >>> ar.setSampler(sampler_user.id)

Exactly these roles can Sample:

    >>> get_roles_for_permission("senaite.core: Transition: Sample Sample", ar)
    ['LabManager', 'Manager', 'Sampler', 'SamplingCoordinator']

Current user can sample because has the `LabManager` role:

    >>> isTransitionAllowed(ar, "sample")
    True

The user can sample if has any of the granted roles:

    >>> are_roles_for_transition_granted("sample", allowed, ar)
    True

But not if the user has the rest of the roles:

    >>> are_roles_for_transition_ungranted("sample", not_allowed, ar)
    True

Reset the roles for current user:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
