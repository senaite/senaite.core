Method
------

A Method describes how an analysis is performed. Methods can be assigned to
analysis services and define which instruments and calculations are possible.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t Method


Test Setup
..........

Needed Imports::

    >>> from bika.lims import api
    >>> from bika.lims.workflow import doActionFor as do_action_for

Variables::

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup
    >>> bika_setup = portal.bika_setup
    >>> methods = setup.methods
    >>> calculations = setup.calculations
    >>> instruments = bika_setup.bika_instruments


Test user::

    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> setRoles(portal, TEST_USER_ID, ["Manager", ])


Create a Method
...............

Methods are created in the `setup/methods` folder::

    >>> method = api.create(methods, "Method", title="Titration")
    >>> method
    <Method at /plone/setup/methods/method-1>

    >>> api.get_portal_type(method)
    'Method'

The method provides the expected marker interfaces::

    >>> from senaite.core.interfaces import IMethod
    >>> from bika.lims.interfaces import IHaveInstrument
    >>> from bika.lims.interfaces import IDeactivable
    >>> IMethod.providedBy(method)
    True
    >>> IHaveInstrument.providedBy(method)
    True
    >>> IDeactivable.providedBy(method)
    True


Method fields
.............

The `Method ID` and `Accredited` fields::

    >>> method.setMethodID("M-001")
    >>> method.getMethodID()
    'M-001'

    >>> method.setAccredited(True)
    >>> method.getAccredited()
    True

The `Instructions` field stores rich text::

    >>> method.setInstructions("<p>Follow the SOP</p>")
    >>> instructions = method.getInstructions()
    >>> instructions.output
    u'<p>Follow the SOP</p>'


Calculations
............

A method can support several calculations::

    >>> calc1 = api.create(calculations, "Calculation", title="Calc 1")
    >>> calc2 = api.create(calculations, "Calculation", title="Calc 2")

    >>> method.setCalculations([api.get_uid(calc1), api.get_uid(calc2)])
    >>> sorted(map(api.get_title, method.getCalculations()))
    ['Calc 1', 'Calc 2']

    >>> sorted(method.getRawCalculations()) == sorted(
    ...     [api.get_uid(calc1), api.get_uid(calc2)])
    True


Instruments (back reference with write-back)
............................................

The `Instruments` field is computed from the instruments that reference the
method (`Instrument.Methods`). Assigning instruments on the method writes the
reference back to the instrument side.

Create two instruments::

    >>> instrument1 = api.create(instruments, "Instrument", title="Balance")
    >>> instrument2 = api.create(instruments, "Instrument", title="Photometer")

Initially, the method has no instruments::

    >>> method.getInstruments()
    []

Assign the instruments on the method::

    >>> method.setInstruments([api.get_uid(instrument1),
    ...                        api.get_uid(instrument2)])

The method now reports both instruments::

    >>> sorted(map(api.get_title, method.getInstruments()))
    ['Balance', 'Photometer']

The change was written back to the instrument side::

    >>> method in instrument1.getMethods()
    True
    >>> method in instrument2.getMethods()
    True

Removing an instrument on the method also updates the instrument::

    >>> method.setInstruments([api.get_uid(instrument1)])
    >>> map(api.get_title, method.getInstruments())
    ['Balance']
    >>> method in instrument2.getMethods()
    False

Linking from the instrument side is reflected on the method too::

    >>> instrument2.setMethods([method])
    >>> sorted(map(api.get_title, method.getInstruments()))
    ['Balance', 'Photometer']

Only active instruments are reported. Deactivating an instrument removes it
from the method's instruments::

    >>> success, message = do_action_for(instrument2, "deactivate")
    >>> api.get_review_status(instrument2)
    'inactive'
    >>> map(api.get_title, method.getInstruments())
    ['Balance']


Method ID uniqueness
....................

The Method ID must be unique. The schema invariant refuses a duplicate::

    >>> from senaite.core.content.method import IMethodSchema
    >>> from zope.interface import Invalid

    >>> method2 = api.create(methods, "Method", title="Another Method")
    >>> method2.setMethodID("M-001")

    >>> class FakeData(object):
    ...     def __init__(self, method_id, context):
    ...         self.method_id = method_id
    ...         self.__context__ = context

    >>> try:
    ...     IMethodSchema.validateInvariants(FakeData("M-001", method2))
    ...     print("no error")
    ... except Invalid:
    ...     print("Invalid")
    Invalid

A unique Method ID validates fine::

    >>> IMethodSchema.validateInvariants(FakeData("M-002", method2))
