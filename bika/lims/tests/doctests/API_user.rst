API User
========

The user API provides a simple interface to control users and groups in SENAITE

Running this test from the buildout directory::

    bin/test test_textual_doctests -t API_user


Test Setup
----------

Needed Imports:

    >>> from bika.lims import api
    >>> from bika.lims.api.user import *
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD


Environment Setup
-----------------

Setup the testing environment:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager', ])
    >>> user = api.get_current_user()


Get user
--------

Get the user object (not the memberdata wrapped user):

    >>> current_user = get_user()
    >>> current_user
    <PloneUser 'test-user'>

This function takes also an optional `user` argument:

    >>> other_user = get_user("admin")
    >>> other_user
    <PropertiedUser 'admin'>

It can also take the user object:

    >>> other_user = get_user(other_user)
    >>> other_user
    <PropertiedUser 'admin'>

Or a `MemberData` object:

    >>> member = api.get_user(TEST_USER_ID)
    >>> member
    <MemberData at /plone/portal_memberdata/test_user_1_ used for /plone/acl_users>

    >>> get_user(member)
    <PloneUser 'test-user'>

It returns `None` if the user was not found:

    >>> get_user("nonexistant") is None
    True


Get user ID
-----------

The user ID can be retrieved by the same objects as the `get_user`
function:

    >>> current_user_id = get_user_id()
    >>> current_user_id
    'test_user_1_'

It takes also the optional `user` argument:

    >>> get_user_id(TEST_USER_ID)
    'test_user_1_'

It can also take the user object:

    >>> current_user = get_user()
    >>> get_user_id(current_user)
    'test_user_1_'

If the user was not found, it returns `None`:

    >>> get_user_id("nonexistant") is None
    True


Get user groups
---------------

This function returns the groups the user belongs to:

    >>> get_groups()
    ['AuthenticatedUsers']

It takes also the optional `user` argument:

    >>> get_groups('admin')
    ['AuthenticatedUsers']


Get group
---------

This function returns a group object:

    >>> get_group('Analysts')
    <GroupData at /plone/portal_groupdata/Analysts used for /plone/acl_users/source_groups>

It returns `None` if the group was not found:

    >>> get_group('noexistant') is None
    True

If the group is `None`, all groups are returned:

    >>> get_group(None) is None
    True


Add group
---------

This function adds users to group(s):

    >>> add_group("Analysts")
    ['AuthenticatedUsers', 'Analysts']


It takes also an optinal `user` parameter to add another user to a group:

    >>> add_group("LabManagers", "admin")
    ['AuthenticatedUsers', 'LabManagers']


Also adding a user to multiple groups are allowed:

    >>> add_group(["Analyst", "Samplers", "Publishers"], "admin")
    ['Publishers', 'Samplers', 'LabManagers', 'AuthenticatedUsers']


Delete group
------------

This function removes users from group(s):

    >>> get_groups()
    ['AuthenticatedUsers', 'Analysts']

    >>> del_group("Analysts")
    ['AuthenticatedUsers']


Also removing a user from multiple groups is allowed:

    >>> get_groups("admin")
    ['Publishers', 'Samplers', 'LabManagers', 'AuthenticatedUsers']

    >>> del_group(["Publishers", "Samplers", "LabManagers"], "admin")
    ['AuthenticatedUsers']
