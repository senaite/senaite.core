import time
from bika.lims.tests.base import *
from datetime import date
from datetime import timedelta

import transaction

class Tests(BikaFunctionalTestCase):

    def test_referencesample_view(self):
        cats = self.portal.bika_setup.bika_analysiscategories
        cats.invokeFactory('AnalysisCategory', id='cat1', title='Category')
        cats.cat1.unmarkCreationFlag()
        services = self.portal.bika_setup.bika_analysisservices
        services.invokeFactory(
            'AnalysisService', id='service1', title='Service One')
        services.invokeFactory(
            'AnalysisService', id='service2', title='Service Two')
        services.service1.unmarkCreationFlag()
        services.service2.unmarkCreationFlag()
        services.service1.edit(Category=cats.cat1)
        services.service2.edit(Category=cats.cat1)
        suppliers = self.portal.bika_setup.bika_referencesuppliers
        suppliers.invokeFactory(
            'ReferenceSupplier', id='sup1', title="Supplier One")
        suppliers.sup1.unmarkCreationFlag()
        mnfrs = self.portal.bika_setup.bika_referencemanufacturers
        mnfrs.invokeFactory(
            'ReferenceManufacturer', id='mnfr1', title="Mnfr One")
        mnfrs.mnfr1.unmarkCreationFlag()
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

        # widget already tested - here we create a new ReferenceSample TTW
        browser = self.getBrowser()
        browser.open(suppliers.sup1.absolute_url() + \
            "/createObject?type_name=ReferenceSample")

        title = "New reference"
        blank = True
        hazardous = True
        refdef = [defs.def1.UID()]
        mnfr = [mnfrs.mnfr1.UID()]
        catnum = '7627:23-AB.2391222'
        lotnum = 'LHG-32_32.41:20#12'
        today = date.today()
        datesampled = today - timedelta(days=-2)
        datereceived = today - timedelta(days=-2)
        dateopened = today
        expirydate = datesampled - timedelta(days=365)

        browser.getControl(name='title').value = title
        browser.getControl(name='ReferenceDefinition:list').value = refdef
        browser.getControl(name='Blank:boolean').value = blank
        browser.getControl(name='Hazardous:boolean').value = hazardous
        browser.getControl(name='ReferenceManufacturer:list').value = mnfr
        browser.getControl(name='CatalogueNumber').value = catnum
        browser.getControl(name='LotNumber').value = lotnum
        browser.getControl(name='DateSampled').value = datesampled.isoformat()
        browser.getControl(name='DateReceived').value = datereceived.isoformat()
        browser.getControl(name='DateOpened').value = dateopened.isoformat()
        browser.getControl(name='ExpiryDate').value = expirydate.isoformat()
        for rr in defs.def1.getReferenceResults():
            browser.getControl(
                name='result.{uid}:records'.format(**rr)).value = rr['result']
            browser.getControl(
                name='min.{uid}:records'.format(**rr)).value = rr['min']
            browser.getControl(
                name='max.{uid}:records'.format(**rr)).value = rr['max']

        browser.getControl(name='form.button.save').click()

        sample = suppliers.sup1.objectValues('ReferenceSample')[0]

        browser.open(sample.absolute_url() + "/base_edit")
        self.assertTrue('New reference' in browser.contents)

        # Check values
        ds = browser.getControl(name='DateSampled').value
        dr = browser.getControl(name='DateReceived').value
        do = browser.getControl(name='DateOpened').value
        ed = browser.getControl(name='ExpiryDate').value

        self.assertEqual(
            time.strftime('%b %d, %Y', datesampled.timetuple()), ds)
        self.assertEqual(
            time.strftime('%b %d, %Y', datereceived.timetuple()), dr)
        self.assertEqual(
            time.strftime('%b %d, %Y', dateopened.timetuple()), do)
        self.assertEqual(
            time.strftime('%b %d, %Y', expirydate.timetuple()), ed)

        self.assertEqual(browser.getControl(name='title').value, title)
        self.assertEqual(browser.getControl(name='ReferenceDefinition:list').value, refdef)
        self.assertEqual(browser.getControl(name='Blank:boolean').value, blank)
        self.assertEqual(browser.getControl(name='Hazardous:boolean').value, hazardous)
        self.assertEqual(browser.getControl(name='ReferenceManufacturer:list').value, mnfr)
        self.assertEqual(browser.getControl(name='CatalogueNumber').value, catnum)
        self.assertEqual(browser.getControl(name='LotNumber').value, lotnum)
