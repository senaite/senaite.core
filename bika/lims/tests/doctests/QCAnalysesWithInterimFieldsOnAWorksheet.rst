QC Analyses With Interim Fields On A Worksheet
==============================================

Creating analysis that has interims fields so that we can test for
Reference Analyses(Blank and Control) that have interim fields.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t QCAnalysesWithInterimFieldsOnAWorksheet


Test Setup
----------

Needed Imports:

    >>> import re
    >>> import transaction
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor
    >>> from DateTime import DateTime
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD
    >>> from plone.app.testing import setRoles

Functional Helpers:

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> bika_setup = portal.bika_setup
    >>> bikasetup = portal.bika_setup
    >>> bika_analysisservices = bika_setup.bika_analysisservices
    >>> bika_calculations = bika_setup.bika_calculations

We need to create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager', 'Analyst'])
    >>> date_now = DateTime().strftime("%Y-%m-%d")
    >>> date_future = (DateTime() + 5).strftime("%Y-%m-%d")
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(bikasetup.bika_sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(bikasetup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(bikasetup.bika_departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(bikasetup.bika_analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> supplier = api.create(bikasetup.bika_suppliers, "Supplier", Name="Naralabs")

    >>> interim_calc = api.create(bika_calculations, 'Calculation', title='Test-Total-Pest')
    >>> pest1 = {'keyword': 'pest1', 'title': 'Pesticide 1', 'value': 12.3, 'type': 'int', 'hidden': False, 'unit': ''}
    >>> pest2 = {'keyword': 'pest2', 'title': 'Pesticide 2', 'value': 14.89, 'type': 'int', 'hidden': False, 'unit': ''}
    >>> pest3 = {'keyword': 'pest3', 'title': 'Pesticide 3', 'value': 16.82, 'type': 'int', 'hidden': False, 'unit': ''}
    >>> interims = [pest1, pest2, pest3]
    >>> interim_calc.setInterimFields(interims)
    >>> self.assertEqual(interim_calc.getInterimFields(), interims)
    >>> interim_calc.setFormula('((([pest1] > 0.0) or ([pest2] > .05) or ([pest3] > 10.0) ) and "FAIL" or "PASS" )')
    >>> total_terpenes = api.create(bika_analysisservices, 'AnalysisService', title='Total Terpenes', Keyword="TotalTerpenes")
    >>> total_terpenes.setUseDefaultCalculation(False)
    >>> total_terpenes.setCalculation(interim_calc)
    >>> total_terpenes.setInterimFields(interims)
    >>> total_terpenes
    <AnalysisService at /plone/bika_setup/bika_analysisservices/analysisservice-1>
    >>> service_uids = [total_terpenes.UID()]

Create a Reference Definition for blank:

    >>> blankdef = api.create(bikasetup.bika_referencedefinitions, "ReferenceDefinition", title="Blank definition", Blank=True)
    >>> blank_refs = [{'uid': total_terpenes.UID(), 'result': '0', 'min': '0', 'max': '0'},]
    >>> blankdef.setReferenceResults(blank_refs)

And for control:

    >>> controldef = api.create(bikasetup.bika_referencedefinitions, "ReferenceDefinition", title="Control definition")
    >>> control_refs = [{'uid': total_terpenes.UID(), 'result': '10', 'min': '9.99', 'max': '10.01'},]
    >>> controldef.setReferenceResults(control_refs)

    >>> blank = api.create(supplier, "ReferenceSample", title="Blank",
    ...                    ReferenceDefinition=blankdef,
    ...                    Blank=True, ExpiryDate=date_future,
    ...                    ReferenceResults=blank_refs)
    >>> control = api.create(supplier, "ReferenceSample", title="Control",
    ...                      ReferenceDefinition=controldef,
    ...                      Blank=False, ExpiryDate=date_future,
    ...                      ReferenceResults=control_refs)


Create an Analysis Request:

    >>> sampletype_uid = api.get_uid(sampletype)
    >>> values = {
    ...     'Client': api.get_uid(client),
    ...     'Contact': api.get_uid(contact),
    ...     'DateSampled': date_now,
    ...     'SampleType': sampletype_uid,
    ...     'Priority': '1',
    ... }

    >>> ar = create_analysisrequest(client, request, values, service_uids)
    >>> ar
    <AnalysisRequest at /plone/clients/client-1/W-0001>
    >>> success = doActionFor(ar, 'receive')

Create a new Worksheet and add the analyses:

    >>> worksheet = api.create(portal.worksheets, "Worksheet", Analyst='test_user_1_')
    >>> worksheet
    <Worksheet at /plone/worksheets/WS-001>

    >>> analyses = map(api.get_object, ar.getAnalyses())
    >>> analysis = analyses[0]
    >>> analysis
    <Analysis at /plone/clients/client-1/W-0001/TotalTerpenes>
    >>> worksheet.addAnalysis(analysis)
    >>> analysis.getWorksheet().UID() == worksheet.UID()
    True

Add a blank and a control:

    >>> blanks = worksheet.addReferenceAnalyses(blank, service_uids)
    >>> transaction.commit()
    >>> blanks.sort(key=lambda analysis: analysis.getKeyword(), reverse=False)
    >>> controls = worksheet.addReferenceAnalyses(control, service_uids)
    >>> transaction.commit()
    >>> controls.sort(key=lambda analysis: analysis.getKeyword(), reverse=False)
    >>> transaction.commit()
    >>> for analysis in worksheet.getAnalyses():
    ...     if analysis.portal_type == 'ReferenceAnalysis':
    ...         if analysis.getReferenceType() == 'b' or analysis.getReferenceType() == 'c':
    ...             # 3 is the number of interim fields on the analysis/calculation
    ...             if len(analysis.getInterimFields()) != 3:
    ...                 self.fail("Blank or Control Analyses interim field are not correct")
