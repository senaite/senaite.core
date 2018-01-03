UIDReferenceField
=================

UIDReferenceField is a drop-in replacement for Plone's ReferenceField which
uses a StringField to store a UID or a list of UIDs.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t UIDReferenceField

Needed Imports:

    >>> import re
    >>> from bika.lims import api
    >>> from bika.lims.browser.fields.uidreferencefield import get_backreferences

Functional Helpers:

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> bika_calculations = portal.bika_setup.bika_setup.bika_calculations
    >>> bika_analysisservices = portal.bika_setup.bika_setup.bika_analysisservices

Test user:

We need certain permissions to create and access objects used in this test,
so here we will assume the role of Lab Manager.

    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])

I'll test using the relationship between Calculations and AnalysisServices.

First I'll create some AnalysisServices and Calculations:

    >>> as1 = api.create(bika_analysisservices, "AnalysisService", title="AS 1")
    >>> as1.setKeyword("as1")
    >>> as1.reindexObject()
    >>> as2 = api.create(bika_analysisservices, "AnalysisService", title="AS 2")
    >>> as2.setKeyword("as2")
    >>> as2.reindexObject()
    >>> as3 = api.create(bika_analysisservices, "AnalysisService", title="AS 3")
    >>> as3.setKeyword("as3")
    >>> as3.reindexObject()
    >>> c1 = api.create(bika_calculations, "Calculation", title="C 1")
    >>> c2 = api.create(bika_calculations, "Calculation", title="C 2")

Put some AS Keywords into the `Formula` field of the calculations, which will
cause their DependentServices field (a UIDReferenceField) to be populated.

    >>> c1.setFormula("[as1] + [as2] + [as3]")
    >>> c2.setFormula("[as1] + [as2]")

c1 now depends on three services:

    >>> deps = [s.Title() for s in c1.getDependentServices()]
    >>> deps.sort()
    >>> deps
    ['AS 1', 'AS 2', 'AS 3']

c2 now depends on two services:

    >>> deps = [s.Title() for s in c2.getDependentServices()]
    >>> deps.sort()
    >>> deps
    ['AS 1', 'AS 2']

Backreferences are stored on each object which is a target of a
UIDReferenceField.  This allows a service to ask, "which calculations
include me in their DependentServices?":

    >>> get_backreferences(as1, 'CalculationDependentServices')
    ['...', '...']

It also allows to find out which services have selected a particular
calculation as their primary Calculation field's value:

    >>> as3.setCalculation(c2)
    >>> get_backreferences(c2, 'AnalysisServiceCalculation')
    ['...']

The value will always be a list of UIDs, unless as_brains is True:

    >>> get_backreferences(c2, 'AnalysisServiceCalculation', as_brains=1)
    [<Products.ZCatalog.Catalog.mybrains object at ...>]

If no relationship is specified when calling get_backreferences, then a dict
is returned (by reference) containing UIDs of all references for all relations.
Modifying this dict in-place, will cause the backreferences to be changed!

    >>> get_backreferences(as1)
    {'CalculationDependentServices': ['...', '...']}

When requesting the entire set of all backreferences only UIDs may be returned,
and it is an error to request brains:

    >>> get_backreferences(as1, as_brains=True)
    Traceback (most recent call last):
    ...
    AssertionError: You cannot use as_brains with no relationship
