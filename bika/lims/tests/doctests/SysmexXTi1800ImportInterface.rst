Sysmex xt i1800 import interface
================================

Running this test from the buildout directory::

    bin/test test_textual_doctests -t SysmexXTi4000ImportInterface


Test Setup
----------
Needed imports::

    >>> import os
    >>> import transaction
    >>> from Products.CMFCore.utils import getToolByName
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from DateTime import DateTime

    >>> import codecs
    >>> from bika.lims.exportimport import instruments
    >>> from bika.lims.exportimport.instruments.sysmex.xt import SysmexXTImporter
    >>> from bika.lims.exportimport.instruments.sysmex.xt.i1800 import TX1800iParser
    >>> from bika.lims.browser.resultsimport.resultsimport import ConvertToUploadFile

Functional helpers::

    >>> def timestamp(format="%Y-%m-%d"):
    ...     return DateTime().strftime(format)

Variables::

    >>> date_now = timestamp()
    >>> portal = self.portal
    >>> request = self.request
    >>> bika_setup = portal.bika_setup
    >>> bika_instruments = bika_setup.bika_instruments
    >>> bika_sampletypes = bika_setup.bika_sampletypes
    >>> bika_samplepoints = bika_setup.bika_samplepoints
    >>> bika_analysiscategories = bika_setup.bika_analysiscategories
    >>> bika_analysisservices = bika_setup.bika_analysisservices

We need certain permissions to create and access objects used in this test,
so here we will assume the role of Lab Manager::

    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> setRoles(portal, TEST_USER_ID, ['Manager',])

