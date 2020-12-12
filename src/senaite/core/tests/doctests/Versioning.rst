Versioning
----------

NOTE: Versioning is outdated!

This code will be removed as soon as we removed the `HistoryAwareReferenceField` reference
between Calculation and Analysis.

Each edit & save process creates a new version, which is triggered by the
`ObjectEditedEvent` from `Products.CMFEditions` package.


Test Setup
..........

    >>> from Acquisition import aq_base
    >>> from plone import api as ploneapi
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID

    >>> portal = self.portal
    >>> setRoles(portal, TEST_USER_ID, ['LabManager', 'Manager', 'Owner'])

    >>> def is_versionable(obj):
    ...     pr = ploneapi.portal.get_tool("portal_repository")
    ...     return pr.supportsPolicy(obj, 'at_edit_autoversion') and pr.isVersionable(obj)

    >>> def get_version(obj):
    ...     if not is_versionable(obj):
    ...         return None
    ...     return getattr(aq_base(obj), "version_id", None)


Calculations
............

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
