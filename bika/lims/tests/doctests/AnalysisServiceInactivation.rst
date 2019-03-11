================================================
Analysis Service - Activations and Inactivations
================================================

The inactivation and activation of Analysis Services relies on `senaite_deactivable_type_workflow`.
To prevent inconsistencies that could have undesired effects, an Analysis Service
can only be deactivated if it does not have active dependents (this is, other
services that depends on the Analysis Service to calculate their results).

Following the same reasoning, an Analysis Service can only be activated if does
not have any calculation assigned or if does, the calculation is active, as well
as its dependencies (this is, other services the Analysis Service depends on to
calculate its result) are active .


Test Setup
==========

Running this test from the buildout directory:

    bin/test -t AnalysisServiceInactivation

Needed Imports:

    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from bika.lims import api
    >>> from bika.lims.workflow import doActionFor
    >>> from bika.lims.workflow import getAllowedTransitions
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD
    >>> from plone.app.testing import setRoles

Functional Helpers:

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> bikasetup = portal.bika_setup
    >>> bika_analysiscategories = bikasetup.bika_analysiscategories
    >>> bika_analysisservices = bikasetup.bika_analysisservices
    >>> bika_calculations = bikasetup.bika_calculations
    >>> bika_suppliers = bikasetup.bika_suppliers

We need to create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
    >>> labcontact = api.create(bikasetup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(bikasetup.bika_departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(bika_analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> supplier = api.create(bika_suppliers, "Supplier", Name="Naralabs")
    >>> Ca = api.create(bika_analysisservices, "AnalysisService", title="Calcium", Keyword="Ca", Price="15", Category=category.UID())
    >>> Mg = api.create(bika_analysisservices, "AnalysisService", title="Magnesium", Keyword="Mg", Price="10", Category=category.UID())
    >>> Au = api.create(bika_analysisservices, "AnalysisService", title="Gold", Keyword="Au", Price="20", Category=category.UID())

Deactivation of Analysis Service
--------------------------------

All services can be deactivated:

    >>> getAllowedTransitions(Ca)
    ['deactivate']
    >>> getAllowedTransitions(Mg)
    ['deactivate']
    >>> getAllowedTransitions(Au)
    ['deactivate']

But if we create a new Analysis Service with a calculation that depends on them:

    >>> calc = api.create(bika_calculations, "Calculation", title="Total Hardness")
    >>> calc.setFormula("[Ca] + [Mg]")
    >>> hardness = api.create(bika_analysisservices, "AnalysisService", title="Total Hardness", Keyword="TotalHardness")
    >>> hardness.setCalculation(calc)

Then, only `Au` can be deactivated, cause `harndess` is active and depends on
`Ca` and `Mg`:

    >>> getAllowedTransitions(Ca)
    []
    >>> getAllowedTransitions(Mg)
    []
    >>> getAllowedTransitions(Au)
    ['deactivate']
    >>> getAllowedTransitions(hardness)
    ['deactivate']

If we deactivate `Hardness`:

    >>> performed = doActionFor(hardness, 'deactivate')
    >>> api.is_active(hardness)
    False

    >>> getAllowedTransitions(hardness)
    ['activate']

Then we will be able to deactivate both `Ca` and `Mg`:

    >>> getAllowedTransitions(Ca)
    ['deactivate']
    >>> getAllowedTransitions(Mg)
    ['deactivate']


Activation of Analysis Service
------------------------------

Deactivate the Analysis Service `Ca`:

    >>> performed = doActionFor(Ca, 'deactivate')
    >>> api.is_active(Ca)
    False

    >>> getAllowedTransitions(Ca)
    ['activate']

And now, we cannot activate `Hardness`, cause one of its dependencies (`Ca`) is
not active:

    >>> api.is_active(hardness)
    False
    >>> getAllowedTransitions(hardness)
    []

But if we activate `Ca` again:

    >>> performed = doActionFor(Ca, 'activate')
    >>> api.is_active(Ca)
    True

`Hardness` can be activated again:

    >>> getAllowedTransitions(hardness)
    ['activate']

    >>> performed = doActionFor(hardness, 'activate')
    >>> api.is_active(hardness)
    True
