Calculations
============

Bika LIMS can dynamically calculate a value based on the results of several
Analyses with a formula.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t Calculations


Test Setup
----------

Needed Imports::

    >>> import transaction
    >>> from operator import methodcaller
    >>> from plone import api as ploneapi

    >>> from bika.lims import api


Functional Helpers::

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)


Variables::

    >>> portal = self.portal
    >>> request = self.request
    >>> bika_setup = portal.bika_setup
    >>> bika_calculations = bika_setup.bika_calculations
    >>> bika_analysisservices = bika_setup.bika_analysisservices


Test user::

We need certain permissions to create and access objects used in this test,
so here we will assume the role of Lab Manager.

    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> setRoles(portal, TEST_USER_ID, ['Manager',])


Calculation
-----------

Calculations are created in the `bika_setup/bika_calculations` folder. They
offer a `Formula` field, where keywords from Analyses can be used to calculate a
result.

Each `AnalysisService` contains a `Keyword` field, which can be referenced in a formula::

    >>> as1 = api.create(bika_analysisservices, "AnalysisService", title="Calcium")
    >>> as1.setKeyword("Ca")
    >>> as1.reindexObject()

    >>> as2 = api.create(bika_analysisservices, "AnalysisService", title="Magnesium")
    >>> as2.setKeyword("Mg")
    >>> as2.reindexObject()


Create one `Calculation`::

    >>> calc = api.create(bika_calculations, "Calculation", title="Total Hardness")


The `Formula` field references the Keywords from Analysis Services::

    >>> calc.setFormula("[Ca] + [Mg]")
    >>> calc.getFormula()
    '[Ca] + [Mg]'

    >>> calc.getMinifiedFormula()
    '[Ca] + [Mg]'


The `Calculation` depends now on the two Analysis Services::

    >>> sorted(calc.getCalculationDependencies(flat=True), key=methodcaller('getId'))
    [<AnalysisService at /plone/bika_setup/bika_analysisservices/analysisservice-1>, <AnalysisService at /plone/bika_setup/bika_analysisservices/analysisservice-2>]

It is also possible to find out if an `AnalysisService` depends on the calculation::

    >>> as1.setCalculation(calc)
    >>> calc.getCalculationDependants()
    [<AnalysisService at /plone/bika_setup/bika_analysisservices/analysisservice-1>]

Or to find out which services have selected a particular calculation as their
primary Calculation field's value:

    >>> from bika.lims.browser.fields.uidreferencefield import get_backreferences
    >>> get_backreferences(calc, 'AnalysisServiceCalculation')
    ['...']

The `Formula` can be tested with dummy values in the `TestParameters` field::

    >>> form_value = [{"keyword": "Ca", "value": 5.6}, {"keyword": "Mg", "value": 3.3},]
    >>> calc.setTestParameters(form_value)
    >>> calc.setTestResult(form_value)
    >>> calc.getTestResult()
    '8.9'


Within a `Calculation` it is also possible to use a Python function to calculate
a result. The user can add a Python `module` as a dotted name and a member
function in the `PythonImports` field::

    >>> calc.setPythonImports([{'module': 'math', 'function': 'floor'}])
    >>> calc.setFormula("floor([Ca] + [Mg])")
    >>> calc.getFormula()
    'floor([Ca] + [Mg])'

    >>> calc.setTestResult(form_value)
    >>> calc.getTestResult()
    '8.0'


A `Calculation` can therefore dynamically get a module and a member::

    >>> calc._getModuleMember('math', 'ceil')
    <built-in function ceil>

