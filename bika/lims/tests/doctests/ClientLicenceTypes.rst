====================
Client Licence Types
====================

Certain client require licences to operate. So one or more licences can be
stored in the client Licences field based of the client licence type

Running this test from the buildout directory::

    bin/test -t ClientLicenceTypes

Test Setup
==========
Needed Imports::

    >>> import transaction
    >>> from plone import api as ploneapi
    >>> from zope.lifecycleevent import modified

    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.idserver import renameAfterCreation

Variables::

    >>> portal = self.portal
    >>> bika_setup = portal.bika_setup
    >>> clientlicencetypes = bika_setup.bika_clientlicencetypes
    >>> portal_url = portal.absolute_url()
    >>> browser = self.getBrowser()
    >>> current_user = ploneapi.user.get_current()
    >>> ploneapi.user.grant_roles(user=current_user,roles = ['Manager'])


Test user::

We need certain permissions to create and access objects used in this test,
so here we will assume the role of Lab Manager.

    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])

ClientLicenceType
=================

A `ClientLicenceType` lives in `ClientLicenceTypes` folder::

    >>> clientlicencetype = api.create(clientlicencetypes, "ClientLicenceType", title="Cultivator")
    >>> renameAfterCreation(clientlicencetype)
    'clientlicencetype-1'
    >>> clientlicencetype
    <ClientLicenceType at /plone/bika_setup/bika_clientlicencetypes/clientlicencetype-1>


Client
======

A `client` lives in the `/clients` folder::

    >>> clients = self.portal.clients
    >>> client = api.create(clients, "Client", Name="RIDING BYTES", ClientID="RB")
    >>> client
    <Client at /plone/clients/client-1>
    >>> client.setLicences([{'Authority': 'AA', 'LicenceType':clientlicencetype.UID(), 'LicenceID': 'MY ID', 'LicenceNumber': 'RS451'},])
    >>> transaction.commit()
    >>> client_url = client.absolute_url() + '/base_edit'
    >>> browser.open(client_url)
    >>> "edit_form" in browser.contents
    True
    >>> browser.getControl(name='Licences.LicenceID:records', index=0).value == 'MY ID'
    True
    >>> browser.getControl(name='Licences.LicenceType:records', index=0).value[0] == clientlicencetype.UID()
    True
