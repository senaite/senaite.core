from App.Common import package_home
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from DateTime import DateTime
from bika.lims import logger, bikaMessageFactory as _
from os.path import join
import Globals
import tempfile
from time import time
from plone.app.folder.utils import timer
import transaction
import random

class LoadTestData(BrowserView):

    def __call__(self):
        self.portal_catalog = getToolByName(self.context, 'portal_catalog')
        self.portal_workflow = getToolByName(self.context, 'portal_workflow')
        self.reference_catalog = getToolByName(self.context, 'reference_catalog')
        self.portal_registration = getToolByName(self.context, 'portal_registration')
        self.portal_groups = getToolByName(self.context, 'portal_groups')
        self.portal_membership = getToolByName(self.context, 'portal_membership')
        self.translate = getToolByName(self.context, 'translation_service').translate
        self.plone_utils = getToolByName(self.context, 'plone_utils')

        self.ars = self.load_ars()

        return "ok"

    def load_ars(self):

        counts = {'Digestible Energy': 10,
                  'Micro-Bio check': 10,
                  'Micro-Bio counts': 10,
                  'Trace Metals': 10}

        sampletypes = [p.getObject() for p in self.portal_catalog(portal_type="SampleType")]
        samplepoints = [p.getObject() for p in self.portal_catalog(portal_type="SamplePoint")]
        for client in self.context.clients.objectValues():
            contacts = [c for c in client.objectValues() if c.portal_type == 'Contact']
            for profile, count_ars in counts.items():
                profile = self.portal_catalog(portal_type='ARProfile',
                                              Title=profile)[0].getObject()
                profile_services = profile.getService()

                _ars = []
                t = timer()
                for i in range(1, count_ars+1):
                    sample_id = client.generateUniqueId('Sample')
                    client.invokeFactory(id = sample_id, type_name = 'Sample')
                    sample = client[sample_id]
                    sample.edit(
                        SampleID = sample_id,
                        SampleType = random.choice(sampletypes).Title(),
                        SamplePoint = random.choice(samplepoints).Title(),
                        ClientReference = "".join([chr(random.randint(70,90)) for r in range(5)]),
                        ClientSampleID = "".join([chr(random.randint(70,90)) for r in range(5)]),
                        LastARNumber = 1,
                        DateSubmitted = DateTime(),
                        DateSampled = DateTime(),
                        SubmittedByUser = sample.current_user()
                    )
                    sample.unmarkCreationFlag()
                    ar_id = client.generateARUniqueId("AnalysisRequest", sample_id, 1)
                    client.invokeFactory("AnalysisRequest", ar_id)
                    ar = client[ar_id]
                    _ars.append(ar)
                    ar.edit(
                        RequestID = ar_id,
                        DateRequested = DateTime(),
                        Contact = contacts[0],
                        CCContact = contacts[1],
                        CCEmails = "",
                        Sample = sample,
                        Profile = profile,
                        ClientOrderNumber = "".join([chr(random.randint(70,90)) for r in range(10)]),
                    )
                    ar.unmarkCreationFlag()
                    prices = {}
                    service_uids = []
                    for service in profile_services:
                        service_uids.append(service.UID())
                        prices[service.UID()] = service.getPrice()
                    ar.setAnalyses(service_uids, prices = prices)
                for i in range(5):
                    self.portal_workflow.doActionFor(_ars[i], 'receive')
                print t.next()
                transaction.get().commit()
