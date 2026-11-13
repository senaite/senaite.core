Calculation formulas and content objects
----------------------------------------

A formula is evaluated with RestrictedPython, without builtins, and imports
only from the modules the site allows.

This only concerns the functions of allowed modules: the values a formula
gets are numbers and text. But a function of an allowed module may return a
content object. From there, a formula would reach the whole site through
public names, e.g. acquisition, `acl_users` and setters, and nothing would
check permissions. A formula must not use the attributes of such objects.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t CalculationObjectEscalation


Test Setup
..........

Needed Imports:

    >>> import sys
    >>> import types
    >>> from bika.lims import api
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from senaite.core.api.calculation import allow_module
    >>> from senaite.core.api.calculation import evaluate_formula
    >>> from senaite.core.interfaces import ICalculationModule
    >>> from zope.component import getGlobalSiteManager

Variables:

    >>> portal = self.portal
    >>> setRoles(portal, TEST_USER_ID, ["Manager"])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills",
    ...                     ClientID="HH")
    >>> uid = api.get_uid(client)

An add-on module for calculations with a helper that returns the object of a
UID, registered and allowed as an add-on does it:

    >>> code = """
    ... from bika.lims import api
    ...
    ... def get_obj(uid):
    ...     return api.get_object_by_uid(uid)
    ... """
    >>> module = types.ModuleType("calc_helpers")
    >>> exec(code, module.__dict__)
    >>> sys.modules["calc_helpers"] = module

    >>> gsm = getGlobalSiteManager()
    >>> gsm.registerUtility(module, ICalculationModule, name="calc_helpers")
    >>> allow_module("calc_helpers")

    >>> imports = [{"module": "calc_helpers", "function": "get_obj"}]

`get_obj` is a function the module defines itself, so a calculation may
import it.


A lab manager does not escalate to Manager
..........................................

Lab managers edit the calculations. The user who runs the formula has no
more than that role:

    >>> setRoles(portal, TEST_USER_ID, ["LabManager"])
    >>> sorted(api.get_current_user().getRoles())
    ['Authenticated', 'LabManager']

The formula does not go up to the portal by acquisition:

    >>> formula = "get_obj([u]).aq_parent.aq_parent.getId()"
    >>> evaluate_formula(formula, {"u": uid}, imports)
    Traceback (most recent call last):
    ...
    UnsafeFormula: ...

It does not list the users of the site:

    >>> formula = "get_obj([u]).aq_parent.aq_parent.acl_users.getUserNames()"
    >>> evaluate_formula(formula, {"u": uid}, imports)
    Traceback (most recent call last):
    ...
    UnsafeFormula: ...

It does not add a user with the role `Manager`. The roles are a tuple, as
square brackets mark the values of a formula:

    >>> formula = (
    ...     "get_obj([u]).aq_parent.aq_parent.acl_users.userFolderAddUser("
    ...     "'intruder', 'secret', ('Manager',), ())")
    >>> evaluate_formula(formula, {"u": uid}, imports)
    Traceback (most recent call last):
    ...
    UnsafeFormula: ...

    >>> portal.acl_users.getUserById("intruder") is None
    True

It does not change content either:

    >>> name = client.getName()
    >>> formula = "get_obj([u]).setName('Changed')"
    >>> evaluate_formula(formula, {"u": uid}, imports)
    Traceback (most recent call last):
    ...
    UnsafeFormula: ...

    >>> client.getName() == name
    True

Clean up:

    >>> gsm.unregisterUtility(module, ICalculationModule, name="calc_helpers")
    True
    >>> del sys.modules["calc_helpers"]
