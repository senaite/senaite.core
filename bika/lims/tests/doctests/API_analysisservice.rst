API Analysis Service
====================

The `api_analysisservice` modue provides single functions for single purposes
especifically related with analyses services.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t API_AnalysisService

Test Setup
----------

Needed Imports::

    >>> from bika.lims import api
    >>> from bika.lims.api.analysisservice import get_calculation_dependencies_for
    >>> from bika.lims.api.analysisservice import get_calculation_dependants_for

Variables::

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.bika_setup
    >>> calculations = setup.bika_calculations
    >>> analysisservices = setup.bika_analysisservices

Test user::

We need certain permissions to create and access objects used in this test,
so here we will assume the role of Lab Manager.

    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> setRoles(portal, TEST_USER_ID, ['Manager',])


Calculation Dependencies
------------------------

Calculations can reference analysis services by *Keyword* in their *Formula*.

The referenced Analysis Services of the calculation are then dependencies of
the Analysis Service which has the Calculation assigned.

The dependencies of an Analysis Service can be retrieved by the API function
`get_calculation_dependencies_for`.


Create some Analysis Services with unique Keywords:

    >>> Ca = api.create(analysisservices, "AnalysisService", title="Calcium", Keyword="Ca")
    >>> Mg = api.create(analysisservices, "AnalysisService", title="Magnesium", Keyword="Mg")
    >>> Cu = api.create(analysisservices, "AnalysisService", title="Copper", Keyword="Cu")
    >>> Fe = api.create(analysisservices, "AnalysisService", title="Iron", Keyword="Fe")
    >>> Au = api.create(analysisservices, "AnalysisService", title="Aurum", Keyword="Au")
    >>> Test1 = api.create(analysisservices, "AnalysisService", title="Calculated Test Service 1", Keyword="Test1")
    >>> Test2 = api.create(analysisservices, "AnalysisService", title="Calculated Test Service 2", Keyword="Test2")

None of these services has so far any calculation dependencies:

    >>> any(map(get_calculation_dependencies_for, [Ca, Mg, Cu, Fe, Au, Test1, Test2]))
    False

Create a calculation, which references the `Ca` and `Mg` services, and link the
calculation to the `Test1` service:

    >>> calc1 = api.create(calculations, "Calculation", title="Calculation 1")
    >>> calc1.setFormula("[Ca] + [Mg]")
    >>> Test1.setCalculation(calc1)

The `Test1` service depends now on `Ca` and `Mg`:

    >>> deps = get_calculation_dependencies_for(Test1)
    >>> sorted(map(lambda d: d.getKeyword(), deps.values()))
    ['Ca', 'Mg']

Now we add `Fe` to the calculation:

    >>> calc1.setFormula("[Ca] + [Mg] + [Fe]")

The `Test1` service depends now on `Fe` as well:

    >>> deps = get_calculation_dependencies_for(Test1)
    >>> sorted(map(lambda d: d.getKeyword(), deps.values()))
    ['Ca', 'Fe', 'Mg']

Now we create a calculation which doubles the results of the calculated `Test1`
service and assign it to the `Test2` service:

    >>> calc2 = api.create(calculations, "Calculation", title="Calculation 2")
    >>> calc2.setFormula("[Test1] * 2")
    >>> Test2.setCalculation(calc2)

The `Test2` service depends now on the `Test1` service:

    >>> deps = get_calculation_dependencies_for(Test2)
    >>> sorted(map(lambda d: d.getKeyword(), deps.values()))
    ['Test1']


Calculation Dependants
----------------------

To get all Analysis Services which depend on a specific Analysis Service, the
API provides the function `get_calculation_dependants_for`.

The Analysis Service `Test1` references `Ca`, `Mg` and `Fe` by its calculation:

    >>> Test1.getCalculation().getFormula()
    '[Ca] + [Mg] + [Fe]'

Therefore, the dependant service of `Ca`, `Mg` and `Fe` is `Test1`

    >>> deps = get_calculation_dependants_for(Ca)
    >>> sorted(map(lambda d: d.getKeyword(), deps.values()))
    ['Test1']

    >>> deps = get_calculation_dependants_for(Mg)
    >>> sorted(map(lambda d: d.getKeyword(), deps.values()))
    ['Test1']

    >>> deps = get_calculation_dependants_for(Fe)
    >>> sorted(map(lambda d: d.getKeyword(), deps.values()))
    ['Test1']

The Analysis Service `Test2` doubles the calculated result from `Test1`:

    >>> Test2.getCalculation().getFormula()
    '[Test1] * 2'

Therefore, `Test2` is a dependant of `Test1`:

    >>> deps = get_calculation_dependants_for(Test1)
    >>> sorted(map(lambda d: d.getKeyword(), deps.values()))
    ['Test2']


Checking edge cases
-------------------

The assigned calculation of `Test2` doubles the value of `Test1`:

    >>> Test2.getCalculation().getFormula()
    '[Test1] * 2'

But what happens when the calculation references `Test2` as well?

    >>> Test2.getCalculation().setFormula("[Test1] * [Test2]")
    >>> Test2.getCalculation().getFormula()
    '[Test1] * [Test2]'

Checking the dependants of `Test2` should not cause an infinite recursion:

    >>> deps = get_calculation_dependants_for(Test2)
    >>> sorted(map(lambda d: d.getKeyword(), deps.values()))
    []
