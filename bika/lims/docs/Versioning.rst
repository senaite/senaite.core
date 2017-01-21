Versioning
==========

Some Bika LIMS contents support versioning. Each editing and saving process
creates a new version.


Test Setup
----------

    >>> from Acquisition import aq_base
    >>> from plone import api as ploneapi

    >>> def is_versionable(obj):
    ...     pr = ploneapi.portal.get_tool("portal_repository")
    ...     return pr.supportsPolicy(obj, 'at_edit_autoversion') and pr.isVersionable(obj)

    >>> def get_version(obj):
    ...     if not is_versionable(obj):
    ...         return None
    ...     return getattr(aq_base(obj), "version_id", 0)


Calculation
-----------

Create a calculation for testing::

    >>> calculations = self.portal.bika_setup.bika_calculations
    >>> _ = calculations.invokeFactory("Calculation", id="tempId", title="Test Calculation 1")
    >>> calculation = calculations.get(_)

Process Form to notify Bika about the new content type::

    >>> calculation.processForm()

Calcuations should be versionable::

    >>> is_versionable(calculation)
    True

    >>> get_version(calculation)
    0

Create a new version – for testing, it is sufficient to call the `process_form`
method, as this is also called after the content has been edited::

    >>> calculation.processForm()

    >>> get_version(calculation)
    1

The `log` view should reflect this version::

    >>> log_view = calculation.restrictedTraverse("@@log")
    >>> folderitems = log_view.folderitems()

There should be two versions::

    >>> len(folderitems)
    2

And the latest version should be 1::

    >>> folderitems[0]["Version"]
    1
