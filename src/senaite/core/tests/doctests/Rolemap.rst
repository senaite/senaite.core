Rolemap
=======

Bika LIMS defines several roles for the lab context


How to run this test
--------------------

Please execute the following command in the `buildout` directory::

    ./bin/test test_textual_doctests -t Rolemap


Test Setup
----------

Needed Imports::

    >>> from bika.lims import api

Test Variables::

    >>> portal = api.get_portal()
    >>> acl_users = api.get_tool("acl_users")


Check Bika LIMS Roles
---------------------

Ensure the "Analyst" role exists::

    >>> role = "Analyst"
    >>> role in acl_users.validRoles()
    True

Ensure the "Client" role exists::

    >>> role = "Client"
    >>> role in acl_users.validRoles()
    True

Ensure the "LabClerk" role exists::

    >>> role = "LabClerk"
    >>> role in acl_users.validRoles()
    True

Ensure the "LabManager" role exists::

    >>> role = "LabManager"
    >>> role in acl_users.validRoles()
    True

Ensure the "Member" role exists::

    >>> role = "Member"
    >>> role in acl_users.validRoles()
    True

Ensure the "Preserver" role exists::

    >>> role = "Preserver"
    >>> role in acl_users.validRoles()
    True

Ensure the "Publisher" role exists::

    >>> role = "Publisher"
    >>> role in acl_users.validRoles()
    True

Ensure the "RegulatoryInspector" role exists::

    >>> role = "RegulatoryInspector"
    >>> role in acl_users.validRoles()
    True

Ensure the "Reviewer" role exists::

    >>> role = "Reviewer"
    >>> role in acl_users.validRoles()
    True

Ensure the "Sampler" role exists::

    >>> role = "Sampler"
    >>> role in acl_users.validRoles()
    True

Ensure the "SamplingCoordinator" role exists::

    >>> role = "SamplingCoordinator"
    >>> role in acl_users.validRoles()
    True

Ensure the "Verifier" role exists::

    >>> role = "Verifier"
    >>> role in acl_users.validRoles()
    True



