Instrument Calibration, Certification and Validation
====================================================

Instruments represent the physical gadgets of the lab.

Each instrument needs calibration from time to time, which can be done inhouse
or externally.

If an instrument is calibrated, an instrument certification is issued.
Certifications are only valid within a specified date range.

Instruments can also be validated by the lab personell for a given time.

Only valid instruments, which are not currently calibrated or validated are
available in the system and can be used to fetch results for analysis.

Running this test from the buildout directory::

    bin/test -t InstrumentCalibrationCertificationAndValidation

Test Setup
==========

    >>> import transaction
    >>> from DateTime import DateTime
    >>> from plone import api as ploneapi
    >>> from zope.lifecycleevent import modified
    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD

    >>> portal = self.portal
    >>> portal_url = portal.absolute_url()
    >>> bika_setup = portal.bika_setup
    >>> setRoles(portal, TEST_USER_ID, ['LabManager', 'Manager', 'Owner'])

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

    >>> def get_roles_for_permission(permission, context):
    ...     allowed = set(rolesForPermissionOn(permission, context))
    ...     return sorted(allowed)

    >>> def create(container, portal_type, title=None):
    ...     # Creates a content in a container and manually calls processForm
    ...     title = title is None and "Test {}".format(portal_type) or title
    ...     _ = container.invokeFactory(portal_type, id="tmpID", title=title)
    ...     obj = container.get(_)
    ...     obj.processForm()
    ...     modified(obj)  # notify explicitly for the test
    ...     transaction.commit()  # somehow the created method did not appear until I added this
    ...     return obj

    >>> def get_workflows_for(context):
    ...     # Returns a tuple of assigned workflows for the given context
    ...     workflow = ploneapi.portal.get_tool("portal_workflow")
    ...     return workflow.getChainFor(context)

    >>> def get_workflow_status_of(context):
    ...     # Returns the workflow status of the given context
    ...     return ploneapi.content.get_state(context)


Instruments
===========

All instruments live in the `/bika_setup/bika_instruments` folder::

    >>> instruments = bika_setup.bika_instruments
    >>> instrument1 = create(instruments, "Instrument", title="Instrument-1")
    >>> instrument2 = create(instruments, "Instrument", title="Instrument-2")
    >>> instrument3 = create(instruments, "Instrument", title="Instrument-3")

Instruments provide the `IInstrument` interface::

    >>> from bika.lims.interfaces import IInstrument
    >>> IInstrument.providedBy(instrument1)
    True


Calibrations
============

Instrument calibrations live inside an instrument::

    >>> calibration1 = create(instrument1, "InstrumentCalibration", title="Calibration-1")
    >>> calibration2 = create(instrument2, "InstrumentCalibration", title="Calibration-2")

Calibrations provide the `IInstrumentCalibration` interface::

    >>> from bika.lims.interfaces import IInstrumentCalibration
    >>> IInstrumentCalibration.providedBy(calibration1)
    True

Calibrations can be in progress or not, depending on the entered dates::

    >>> calibration1.isCalibrationInProgress()
    False

The `DownFrom` field specifies the start date of the calibration::

    >>> calibration1.setDownFrom(DateTime())

The calibration shouldn't be in progress with only this field set::

    >>> calibration1.isCalibrationInProgress()
    False

The `DownTo` field specifies the end date of the calibration::

    >>> calibration1.setDownTo(DateTime() + 7) # In calibration for 7 days

With this valid date range, the calibration is in progress::

    >>> calibration1.isCalibrationInProgress()
    True

The instrument will return in 7 days::

    >>> calibration1.getRemainingDaysInCalibration()
    7

Only valid date ranges switch the calibration to "in progress"::

    >>> calibration2.setDownFrom(DateTime() + 7)
    >>> calibration2.setDownTo(DateTime())

    >>> calibration2.isCalibrationInProgress()
    False

    >>> calibration2.getRemainingDaysInCalibration()
    0

The instrument knows if a calibration is in progress::

    >>> instrument1.isCalibrationInProgress()
    True

    >>> instrument2.isCalibrationInProgress()
    False

Since multiple calibrations might be in place, the instrument needs to know
about the calibration which takes the longest time::

    >>> calibration3 = create(instrument1, "InstrumentCalibration", title="Calibration-3")
    >>> calibration3.setDownFrom(DateTime())
    >>> calibration3.setDownTo(DateTime() + 365)

    >>> instrument1.getLatestValidCalibration()
    <InstrumentCalibration at /plone/bika_setup/bika_instruments/instrument-1/instrumentcalibration-3>

Only calibrations which are currently in progress are returned.
So if it would start tomorrow, it should not be returned::

    >>> calibration3.setDownFrom(DateTime() + 1)
    >>> calibration3.isCalibrationInProgress()
    False
    >>> instrument1.getLatestValidCalibration()
    <InstrumentCalibration at /plone/bika_setup/bika_instruments/instrument-1/instrumentcalibration-1>

If all calibrations are dated in the future, it should return none::

    >>> calibration1.setDownFrom(DateTime() + 1)
    >>> calibration1.isCalibrationInProgress()
    False
    >>> instrument1.getLatestValidCalibration()

Instruments w/o any calibration should return no valid calibrations::

    >>> instrument3.getLatestValidCalibration()


Calibration Certificates
========================

Certification live inside an instrument::

    >>> certification1 = create(instrument1, "InstrumentCertification", title="Certification-1")
    >>> certification2 = create(instrument2, "InstrumentCertification", title="Certification-2")

Certifications provide the `IInstrumentCertification` interface::

    >>> from bika.lims.interfaces import IInstrumentCertification
    >>> IInstrumentCertification.providedBy(certification1)
    True

Certifications can be in valid or not, depending on the entered dates::

    >>> certification1.isValid()
    False

The `ValidFrom` field specifies the start date of the certification::

    >>> certification1.setValidFrom(DateTime())

The certification shouldn't be valid with only this field set::

    >>> certification1.isValid()
    False

The `ValidTo` field specifies the expiration date of the certification::

    >>> certification1.setValidTo(DateTime() + 7)  # one week until expiration

With this valid date range, the certification is in valid::

    >>> certification1.isValid()
    True

For exactly 7 days::

    >>> certification1.getDaysToExpire()
    7

Or one week::

    >>> certification1.getWeeksAndDaysToExpire()
    (1, 0)

Only valid date ranges switch the certification to "valid"::

    >>> certification2.setValidFrom(DateTime() + 7)
    >>> certification2.setValidTo(DateTime())

    >>> certification2.isValid()
    False

    >>> certification2.getDaysToExpire()
    0

    >>> certification2.getWeeksAndDaysToExpire()
    (0, 0)

The instrument knows if a certification is valid/out of date::

    >>> instrument1.isOutOfDate()
    False

    >>> instrument2.isOutOfDate()
    True

Since multiple certifications might be in place, the instrument needs to know
about the certification with the longest validity::

    >>> certification3 = create(instrument1, "InstrumentCertification", title="Certification-3")
    >>> certification3.setValidFrom(DateTime())
    >>> certification3.setValidTo(DateTime() + 365)  # one year until expiration

    >>> instrument1.getLatestValidCertification()
    <InstrumentCertification at /plone/bika_setup/bika_instruments/instrument-1/instrumentcertification-3>

Only certifications which are valid are returned.
So if the validation would start tomorrow, it should not be returned::

    >>> certification3.setValidFrom(DateTime() + 1)
    >>> certification3.isValid()
    False
    >>> instrument1.getLatestValidCertification()
    <InstrumentCertification at /plone/bika_setup/bika_instruments/instrument-1/instrumentcertification-1>

If all certifications are dated in the future, it shouldn't be returned::

    >>> certification1.setValidFrom(DateTime() + 1)
    >>> certification1.setValidTo(DateTime() + 7)
    >>> instrument1.getLatestValidCertification()

It should also marked as invalid:

    >>> certification1.isValid()
    False

But the days to expire are calculated until the `ValidTo` date from today.
Thus, the full 7 days are returned::

    >>> certification1.getDaysToExpire()
    7

Instruments w/o any certifications should also return no valid certifications::

    >>> instrument3.getLatestValidCertification()


Certification Expiration Intervals
==================================

Besides the `ValidFrom` and `ValidTo` date range, users might also specify an `ExpirationInterval`,
which calculates the expiration date automatically on save.

Removing the `ValidTo` field makes the certificate invalid::

    >>> certification1.setValidFrom(DateTime())
    >>> certification1.setValidTo(None)

    >>> certification1.isValid()
    False

Setting an interval of 1 year (365 days)::

    >>> certification1.setExpirationInterval(365)

The interval takes now precedence over the `ValidTo` date, but only if the
custom `setValidTo` setter is called. This setter is always called when using
the `edit` form in Plone::

    >>> certification1.setValidTo(None)
    >>> certification1.isValid()
    True

    >>> certification1.getDaysToExpire()
    365


Validation
==========

Validations live inside an instrument::

    >>> validation1 = create(instrument1, "InstrumentValidation", title="Validation-1")
    >>> validation2 = create(instrument2, "InstrumentValidation", title="Validation-2")

Validations provide the `IInstrumentValidation` interface::

    >>> from bika.lims.interfaces import IInstrumentValidation
    >>> IInstrumentValidation.providedBy(validation1)
    True

Validations can be in progress or not, depending on the entered dates::

    >>> validation1.isValidationInProgress()
    False

The `DownFrom` field specifies the start date of the validation::

    >>> validation1.setDownFrom(DateTime())

The validation shouldn't be in progress with only this field set::

    >>> validation1.isValidationInProgress()
    False

The `DownTo` field specifies the end date of the validation::

    >>> validation1.setDownTo(DateTime() + 7)  # Down for 7 days

With this valid date range, the calibration is in progress::

    >>> validation1.isValidationInProgress()
    True

The instrument will be available after 7 days::

    >>> validation1.getRemainingDaysInValidation()
    7

Since multiple validations might be in place, the instrument needs to know
about the validation which takes the longest time::

    >>> validation3 = create(instrument1, "InstrumentValidation", title="Validation-3")
    >>> validation3.setDownFrom(DateTime())
    >>> validation3.setDownTo(DateTime() + 365)

    >>> instrument1.getLatestValidValidation()
    <InstrumentValidation at /plone/bika_setup/bika_instruments/instrument-1/instrumentvalidation-3>

Only validations which are currently in progress are returned.
So if it would start tomorrow, it should not be returned::

    >>> validation3.setDownFrom(DateTime() + 1)
    >>> validation3.isValidationInProgress()
    False
    >>> instrument1.getLatestValidValidation()
    <InstrumentValidation at /plone/bika_setup/bika_instruments/instrument-1/instrumentvalidation-1>

If all validations are dated in the future, it should return none::

    >>> validation1.setDownFrom(DateTime() + 1)
    >>> validation1.isValidationInProgress()
    False
    >>> instrument1.getLatestValidValidation()

Instruments w/o any validation should return no valid validations::

    >>> instrument3.getLatestValidValidation()
