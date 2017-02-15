======================
Instrument Calibration
======================

Instruments represent the physical gadgets of the lab.

Each instruments needs some calibration from time to time, which can be done
inhouse or externally.

If the instrument is in calibration, it can not be used to fetch analysis results.



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

    >>> portal = self.getPortal()
    >>> portal_url = portal.absolute_url()
    >>> bika_setup = portal.bika_setup
    >>> bika_setup_url = portal_url + "/bika_setup"
    >>> browser = self.getBrowser()
    >>> setRoles(portal, TEST_USER_ID, ['LabManager', 'Manager', 'Owner'])

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

    >>> def login(user=TEST_USER_ID, password=TEST_USER_PASSWORD):
    ...     browser.open(portal_url + "/login_form")
    ...     browser.getControl(name='__ac_name').value = user
    ...     browser.getControl(name='__ac_password').value = password
    ...     browser.getControl(name='submit').click()
    ...     assert("__ac_password" not in browser.contents)
    ...     return ploneapi.user.get_current()

    >>> def logout():
    ...     browser.open(portal_url + "/logout")
    ...     assert("You are now logged out" in browser.contents)

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


Calibrations
============

Instrument calibrations live inside an instrument::

    >>> calibration1 = create(instrument1, "InstrumentCalibration", title="Calibration-1")
    >>> calibration2 = create(instrument2, "InstrumentCalibration", title="Calibration-2")

Calibrations can be in progress or not, depending on the entered dates::

    >>> calibration1.isCalibrationInProgress()
    False

The `DownFrom` field specifies the start date of the calibration::

    >>> down_from = DateTime()
    >>> calibration1.setDownFrom(down_from)

The calibration shouldn't be in progress with only this field set::

    >>> calibration1.isCalibrationInProgress()
    False

The `DownTo` field specifies the end date of the calibration::

    >>> down_to = down_from + 7  # one week in calibration
    >>> calibration1.setDownTo(down_to)

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
about the calibration which takes the longes time::

    >>> calibration3 = create(instrument1, "InstrumentCalibration", title="Calibration-3")
    >>> calibration3.setDownFrom(down_from)
    >>> calibration3.setDownTo(down_to + 7)

    >>> instrument1.getLatestValidCalibration()
    <InstrumentCalibration at /plone/bika_setup/bika_instruments/instrument-1/instrumentcalibration-3>

Only calibrations which are currently in progress are returned.
So if it would start tomorrow, it should not be returned::

    >>> calibration3.setDownFrom(down_from + 1)
    >>> calibration3.isCalibrationInProgress()
    False
    >>> instrument1.getLatestValidCalibration()
    <InstrumentCalibration at /plone/bika_setup/bika_instruments/instrument-1/instrumentcalibration-1>

If all calibrations are dated in the future, it should return none::

    >>> calibration1.setDownFrom(down_from + 1)
    >>> calibration1.isCalibrationInProgress()
    False
    >>> instrument1.getLatestValidCalibration()

Instruments w/o any calibration should also no valid calibrations::

    >>> instrument3.getLatestValidCalibration()


Calibration Certificates
========================

Certification live inside an instrument::

    >>> certification1 = create(instrument1, "InstrumentCertification", title="Certification-1")
    >>> certification2 = create(instrument2, "InstrumentCertification", title="Certification-2")

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

Setting an interval of 1 year (365 days) will calculate the `ValidTo` field automatically::

    >>> certification1.setExpirationInterval(365)
    >>> certification1.isValid()
    True

    >>> certification1.getDaysToExpire()
    365
