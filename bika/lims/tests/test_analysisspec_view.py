from bika.lims.tests.base import BikaFunctionalTestCase

import transaction


class Tests(BikaFunctionalTestCase):

    def test_analysisspec_view(self):
        stypes = self.portal.bika_setup.bika_sampletypes
        stypes.invokeFactory('SampleType', id='st1', title='Type One')
        stypes.st1.unmarkCreationFlag()
        services = self.portal.bika_setup.bika_analysisservices
        services.invokeFactory('AnalysisService', id='service1')
        services.invokeFactory('AnalysisService', id='service2')
        services.invokeFactory('AnalysisService', id='service3')
        services.service1.edit(title="Service One", Keyword="S1")
        services.service2.edit(title="Service Two", Keyword="S2")
        services.service3.edit(title="Service Two", Keyword="S2")
        services.service1.unmarkCreationFlag()
        services.service2.unmarkCreationFlag()
        services.service3.unmarkCreationFlag()
        specs = self.portal.bika_setup.bika_analysisspecs
        specs.invokeFactory('AnalysisSpec', id='spec1')
        specs.spec1.edit(
            SampleType=stypes.st1,
            ResultsRange=[
                {'keyword': 'S1', 'min':'1', 'max':'10', 'error': '10'},
                {'keyword': 'S2', 'min':'5', 'max':'10', 'error': '10'}])
        specs.spec1.unmarkCreationFlag()

        transaction.commit()

        browser = self.getBrowser()
        browser.open(specs.spec1.absolute_url())

        # verify that the widget is showing the right values
        self.assertTrue("Type One" in browser.contents)
        s1_uid = services.service1.UID()
        self.assertEquals(
            browser.getControl(name=('min.' + s1_uid + ':records')).value,
            "1")
        self.assertEquals(
            browser.getControl(name=('max.' + s1_uid + ':records')).value,
            "10")
        s2_uid = services.service2.UID()
        self.assertEquals(
            browser.getControl(name=('min.' + s2_uid + ':records')).value,
            "5")
        self.assertEquals(
            browser.getControl(name=('max.' + s2_uid + ':records')).value,
            "10")

        # some validation tests...

        browser.getControl(name=('min.' + s1_uid + ':records')).value = "10"
        browser.getControl(name=('max.' + s1_uid + ':records')).value = "1"
        browser.getControl(name='form.button.save').click()
        self.assertTrue('Max values must be greater than Min values'
            in browser.contents)

        browser.getControl(name=('min.' + s1_uid + ':records')).value = "1"
        browser.getControl(name=('max.' + s1_uid + ':records')).value = "10"
        browser.getControl(name=('error.' + s1_uid + ':records')).value = "-1"
        browser.getControl(name='form.button.save').click()
        self.assertTrue('Error percentage must be between 0 and 100'
            in browser.contents)

        browser.getControl(name=('min.' + s1_uid + ':records')).value = "10"
        browser.getControl(name=('max.' + s1_uid + ':records')).value = "20"
        browser.getControl(name=('error.' + s1_uid + ':records')).value = "101"
        browser.getControl(name='form.button.save').click()
        self.assertTrue('Error percentage must be between 0 and 100'
            in browser.contents)

        # normal save and retrieve
        tests = [{'id':'1', 'min':'-20', 'max':'-10', 'error':'10'},
                 {'id':'2', 'min':'-10', 'max': '0', 'error':'10'},
                 {'id':'3', 'min': '0', 'max': '10', 'error':'10'}]
        for s in tests:
            uid = services["service" + s['id']].UID()
            browser.getControl(name='min.' + uid + ':records').value = s['min']
            browser.getControl(name='max.' + uid + ':records').value = s['max']
            browser.getControl(
                name='error.' + uid + ':records').value = s['error']
        browser.getControl(name='description').value = 'Type Two Spec'
        browser.getControl(name='form.button.save').click()
        for s in tests:
            service = services['service' + s['id']]
            uid = service.UID()
            self.assertTrue(
                browser.getControl(name='min.' + uid + ':records').value,
                s['min'])
            self.assertTrue(
                browser.getControl(name='max.' + uid + ':records').value,
                s['max'])
            self.assertTrue(
                browser.getControl(name='error.' + uid + ':records').value,
                s['error'])
        self.assertTrue(
            browser.getControl(name='description').value, 'Type Two Spec')
