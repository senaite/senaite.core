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

Only valid date ranges switch the calibration to "in progress"::

    >>> calibration2.setDownFrom(DateTime() + 7)
    >>> calibration2.setDownTo(DateTime())

    >>> calibration2.isCalibrationInProgress()
    False

The instrument knows if a calibration is in progress::

    >>> instrument1.isCalibrationInProgress()
    True

    >>> instrument2.isCalibrationInProgress()
    False


Calibration Certificates
========================

Certification live inside an instrument::

    >>> certification1 = create(instrument1, "InstrumentCertification", title="Certification-1")
    >>> certification2 = create(instrument2, "InstrumentCertification", title="Certification-2")

Certifications can be in valid or not, depending on the entered dates::

    >>> certification1.isValid()
    False

The `ValidFrom` field specifies the start date of the certification::

    >>> valid_from = DateTime()
    >>> certification1.setValidFrom(valid_from)

The certification shouldn't be valid with only this field set::

    >>> certification1.isValid()
    False

The `ValidTo` field specifies the expiration date of the certification::

    >>> valid_to = valid_from + 7  # one week until expiration
    >>> certification1.setValidTo(valid_to)

With this valid date range, the certification is in valid::

    >>> certification1.isValid()
    True

Only valid date ranges switch the certification to "valid"::

    >>> certification2.setValidFrom(DateTime() + 7)
    >>> certification2.setValidTo(DateTime())

    >>> certification2.isValid()
    False
