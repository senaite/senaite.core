API Security
============

The security API provides a simple interface to control access in SENAITE

Running this test from the buildout directory::

    bin/test test_textual_doctests -t API_security


Test Setup
----------

Needed Imports:

    >>> from bika.lims import api
    >>> from bika.lims.api.security import *
    >>> from bika.lims.permissions import FieldEditAnalysisHidden
    >>> from bika.lims.permissions import FieldEditAnalysisResult
    >>> from bika.lims.permissions import FieldEditAnalysisRemarks
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from DateTime import DateTime
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD

Functional Helpers:

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

		>>> def new_sample(services):
		...     values = {
		...         "Client": client.UID(),
		...         "Contact": contact.UID(),
		...         "DateSampled": date_now,
		...         "SampleType": sampletype.UID()}
		...     service_uids = map(api.get_uid, services)
		...     return create_analysisrequest(client, request, values, service_uids)

    >>> def get_analysis(sample, id):
    ...     ans = sample.getAnalyses(getId=id, full_objects=True)
    ...     if len(ans) != 1:
    ...         return None
    ...     return ans[0]


Environment Setup
-----------------

Setup the testing environment:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.bika_setup
    >>> date_now = DateTime().strftime("%Y-%m-%d")
    >>> date_future = (DateTime() + 5).strftime("%Y-%m-%d")
    >>> setRoles(portal, TEST_USER_ID, ['LabManager', ])
    >>> user = api.get_current_user()


LIMS Setup
----------

Setup the Lab for testing:

    >>> setup.setSelfVerificationEnabled(True)
    >>> analysisservices = setup.bika_analysisservices
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH")
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> labcontact = api.create(setup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.bika_departments, "Department", title="Chemistry", Manager=labcontact)
    >>> sampletype = api.create(setup.bika_sampletypes, "SampleType", title="Water", Prefix="Water")


Content Setup
-------------

Create some Analysis Services with unique Keywords:

    >>> Ca = api.create(analysisservices, "AnalysisService", title="Calcium", Keyword="Ca")
    >>> Mg = api.create(analysisservices, "AnalysisService", title="Magnesium", Keyword="Mg")
    >>> Cu = api.create(analysisservices, "AnalysisService", title="Copper", Keyword="Cu")
    >>> Fe = api.create(analysisservices, "AnalysisService", title="Iron", Keyword="Fe")
    >>> Au = api.create(analysisservices, "AnalysisService", title="Aurum", Keyword="Au")
    >>> Test1 = api.create(analysisservices, "AnalysisService", title="Calculated Test Service 1", Keyword="Test1")
    >>> Test2 = api.create(analysisservices, "AnalysisService", title="Calculated Test Service 2", Keyword="Test2")

Create an new Sample:

    >>> sample = new_sample([Cu, Fe, Au])

Get the contained `Cu` Analysis:

    >>> cu = get_analysis(sample, Cu.getKeyword())


Get a security manager for the current thread
---------------------------------------------

A security manager provides methods for checking access and managing executable
context and policies:

    >>> get_security_manager()
    <AccessControl.ImplPython.SecurityManager instance at ...>


Get the possible permissions of an object
-----------------------------------------

The possible permissions include the permissions on the object and the inherited
permissions:

    >>> possible_permissions = get_possible_permissions_for(cu)
    >>> "Modify portal content" in possible_permissions
    True


Get the mapped permissions of an object
---------------------------------------

While the possible permissions return *all* possible permissions of the object,
only few of them are mapped to the object.

The function `get_mapped_permissions_for` returns only those permissions which
have roles mapped on the given object or on objects within the acquisition
chain.

    >>> mapped_permissions = get_mapped_permissions_for(cu)

The mapped permissions are therefore a subset of the possible transitions:

    >>> set(mapped_permissions).issubset(possible_permissions)
    True


Get the granted permissions
---------------------------

This function returns the allowed permissions on an object for a user:

    >>> allowed_permissions = get_allowed_permissions_for(cu)

The allowed permissions is a subset of the mapped permissions:

    >>> set(allowed_permissions).issubset(mapped_permissions)
    True


Get the non-granted permissions
-------------------------------

This function returns the disallowed permissions on an object for a user:

    >>> disallowed_permissions = get_disallowed_permissions_for(cu)

The disallowed permissions is a subset of the mapped permissions:

    >>> set(disallowed_permissions).issubset(mapped_permissions)
    True

It is mutual exclusive to the allowed permissions:

    >>> set(disallowed_permissions).isdisjoint(allowed_permissions)
    True

The allowed and disallowed permissions are exactly the mapped permissions:

    >>> set(allowed_permissions + disallowed_permissions) == set(mapped_permissions)
    True


Check if a user has a permission granted
----------------------------------------

This function checks if the user has a permission granted on an object:

    >>> check_permission(get_allowed_permissions_for(cu)[0], cu)
    True

    >>> check_permission(get_disallowed_permissions_for(cu)[0], cu)
    False

Non existing permissions are returned as False:

    >>> check_permission("nonexisting_permission", cu)
    False


Get the granted permissions of a role
-------------------------------------

This function returns the permissions that are granted to a role:

    >>> get_permissions_for_role("Sampler", cu)
    ['senaite.core: Field: Edit Analysis Remarks', 'senaite.core: Field: Edit Analysis Result']


Get the mapped roles of a permission
------------------------------------

This function is the opposite of `get_permissions_for_role` and returns
the roles for a given permission:

    >>> get_roles_for_permission(FieldEditAnalysisResult, cu)
    ('Manager', 'Sampler')


Get the roles of a user
-----------------------

This function returns the global roles the user has:

    >>> get_roles()
    ['Authenticated', 'LabManager']

    >>> setRoles(portal, TEST_USER_ID, ['LabManager', 'Sampler', ])

    >>> get_roles()
    ['Authenticated', 'LabManager', 'Sampler']

The optional `user` parameter allows to get the roles of another user:

    >>> get_roles("admin")
    ['Authenticated', 'Manager']


Get the local roles of a user
-----------------------------

This function returns the local granted roles the user has for the given object:

    >>> get_local_roles_for(cu)
    ['Owner']

The optional `user` parameter allows to get the local roles of another user:

    >>> get_local_roles_for(cu, "admin")
    []


Granting local roles
--------------------

This function allows to grant local roles on an object:

    >>> grant_local_roles_for(cu, "Sampler")
    ['Owner', 'Sampler']

    >>> grant_local_roles_for(cu, ["Analyst", "LabClerk"])
    ['Analyst', 'LabClerk', 'Owner', 'Sampler']

    >>> get_local_roles_for(cu)
    ['Analyst', 'LabClerk', 'Owner', 'Sampler']


Revoking local roles
--------------------

This function allows to revoke local roles on an object:

    >>> revoke_local_roles_for(cu, "Sampler")
    ['Analyst', 'LabClerk', 'Owner']

    >>> revoke_local_roles_for(cu, ["Analyst", "LabClerk"])
    ['Owner']

    >>> get_local_roles_for(cu)
    ['Owner']


Getting all valid roles
-----------------------

This function lists all valid roles for an object:

    >>> get_valid_roles_for(cu)
    ['Analyst', ...]


Granting a permission to a role
-------------------------------

This function allows to grant a permission to one or more roles:

    >>> get_permissions_for_role("Sampler", cu)
    ['senaite.core: Field: Edit Analysis Remarks', 'senaite.core: Field: Edit Analysis Result']

    >>> grant_permission_for(cu, FieldEditAnalysisHidden, "Sampler", acquire=0)

    >>> get_permissions_for_role("Sampler", cu)
    ['senaite.core: Field: Edit Analysis Hidden', 'senaite.core: Field: Edit Analysis Remarks', 'senaite.core: Field: Edit Analysis Result']


Revoking a permission from a role
---------------------------------

This function allows to revoke a permission of one or more roles:

    >>> revoke_permission_for(cu, FieldEditAnalysisHidden, "Sampler", acquire=0)

    >>> get_permissions_for_role("Sampler", cu)
    ['senaite.core: Field: Edit Analysis Remarks', 'senaite.core: Field: Edit Analysis Result']


Manage permissions
------------------

This function allows to set a permission explicitly  to the given roles (drop other roles):

    >>> grant_permission_for(cu, FieldEditAnalysisResult, ["Analyst", "LabClerk"])

    >>> get_permissions_for_role("Analyst", cu)
    ['senaite.core: Field: Edit Analysis Result']

    >>> get_permissions_for_role("LabClerk", cu)
    ['senaite.core: Field: Edit Analysis Result']

Now we use `manage_permission_for` to grant this permission *only* for Samplers:

    >>> manage_permission_for(cu, FieldEditAnalysisResult, ["Sampler"])

The Sampler has now the permission granted:

    >>> get_permissions_for_role("Sampler", cu)
    ['senaite.core: Field: Edit Analysis Remarks', 'senaite.core: Field: Edit Analysis Result']

But the Analyst and LabClerk not anymore:

    >>> get_permissions_for_role("Analyst", cu)
    []

    >>> get_permissions_for_role("LabClerk", cu)
    []
