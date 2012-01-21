from Products.validation import validation
from bika.lims.testing import BIKA_INTEGRATION_TESTING
from plone.app.testing import *
from plone.testing import z2
from Products.validation import validation as validationService

import unittest

class Tests(unittest.TestCase):

    layer = BIKA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.app = self.layer['app']

    def test_UniqueFieldValidator(self):
        login(self.portal, TEST_USER_NAME)

        clients = self.portal.clients
        client1 = self.portal.clients['client-1']
        self.assertEqual(
            client1.schema.get('Name').validate('Norton Feeds', client1),
            u"Validation failed: 'Norton Feeds' is in use")
        self.assertEqual(
            client1.schema.get('title').validate('Another Client', client1),
            None)

    def test_ServiceKeywordValidator(self):
        login(self.portal, TEST_USER_NAME)

        services = self.portal.bika_setup.bika_analysisservices
        service1 = services['analysisservice-1']

        self.assertEqual(
            service1.schema.get('Keyword').validate('', service1),
            u'Analysis Keyword is required, please correct.')
        self.assertEqual(
            service1.schema.get('Keyword').validate('&', service1),
            u'Validation failed: keyword contains invalid characters')
        self.assertEqual(
            service1.schema.get('Keyword').validate('Ash', service1),
            u"Validation failed: 'Ash': This keyword is used by service 'Ash'")
        self.assertEqual(
            service1.schema.get('Keyword').validate('VALID_KW', service1),
            None)

    def test_InterimFieldsValidator(self):
        login(self.portal, TEST_USER_NAME)

        calcs = self.portal.bika_setup.bika_calculations
        calc1 = calcs['calculation-1']

        interim_fields = [{'keyword': '&', 'title':'Titration Volume', 'unit':'','default':''},]
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.portal.REQUEST['validated'] = None
        self.assertEqual(
            calc1.schema.get('InterimFields').validate(interim_fields, calc1, REQUEST=self.portal.REQUEST),
            u"Validation failed: keyword contains invalid characters"*2)

        interim_fields = [{'keyword': 'TV', 'title':'Titration Volume', 'unit':'','default':''},
                          {'keyword': 'TV', 'title':'Titration Volume', 'unit':'','default':''}]
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.portal.REQUEST['validated'] = None
        self.assertEqual(
            calc1.schema.get('InterimFields').validate(interim_fields, calc1, REQUEST=self.portal.REQUEST),
            u"Validation failed: 'TV': duplicate keyword"*2)

        interim_fields = [{'keyword': 'TV', 'title':'Titration Volume', 'unit':'','default':''},
                          {'keyword': 'TF', 'title':'Titration Volume', 'unit':'','default':''}]
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.portal.REQUEST['validated'] = None
        self.assertEqual(
            calc1.schema.get('InterimFields').validate(interim_fields, calc1, REQUEST=self.portal.REQUEST),
            u"Validation failed: 'Titration Volume': duplicate title"*2)

        interim_fields = [{'keyword': 'Ash', 'title':'Titration Volume', 'unit':'','default':''},
                          {'keyword': 'TF', 'title':'Titration Factor', 'unit':'','default':''}]
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.portal.REQUEST['validated'] = None
        self.assertEqual(
            calc1.schema.get('InterimFields').validate(interim_fields, calc1, REQUEST=self.portal.REQUEST),
            u"Validation failed: 'Ash': This keyword is used by service 'Ash'"*2)

        interim_fields = [{'keyword': 'TV', 'title':'Titration Volume', 'unit':'','default':''},
                          {'keyword': 'TF', 'title':'Titration Factor', 'unit':'','default':''}]
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.portal.REQUEST['validated'] = None
        self.assertEqual(
            calc1.schema.get('InterimFields').validate(interim_fields, calc1, REQUEST=self.portal.REQUEST),
            None)

    def test_FormulaValidator(self):
        login(self.portal, TEST_USER_NAME)

        v = validationService.validatorFor('formulavalidator')
        calcs = self.portal.bika_setup.bika_calculations
        calc1 = calcs['calculation-1']

        interim_fields = [{'keyword': 'TV', 'title':'Titration Volume', 'unit':'','default':''},
                          {'keyword': 'TF', 'title':'Titration Factor', 'unit':'','default':''}]
        self.portal.REQUEST.form['InterimFields'] = interim_fields

        formula = "[TV] * [TF] * [Ash] * [Wrong]"
        self.failUnlessEqual(
            v(formula, instance=calc1, field=calc1.schema.get('Formula'), REQUEST=self.portal.REQUEST),
            "Validation failed: Keyword 'Wrong' is invalid")

        formula = "[TV] * [TF] * [Ash]"
        self.failUnlessEqual(
            v(formula, instance=calc1, field=calc1.schema.get('Formula'), REQUEST=self.portal.REQUEST),
            True)

    def test_CoordinateValidator(self):
        login(self.portal, TEST_USER_NAME)

        sp = self.portal.bika_setup.bika_samplepoints['samplepoint-1']

        latitude = {'degrees':'!','minutes':'2','seconds':'3', 'bearing':'N'}
        self.portal.REQUEST.form['Latitude'] = latitude
        self.assertEqual(sp.schema.get('Latitude').validate(latitude, sp),
            u"Validation failed: degrees must be numeric")

        latitude = {'degrees':'0','minutes':'!','seconds':'3', 'bearing':'N'}
        self.portal.REQUEST.form['Latitude'] = latitude
        self.portal.REQUEST['validated'] = None
        self.assertEqual(
            sp.schema.get('Latitude').validate(latitude, sp),
            u"Validation failed: minutes must be numeric")

        latitude = {'degrees':'0','minutes':'0','seconds':'!', 'bearing':'N'}
        self.portal.REQUEST.form['Latitude'] = latitude
        self.portal.REQUEST['validated'] = None
        self.assertEqual(
            sp.schema.get('Latitude').validate(latitude, sp),
            u"Validation failed: seconds must be numeric")

        latitude = {'degrees':'0','minutes':'60','seconds':'0', 'bearing':'N'}
        self.portal.REQUEST.form['Latitude'] = latitude
        self.portal.REQUEST['validated'] = None
        self.assertEqual(
            sp.schema.get('Latitude').validate(latitude, sp),
            u"Validation failed: minutes must be 0 - 59")

        latitude = {'degrees':'0','minutes':'0','seconds':'60', 'bearing':'N'}
        self.portal.REQUEST.form['Latitude'] = latitude
        self.portal.REQUEST['validated'] = None
        self.assertEqual(
            sp.schema.get('Latitude').validate(latitude, sp),
            u"Validation failed: seconds must be 0 - 59")

        # latitude specific

        latitude = {'degrees':'91','minutes':'0','seconds':'0', 'bearing':'N'}
        self.portal.REQUEST.form['Latitude'] = latitude
        self.portal.REQUEST['validated'] = None
        self.assertEqual(
            sp.schema.get('Latitude').validate(latitude, sp),
            u"Validation failed: degrees must be 0 - 90")

        latitude = {'degrees':'90','minutes':'1','seconds':'0', 'bearing':'N'}
        self.portal.REQUEST.form['Latitude'] = latitude
        self.portal.REQUEST['validated'] = None
        self.assertEqual(
            sp.schema.get('Latitude').validate(latitude, sp),
            u"Validation failed: degrees is 90; minutes must be zero")

        latitude = {'degrees':'90','minutes':'0','seconds':'1', 'bearing':'N'}
        self.portal.REQUEST.form['Latitude'] = latitude
        self.portal.REQUEST['validated'] = None
        self.assertEqual(
            sp.schema.get('Latitude').validate(latitude, sp),
            u"Validation failed: degrees is 90; seconds must be zero")

        latitude = {'degrees':'90','minutes':'0','seconds':'0', 'bearing':'E'}
        self.portal.REQUEST.form['Latitude'] = latitude
        self.portal.REQUEST['validated'] = None
        self.assertEqual(
            sp.schema.get('Latitude').validate(latitude, sp),
            u"Validation failed: Bearing must be N/S")

        # longitude specific

        longitude = {'degrees':'181','minutes':'0','seconds':'0', 'bearing':'E'}
        self.portal.REQUEST.form['Longitude'] = longitude
        self.portal.REQUEST['validated'] = None
        self.assertEqual(
            sp.schema.get('Longitude').validate(longitude, sp),
            u"Validation failed: degrees must be 0 - 180")

        longitude = {'degrees':'180','minutes':'1','seconds':'0', 'bearing':'E'}
        self.portal.REQUEST.form['Longitude'] = longitude
        self.portal.REQUEST['validated'] = None
        self.assertEqual(
            sp.schema.get('Longitude').validate(longitude, sp),
            u"Validation failed: degrees is 180; minutes must be zero")

        longitude = {'degrees':'180','minutes':'0','seconds':'1', 'bearing':'E'}
        self.portal.REQUEST.form['Longitude'] = longitude
        self.portal.REQUEST['validated'] = None
        self.assertEqual(
            sp.schema.get('Longitude').validate(longitude, sp),
            u"Validation failed: degrees is 180; seconds must be zero")

        longitude = {'degrees':'0','minutes':'0','seconds':'0', 'bearing':'N'}
        self.portal.REQUEST.form['Longitude'] = longitude
        self.portal.REQUEST['validated'] = None
        self.assertEqual(
            sp.schema.get('Longitude').validate(longitude, sp),
            u"Validation failed: Bearing must be E/W")

        longitude = {'degrees':'1','minutes':'1','seconds':'1', 'bearing':'E'}
        self.portal.REQUEST.form['Longitude'] = longitude
        self.portal.REQUEST['validated'] = None
        self.assertEqual(
            sp.schema.get('Longitude').validate(longitude, sp),
            None)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Tests))
    suite.layer = BIKA_INTEGRATION_TESTING
    return suite
