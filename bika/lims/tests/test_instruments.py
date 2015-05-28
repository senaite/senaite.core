from Products.CMFPlone.utils import _createObjectByType
from bika.lims.utils import tmpID
from bika.lims.testing import BIKA_FUNCTIONAL_TESTING
from bika.lims.tests.base import BikaFunctionalTestCase
from bika.lims.idserver import renameAfterCreation
from plone.app.testing import login, logout
from plone.app.testing import TEST_USER_NAME
from datetime import date
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
        instrument_names = self.portal.bika_setup.bika_instruments.keys()
        # Setting validation dates
        for instrument_name in instrument_names:
            instrument = self.portal.bika_setup.bika_instruments[instrument_name]
            today = date.today()
            # Getting last valid validation
            lastval = instrument.getLatestValidValidation()
            if not lastval:
                #  Creating a new validation
                cal_obj = _createObjectByType("InstrumentValidation", instrument, tmpID())
                cal_obj.edit(
                    title='test',
                    DownFrom=today.strftime("%Y/%m/%d"),
                    DownTo=today.strftime("%Y/%m/%d"),
                    Instrument=instrument
                )
                cal_obj.unmarkCreationFlag()
                renameAfterCreation(cal_obj)
            else:
                #  Updating last validation
                lastval.setDownTo(today.strftime("%Y/%m/%d"))
                lastval.setDownFrom(today.strftime("%Y/%m/%d"))

        for instrument_name in instrument_names:
            instrument = self.portal.bika_setup.bika_instruments[instrument_name]
            self.assertTrue(instrument.isValidationInProgress())

        for instrument_name in instrument_names:
            instrument = self.portal.bika_setup.bika_instruments[instrument_name]
            anotherday = '2014/11/27'
            lastval = instrument.getLatestValidValidation()
            lastval.setDownTo(anotherday)
            lastval.setDownFrom(anotherday)
        for instrument_name in instrument_names:
            instrument = self.portal.bika_setup.bika_instruments[instrument_name]
            self.assertFalse(instrument.isValidationInProgress())

    def test_instrument_calibration(self):
        # Getting all instruments
        instrument_names = self.portal.bika_setup.bika_instruments.keys()
        # Setting calibration dates
        for instrument_name in instrument_names:
            # Getting each instrument
            instrument = self.portal.bika_setup.bika_instruments[instrument_name]
            today = date.today()
            # Getting last valid calibration
            lastcal = instrument.getLatestValidCalibration()
            if not lastcal:
                #  Creating a new calibration
                cal_obj = _createObjectByType("InstrumentCalibration", instrument, tmpID())
                cal_obj.edit(
                    title='test',
                    DownFrom=today.strftime("%Y/%m/%d"),
                    DownTo=today.strftime("%Y/%m/%d"),
                    Instrument=instrument
                )
                cal_obj.unmarkCreationFlag()
                renameAfterCreation(cal_obj)
            else:
                #  Updating last calibration
                lastcal.setDownTo(today)
                lastcal.setDownFrom(today)
        #  Testing calibration state
        for instrument_name in instrument_names:
            instrument = self.portal.bika_setup.bika_instruments[instrument_name]
            self.assertTrue(instrument.isCalibrationInProgress())

        for instrument_name in instrument_names:
            instrument = self.portal.bika_setup.bika_instruments[instrument_name]
            anotherday = '2014/11/27'
            lastcal = instrument.getLatestValidCalibration()
            lastcal.setDownTo(anotherday)
            lastcal.setDownFrom(anotherday)
        for instrument_name in instrument_names:
            instrument = self.portal.bika_setup.bika_instruments[instrument_name]
            self.assertFalse(instrument.isCalibrationInProgress())

    def tearDown(self):
        logout()
        super(TestInstrumentAlerts, self).tearDown()


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInstrumentAlerts))
    suite.layer = BIKA_FUNCTIONAL_TESTING
    return suite