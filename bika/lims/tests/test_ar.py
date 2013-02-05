from Products.CMFCore.utils import getToolByName
from bika.lims.tests.base import BikaIntegrationTestCase
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from bika.lims.browser.analysisrequest import ajaxAnalysisRequestSubmit


class Tests(BikaIntegrationTestCase):

    def test_AR(self):
        """ AR wf.
        """

        wf = getToolByName(self.portal, 'portal_workflow')
        setRoles(self.portal, TEST_USER_ID, ['Manager', 'LabManager',
                                             'Member'])
        wf.setChainForPortalTypes(('Analysis'),
                                  ('bika_analysis_workflow',
                                   'bika_worksheetanalysis_workflow',
                                   'bika_cancellation_workflow'))
        wf.setChainForPortalTypes(('AnalysisRequest'),
                                  ('bika_ar_workflow',
                                   'bika_worksheetanalysis_workflow',
                                   'bika_cancellation_workflow'))
        wf.setChainForPortalTypes(('SamplePartition', 'Sample'),
                                  ('bika_sample_workflow',
                                   'bika_cancellation_workflow'))
        setRoles(self.portal, TEST_USER_ID, ['LabManager', 'Member'])

        self.portal.bika_setup.setSamplingWorkflowEnabled(False)

        clients = self.portal.clients
        clients.invokeFactory('Client', 'client1', title="Client One")
        client1 = self.portal.clients.client1
        client1.setClientID('CLIENT1')
        client1.unmarkCreationFlag()
        client1.invokeFactory('Contact', 'contact1')
        contact1 = client1.contact1
        contact1.unmarkCreationFlag()
        contact1.edit(Firstname="First", Surname="Last")
        cats = self.portal.bika_setup.bika_analysiscategories
        cats.invokeFactory('AnalysisCategory', id='cat1', title='Category')
        cats.cat1.unmarkCreationFlag()
        services = self.portal.bika_setup.bika_analysisservices
        services.invokeFactory(
            'AnalysisService', id='service1', title='Service One')
        services.service1.unmarkCreationFlag()
        services.service1.edit(Category=cats.cat1)
        sampletypes = self.portal.bika_setup.bika_sampletypes
        sampletypes.invokeFactory('SampleType', id='st1', title="Type AAA 1")
        sampletypes.st1.unmarkCreationFlag()
        sampletypes.st1.edit(Prefix="ST1", MinimumVolume="10 ml")

        # Configure request for ar_add
        for x in (
            ('_authenticator', self.getAuthenticator()),
            ('CCEmails', ''),
            ('Contact', client1.contact1.UID()),
            ('Prices.' + services.service1.UID(), '10.00'),
            ('VAT.' + services.service1.UID(), '14.00'),
            ('ar.0', {
                'Analyses': [services.service1.UID()],
                'ClientID': 'CLIENT1',
                'ClientUID': client1.UID(),
                'SampleType': sampletypes.st1.UID(),
                'SamplingDate': '2013-01-31',
                'subtotal': '8.50',
                'total': '9.69',
                'vat': '1.19'})):
            self.request[x[0]] = x[1]

        # Create AR, samples, analyses
        ajaxAnalysisRequestSubmit(client1, self.request)

        def check_state(ar, desired_state):
            sample = ar.getSample()
            self.assertEqual(wf.getInfoFor(sample, 'review_state'),
                             desired_state)
            part = sample.objectValues('SamplePartition')[0]
            self.assertEqual(wf.getInfoFor(part, 'review_state'),
                             desired_state)
            analyses = ar.getAnalyses(full_objects=True)
            for a in analyses:
                self.assertEqual(wf.getInfoFor(a, 'review_state'),
                                 desired_state)

        ar = client1.objectValues('AnalysisRequest')[0]
        wf.doActionFor(ar, 'receive')
