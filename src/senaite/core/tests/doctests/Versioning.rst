Versioning
==========

Some Bika LIMS contents support versioning.

Each edit & save process creates a new version, which is triggered by the
`ObjectEditedEvent` from `Products.CMFEditions` package.


Test Setup
----------

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


Versionable Types
-----------------

The following types support versioning::

    >>> versionable_types = ["AnalysisService", "Calculation"]


Analysis Services
-----------------

Create a analysis service for testing::

    >>> analysisservices = self.portal.bika_setup.bika_analysisservices
    >>> _ = analysisservices.invokeFactory("AnalysisService", id="tempId", title="Test Analysis Service 1")
    >>> analysisservice = analysisservices.get(_)

Process Form to notify Bika about the new content type::

    >>> analysisservice.processForm()

Calcuations should be versionable::

    >>> is_versionable(analysisservice)
    True

    >>> get_version(analysisservice)
    0

Create a new version – for testing, it is sufficient to call the `process_form`
method, as this is also called after the content has been edited::

    >>> analysisservice.processForm()

    >>> get_version(analysisservice)
    1


Calculations
------------

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


Non Versionable Types
---------------------

The following types used to be versionable in Bika LIMS in the past.


Methods
.......

Create a method for testing::

    >>> methods = self.portal.methods
    >>> _ = methods.invokeFactory("Method", id="tempId", title="Test Method 1")
    >>> method = methods.get(_)

Process Form to notify Bika about the new content type::

    >>> method.processForm()

Methods shouldn't be versionable::

    >>> is_versionable(method)
    False


Sample Points
.............

Create a sample point for testing::

    >>> samplepoints = self.portal.bika_setup.bika_samplepoints
    >>> _ = samplepoints.invokeFactory("SamplePoint", id="tempId", title="Test Sample Point 1")
    >>> samplepoint = samplepoints.get(_)

Process Form to notify Bika about the new content type::

    >>> samplepoint.processForm()

Calcuations should be versionable::

    >>> is_versionable(samplepoint)
    False


Sample Types
............

Create a sample type for testing::

    >>> sampletypes = self.portal.bika_setup.bika_sampletypes
    >>> _ = sampletypes.invokeFactory("SampleType", id="tempId", title="Test Sample Point 1")
    >>> sampletype = sampletypes.get(_)

Process Form to notify Bika about the new content type::

    >>> sampletype.processForm()

Calcuations should be versionable::

    >>> is_versionable(sampletype)
    False


Storage Locations
.................

Create a sample type for testing::

    >>> storagelocations = self.portal.bika_setup.bika_storagelocations
    >>> _ = storagelocations.invokeFactory("StorageLocation", id="tempId", title="Test Sample Point 1")
    >>> storagelocation = storagelocations.get(_)

Process Form to notify Bika about the new content type::

    >>> storagelocation.processForm()

Calcuations should be versionable::

    >>> is_versionable(storagelocation)
    False
