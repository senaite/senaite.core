from bika.lims.tests.base import BikaFunctionalTestCase

import transaction


class Tests(BikaFunctionalTestCase):

    def test_referencedefinition_view(self):
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
        defs = self.portal.bika_setup.bika_referencedefinitions
        defs.invokeFactory('ReferenceDefinition', id='def1')
        defs.def1.edit(
            title="Definition One",
            ReferenceResults=[{'uid': services.service1.UID(),
                               'result': '100',
                               'min':'90',
                               'max':'110',
                               'error': '10'},
                              {'uid': services.service2.UID(),
                               'result': '100',
                               'min':'90',
                               'max':'110',
                               'error': '10'}])
        defs.def1.unmarkCreationFlag()

        transaction.commit()

        browser = self.getBrowser()
        browser.open(defs.def1.absolute_url())
        self.assertTrue("Definition One" in browser.contents)

        # verify that the widget is showing the right values
        uid = services.service1.UID()
        self.assertEquals(
            browser.getControl(name='result.' + uid + ':records').value, "100")
        self.assertEquals(
            browser.getControl(name='min.' + uid + ':records').value, "90")
        self.assertEquals(
            browser.getControl(name='max.' + uid + ':records').value, "110")

        # some validation tests...

        browser.getControl(name='result.%s:records' % uid).value = "5"
        browser.getControl(name='min.%s:records' % uid).value = "10"
        browser.getControl(name='max.%s:records' % uid).value = "0"
        browser.getControl(name='form.button.save').click()
        self.assertTrue("Max values must be greater than Min values"
                        in browser.contents)

        browser.getControl(name='result.%s:records' % uid).value = "25"
        browser.getControl(name='min.%s:records' % uid).value = "10"
        browser.getControl(name='max.%s:records' % uid).value = "20"
        browser.getControl(name='form.button.save').click()
        self.assertTrue("Expected values must be between Min and Max values"
                        in browser.contents)

        tests = [
            {'uid':services.service1.UID(),
                'result':'-15', 'min':'-20', 'max':'-10', 'error':'10'},
            {'uid':services.service2.UID(),
                'result':'-16', 'min':'-21', 'max':'-11', 'error':'11'},
            {'uid':services.service3.UID(),
                'result':'-17', 'min':'-22', 'max':'-12', 'error':'12'},
        ]

        for s in tests:
            uid = s['uid']
            browser.getControl(name='result.' + uid + ':records').value = \
                s['result']
            browser.getControl(name='min.' + uid + ':records').value = s['min']
            browser.getControl(name='max.' + uid + ':records').value = s['max']
            browser.getControl(
                name='error.' + uid + ':records').value = s['error']
        description = 'Blank Reference description'
        browser.getControl(name='description').value = description
        browser.getControl(name='form.button.save').click()

        for s in tests:
            uid = s['uid']
            self.assertTrue(
                browser.getControl(name='result.' + uid + ':records').value,
                s['result'])
            self.assertTrue(
                browser.getControl(name='min.' + uid + ':records').value,
                s['min'])
            self.assertTrue(
                browser.getControl(name='max.' + uid + ':records').value,
                s['max'])
        self.assertTrue(
            browser.getControl(name='description').value,
            'Blank Reference description')
