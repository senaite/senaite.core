from bika.lims.tests.base import BikaFunctionalTestCase

import transaction


class Tests(BikaFunctionalTestCase):

    def test_analysisprofile_view(self):
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
        profiles = self.portal.bika_setup.bika_analysisprofiles
        profiles.invokeFactory('AnalysisProfile', id='profile1',
                               title='Analysis Profile One')
        profiles.profile1.setService([services.service1, services.service2])
        profiles.profile1.unmarkCreationFlag()

        transaction.commit()

        browser = self.getBrowser()
        browser.open("{}".format(profiles.profile1.absolute_url()))
        self.assertTrue("Analysis Profile One" in browser.contents)
        control = browser.getControl(name="uids:list")
        uids = control.value
        all_uids = control.options
        self.assertEqual(len(uids), 2)
        self.assertEqual(len(all_uids), 3)

        # select all and save
        control.value = all_uids
        browser.getControl(name='form.button.save').click()
        browser.reload()
        control = browser.getControl(name="uids:list")
        self.assertEqual(control.value, all_uids)

        # revert and save
        control = browser.getControl(name="uids:list")
        control.value = uids
        browser.getControl(name='form.button.save').click()
        browser.reload()
        control = browser.getControl(name="uids:list")
        self.assertEqual(control.value, uids)
