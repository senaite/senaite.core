Versioning
----------

Versioning simply returns the snapshot version


Test Setup
..........

    >>> from Acquisition import aq_base
    >>> from bika.lims import api
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from zope.lifecycleevent import modified

    >>> portal = self.portal
    >>> setRoles(portal, TEST_USER_ID, ['LabManager', 'Manager', 'Owner'])

    >>> def get_version(obj):
    ...     return api.snapshot.get_version(obj)


Calculations
............

Create a calculation for testing::

    >>> calculations = self.portal.setup.calculations
    >>> calculation = api.create(calculations, "Calculation", title="Test Calculation 1")

The initial version is 0:

    >>> get_version(calculation)
    0

Calling the object modified event will create a new version:

    >>> modified(calculation)
    >>> get_version(calculation)
    1

    >>> modified(calculation)
    >>> get_version(calculation)
    2
