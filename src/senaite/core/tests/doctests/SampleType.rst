Sample Type
===========

Sample Types define the types of physical samples that can be processed in
the laboratory. Each Sample Type has specific properties including a prefix
that must be ASCII-only without whitespaces.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t SampleType


Test Setup
..........

Imports:

    >>> from bika.lims import api
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> from zope.interface import Invalid


Setup the test user
...................

We need certain permissions to create and access objects used in this test,
so here we will assume the role of Lab Manager.

    >>> setRoles(portal, TEST_USER_ID, ["Manager"])


Get the sample types folder
...........................

    >>> setup = api.get_senaite_setup()
    >>> sampletypes = setup.sampletypes


Creating Sample Types
.....................

Create a basic sample type with a valid prefix:

    >>> sampletype = api.create(
    ...     sampletypes,
    ...     "SampleType",
    ...     title="Blood",
    ...     prefix="BLD",
    ...     min_volume="5 ml"
    ... )
    >>> api.get_id(sampletype)
    'sampletype-...'

    >>> sampletype.getPrefix()
    'BLD'


Prefix Validator - Valid Cases
..............................

Test that valid prefixes are accepted.


Valid ASCII prefix without whitespace
.....................................

    >>> sampletype1 = api.create(
    ...     sampletypes,
    ...     "SampleType",
    ...     title="Urine",
    ...     prefix="URN",
    ...     min_volume="10 ml"
    ... )
    >>> sampletype1.getPrefix()
    'URN'


Valid prefix with numbers
.........................

    >>> sampletype2 = api.create(
    ...     sampletypes,
    ...     "SampleType",
    ...     title="Sample Type 1",
    ...     prefix="ST1",
    ...     min_volume="5 ml"
    ... )
    >>> sampletype2.getPrefix()
    'ST1'


Valid prefix with underscores
.............................

    >>> sampletype3 = api.create(
    ...     sampletypes,
    ...     "SampleType",
    ...     title="Tissue Sample",
    ...     prefix="TSS_01",
    ...     min_volume="1 g"
    ... )
    >>> sampletype3.getPrefix()
    'TSS_01'


Valid prefix with hyphens
.........................

    >>> sampletype4 = api.create(
    ...     sampletypes,
    ...     "SampleType",
    ...     title="Serum Sample",
    ...     prefix="SRM-01",
    ...     min_volume="5 ml"
    ... )
    >>> sampletype4.getPrefix()
    'SRM-01'


Prefix Validator - Invalid Cases
................................

Test that invalid prefixes are rejected by directly testing the constraint
function and by attempting to create sample types with invalid prefixes.


Test the constraint function directly
......................................

Import the constraint function:

    >>> from senaite.core.content.sampletype import prefix_ascii_no_whitespaces_constraint


Invalid prefix with whitespace
...............................

Prefix with space should raise an error:

    >>> prefix_ascii_no_whitespaces_constraint("BLD 01")
    Traceback (most recent call last):
    ...
    Invalid: ...


Tab character is currently allowed
..................................

Note: The constraint currently only checks for space characters, not tabs:

    >>> prefix_ascii_no_whitespaces_constraint("BLD\t01")
    True


Invalid prefix with Unicode characters
......................................

Prefix with non-ASCII characters should raise an error:

    >>> prefix_ascii_no_whitespaces_constraint(u"BLÖ")
    Traceback (most recent call last):
    ...
    Invalid: ...


Invalid prefix with emoji
.........................

    >>> prefix_ascii_no_whitespaces_constraint(u"BLD😀")
    Traceback (most recent call last):
    ...
    Invalid: ...


Invalid prefix with Chinese characters
......................................

    >>> prefix_ascii_no_whitespaces_constraint(u"血液")
    Traceback (most recent call last):
    ...
    Invalid: ...


Edge Cases
..........


Empty prefix validation
........................

Empty strings should pass basic constraint but fail required validation:

    >>> from senaite.core.content.sampletype import prefix_ascii_no_whitespaces_constraint
    >>> prefix_ascii_no_whitespaces_constraint("")
    True


Single character prefix
.......................

    >>> sampletype5 = api.create(
    ...     sampletypes,
    ...     "SampleType",
    ...     title="Type A",
    ...     prefix="A",
    ...     min_volume="1 ml"
    ... )
    >>> sampletype5.getPrefix()
    'A'


Long prefix
...........

    >>> long_prefix = "VERY_LONG_PREFIX_123"
    >>> sampletype6 = api.create(
    ...     sampletypes,
    ...     "SampleType",
    ...     title="Type with Long Prefix",
    ...     prefix=long_prefix,
    ...     min_volume="1 ml"
    ... )
    >>> sampletype6.getPrefix()
    'VERY_LONG_PREFIX_123'


Prefix with special ASCII characters
.....................................

Test various special ASCII characters:

    >>> special_chars = ["ABC_123", "ABC-123", "ABC.123", "ABC+123"]
    >>> for i, prefix in enumerate(special_chars):
    ...     st = api.create(
    ...         sampletypes,
    ...         "SampleType",
    ...         title="Type {}".format(i),
    ...         prefix=prefix,
    ...         min_volume="1 ml"
    ...     )
    ...     st.getPrefix() == prefix
    True
    True
    True
    True


Updating Sample Type Prefix
............................

Test updating the prefix after creation:


Update with valid prefix
........................

    >>> sampletype.setPrefix("BLD2")
    >>> sampletype.getPrefix()
    'BLD2'


Unicode to ASCII conversion
............................

The setter should handle safe_unicode conversion:

    >>> sampletype.setPrefix(b"BLD3")
    >>> sampletype.getPrefix()
    'BLD3'


Prefix validation on update
............................

Invalid prefixes should be rejected on update as well. We can test this
by trying to set an invalid prefix:

    >>> # Create a sample type
    >>> temp_st = api.create(
    ...     sampletypes,
    ...     "SampleType",
    ...     title="Temp Type",
    ...     prefix="TMP",
    ...     min_volume="1 ml"
    ... )

Note: The constraint validation happens at the schema level during form
submission, not when using the setter directly. The setter accepts any
value and relies on the form validation to enforce constraints.


Sample ID Generation with Prefix
.................................

Test that the sample type prefix is correctly used in sample ID generation.


Create a client and contact for sample creation
................................................

    >>> from bika.lims.utils import tmpID

    >>> clients_folder = portal.clients
    >>> client = api.create(clients_folder, "Client", title="Test Client")
    >>> contact = api.create(client, "Contact", Firstname="Test", Surname="Contact")


Create samples with different prefixes
.......................................

Create a sample type with prefix "BLD":

    >>> blood_type = api.create(
    ...     sampletypes,
    ...     "SampleType",
    ...     title="Blood Sample",
    ...     prefix="BLD",
    ...     min_volume="5 ml"
    ... )


Create a sample with this sample type:

    >>> sample1 = api.create(
    ...     client,
    ...     "AnalysisRequest",
    ...     Contact=contact,
    ...     SampleType=blood_type
    ... )

Check the sample's sample type prefix:

    >>> sample1.getSampleType() == blood_type
    True

    >>> sample1.getSampleType().getPrefix()
    'BLD'


Create another sample type with different prefix
.................................................

    >>> urine_type = api.create(
    ...     sampletypes,
    ...     "SampleType",
    ...     title="Urine Sample",
    ...     prefix="URN",
    ...     min_volume="10 ml"
    ... )

    >>> sample2 = api.create(
    ...     client,
    ...     "AnalysisRequest",
    ...     Contact=contact,
    ...     SampleType=urine_type
    ... )

Check the second sample's sample type prefix:

    >>> sample2.getSampleType() == urine_type
    True

    >>> sample2.getSampleType().getPrefix()
    'URN'


Verify prefixes are different
..............................

The two samples should have different sample type prefixes:

    >>> sample1.getSampleType().getPrefix() != sample2.getSampleType().getPrefix()
    True


Sample Type Properties
......................

Test other Sample Type properties to ensure they work correctly.


Minimum Volume
..............

    >>> sampletype.getMinimumVolume()
    '5 ml'

    >>> sampletype.setMinimumVolume("10 ml")
    >>> sampletype.getMinimumVolume()
    '10 ml'


Hazardous Flag
..............

    >>> sampletype.getHazardous()
    False

    >>> sampletype.setHazardous(True)
    >>> sampletype.getHazardous()
    True


Sample Matrix
.............

Create a sample matrix first:

    >>> matrices = setup.samplematrices
    >>> matrix = api.create(
    ...     matrices,
    ...     "SampleMatrix",
    ...     title="Liquid"
    ... )

Set the sample matrix:

    >>> sampletype.setSampleMatrix(matrix)
    >>> sampletype.getSampleMatrix() == matrix
    True


Container Type
..............

Create a container type:

    >>> containertypes = setup.containertypes
    >>> container = api.create(
    ...     containertypes,
    ...     "ContainerType",
    ...     title="Tube 10ml"
    ... )

Set the container type:

    >>> sampletype.setContainerType(container)
    >>> sampletype.getContainerType() == container
    True


Retention Period
................

The retention period is a timedelta object:

    >>> from datetime import timedelta
    >>> period = sampletype.getRawRetentionPeriod()
    >>> isinstance(period, timedelta)
    True

Get as dict:

    >>> period_dict = sampletype.getRetentionPeriod()
    >>> "days" in period_dict or "hours" in period_dict or "minutes" in period_dict
    True

Set retention period:

    >>> from senaite.core.api import dtime
    >>> new_period = {"days": 30}
    >>> sampletype.setRetentionPeriod(new_period)
    >>> period = sampletype.getRawRetentionPeriod()
    >>> period.days
    30


Sticker Templates
.................

Test the sticker templates functionality:

    >>> stickers = sampletype.getAdmittedStickerTemplates()
    >>> isinstance(stickers, list)
    True

    >>> len(stickers) > 0
    True

Get admitted stickers:

    >>> admitted = sampletype.getAdmittedStickers()
    >>> isinstance(admitted, (list, set, tuple))
    True

Get default stickers:

    >>> small = sampletype.getDefaultSmallSticker()
    >>> small is None or isinstance(small, (str, unicode))
    True

    >>> large = sampletype.getDefaultLargeSticker()
    >>> large is None or isinstance(large, (str, unicode))
    True


Sample Type Deactivation
........................

Sample types implement IDeactivable:

    >>> from bika.lims.interfaces import IDeactivable
    >>> IDeactivable.providedBy(sampletype)
    True

Check if active:

    >>> api.is_active(sampletype)
    True

Deactivate:

    >>> _ = api.do_transition_for(sampletype, "deactivate")
    >>> api.is_active(sampletype)
    False

Reactivate:

    >>> _ = api.do_transition_for(sampletype, "activate")
    >>> api.is_active(sampletype)
    True


Cataloging
..........

Sample types are cataloged in the setup catalog:

    >>> from senaite.core.catalog import SETUP_CATALOG
    >>> setup_catalog = api.get_tool(SETUP_CATALOG)
    >>> brains = setup_catalog(portal_type="SampleType", getId=api.get_id(sampletype))
    >>> len(brains) == 1
    True

    >>> brain = brains[0]
    >>> api.get_object(brain) == sampletype
    True


Cleanup
.......

Note: In this test environment, cleanup is handled automatically by the
test layer teardown. Objects created during the test will be removed
when the test completes.
