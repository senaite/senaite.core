Analysis Service - Activations and Inactivations
------------------------------------------------

The inactivation and activation of Analysis Services relies on `senaite_deactivable_type_workflow`.
To prevent inconsistencies that could have undesired effects, an Analysis Service
can only be deactivated if it does not have active dependents (this is, other
services that depends on the Analysis Service to calculate their results).

Following the same reasoning, an Analysis Service can only be activated if does
not have any calculation assigned or if does, the calculation is active, as well
as its dependencies (this is, other services the Analysis Service depends on to
calculate its result) are active .


Test Setup
----------

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
    >>> setup = portal.setup
    >>> bikasetup = portal.bika_setup
    >>> analysiscategories = setup.analysiscategories
    >>> bika_analysisservices = bikasetup.bika_analysisservices
    >>> calculations = setup.calculations
    >>> suppliers = setup.suppliers

We need to create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
    >>> labcontact = api.create(bikasetup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> supplier = api.create(suppliers, "Supplier", Name="Naralabs")
    >>> Ca = api.create(bika_analysisservices, "AnalysisService", title="Calcium", Keyword="Ca", Price="15", Category=category.UID())
    >>> Mg = api.create(bika_analysisservices, "AnalysisService", title="Magnesium", Keyword="Mg", Price="10", Category=category.UID())
    >>> Au = api.create(bika_analysisservices, "AnalysisService", title="Gold", Keyword="Au", Price="20", Category=category.UID())

Deactivation of Analysis Service
................................

All services can be deactivated:

    >>> getAllowedTransitions(Ca)
    ['deactivate']
    >>> getAllowedTransitions(Mg)
    ['deactivate']
    >>> getAllowedTransitions(Au)
    ['deactivate']

But if we create a new Analysis Service with a calculation that depends on them:

    >>> calc = api.create(calculations, "Calculation", title="Total Hardness")
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
..............................

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


Deactivated service is kept in profiles, but not returned
.........................................................

Create a profile:

    >>> profile = api.create(setup.analysisprofiles, "AnalysisProfile")
    >>> profile.setServices([Ca, Mg, Au])
    >>> [service.getKeyword() for service in profile.getServices()]
    ['Ca', 'Mg', 'Au']
    >>> len(profile.getRawServices())
    3

If we deactivate `Au`:

    >>> performed = doActionFor(Au, 'deactivate')
    >>> api.is_active(Au)
    False

Profile does no longer contain this service:

    >>> services = profile.getServices()
    >>> [service.getKeyword() for service in services]
    ['Ca', 'Mg']

Unless we explicitly ask to include inactive ones:

    >>> services = profile.getServices(active_only=False)
    >>> [service.getKeyword() for service in services]
    ['Ca', 'Mg', 'Au']

So the reference to inactive services is kept as a raw value:

    >>> len(profile.getRawServices())
    3

And if we re-activate `Au`:

    >>> performed = doActionFor(Au, 'activate')
    >>> api.is_active(Au)
    True

The profile returns the service again:

    >>> services = profile.getServices()
    >>> [service.getKeyword() for service in services]
    ['Ca', 'Mg', 'Au']


Deactivated service is kept in templates, but not returned
..........................................................

Create a sample template:

    >>> template = api.create(setup.sampletemplates, "SampleTemplate")
    >>> template.setServices([Ca, Mg, Au])
    >>> [service.getKeyword() for service in template.getServices()]
    ['Ca', 'Mg', 'Au']
    >>> len(template.getRawServices())
    3

If we deactivate `Au`:

    >>> performed = doActionFor(Au, 'deactivate')
    >>> api.is_active(Au)
    False

Template does no longer contain this service:

    >>> services = template.getServices()
    >>> [service.getKeyword() for service in services]
    ['Ca', 'Mg']

Unless we explicitly ask to include inactive ones:

    >>> services = template.getServices(active_only=False)
    >>> [service.getKeyword() for service in services]
    ['Ca', 'Mg', 'Au']

So the reference to inactive services is kept as a raw value:

    >>> len(profile.getRawServices())
    3

And if we re-activate `Au`:

    >>> performed = doActionFor(Au, 'activate')
    >>> api.is_active(Au)
    True

The template returns the service again:

    >>> services = template.getServices()
    >>> [service.getKeyword() for service in services]
    ['Ca', 'Mg', 'Au']
