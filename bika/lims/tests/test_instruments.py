from Products.CMFCore.utils import getToolByName
from bika.lims.testing import BIKA_FUNCTIONAL_TESTING
from bika.lims.tests.base import BikaFunctionalTestCase
from plone.app.testing import login, logout
from plone.app.testing import TEST_USER_NAME
from datetime import date
from DateTime import DateTime
import unittest

try:
    import unittest2 as unittest
except ImportError: # Python 2.7
    import unittest


class TestInstrumentAlerts(BikaFunctionalTestCase):
    layer = BIKA_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestInstrumentAlerts, self).setUp()
        login(self.portal, TEST_USER_NAME)

    def test_instrument_validation(self):
        # Getting all instruments
        bsc = getToolByName(self, 'bika_setup_catalog')
        instruments = bsc(portal_type='Instrument', inactive_state='active')
        # Setting validation dates
        for instrument in instruments:
            today = date.today()
            instrument.setDownTo(today)
            instrument.setDownFrom(today)
        try:
            for instrument in instruments:
                if not(instrument.isValidationInProgress()):
                    raise ValidationError('Instrument should be under validation progress')
        except ValidationError as e:
            print e.value

        for instrument in instruments:
            anotherday = DateTime('2014/11/27')
            instrument.setDownTo(anotherday)
            instrument.setDownFrom(anotherday)
        try:
            for instrument in instruments:
                if instrument.isValidationInProgress():
                    raise ValidationError('Instrument should not be under validation progress')
        except ValidationError as e:
            print e.value

    def test_instrument_calibration(self):
        # Getting all instruments
        bsc = getToolByName(self, 'bika_setup_catalog')
        instruments = bsc(portal_type='Instrument', inactive_state='active')
        # Setting calibration dates
        for instrument in instruments:
            today = date.today()
            instrument.setDownTo(today)
            instrument.setDownFrom(today)
        try:
            for instrument in instruments:
                if not(instrument.isCalibrationInProgress()):
                    raise CalibrationError('Instrument should be under calibration progress')
        except CalibrationError as e:
            print e.value

        for instrument in instruments:
            anotherday = DateTime('2014/11/27')
            instrument.setDownTo(anotherday)
            instrument.setDownFrom(anotherday)
        try:
            for instrument in instruments:
                if instrument.isCalibrationInProgress():
                    raise CalibrationError('Instrument should not be under calibration progress')
        except CalibrationError as e:
            print e.value

    def tearDown(self):
        logout()
        super(TestInstrumentAlerts, self).tearDown()


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInstrumentAlerts))
    suite.layer = BIKA_FUNCTIONAL_TESTING
    return suite