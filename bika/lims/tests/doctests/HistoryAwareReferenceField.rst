History Aware Reference Field
=============================

This field behaves almost the same like the standard AT ReferenceField, but
stores the version of the reference object on `set` and keeps that version.

Currently, only analyses uses that field to store the exact version of their
calculation. This ensures that later changes in, e.g. the formula, does not
affect already created analyses.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t HistoryAwareReferenceField


Test Setup
----------

Needed Imports:

    >>> from bika.lims import api
    >>> from bika.lims.api.security import *
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from DateTime import DateTime
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD

Functional Helpers:

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

		>>> def new_sample(services):
		...     values = {
		...         "Client": client.UID(),
		...         "Contact": contact.UID(),
		...         "DateSampled": date_now,
		...         "SampleType": sampletype.UID()}
		...     service_uids = map(api.get_uid, services)
		...     return create_analysisrequest(client, request, values, service_uids)

    >>> def get_analysis(sample, id):
    ...     ans = sample.getAnalyses(getId=id, full_objects=True)
    ...     if len(ans) != 1:
    ...         return None
    ...     return ans[0]


Environment Setup
-----------------

Setup the testing environment:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.bika_setup
    >>> date_now = DateTime().strftime("%Y-%m-%d")
    >>> date_future = (DateTime() + 5).strftime("%Y-%m-%d")
    >>> setRoles(portal, TEST_USER_ID, ['LabManager', ])
    >>> user = api.get_current_user()


LIMS Setup
----------

Setup the Lab for testing:

    >>> setup.setSelfVerificationEnabled(True)
    >>> analysisservices = setup.bika_analysisservices
    >>> calculations = setup.bika_calculations
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH")
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> labcontact = api.create(setup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.bika_departments, "Department", title="Chemistry", Manager=labcontact)
    >>> sampletype = api.create(setup.bika_sampletypes, "SampleType", title="Water", Prefix="Water")


Content Setup
-------------

Create some Analysis Services with unique Keywords:

    >>> Ca = api.create(analysisservices, "AnalysisService", title="Calcium", Keyword="Ca")
    >>> Mg = api.create(analysisservices, "AnalysisService", title="Magnesium", Keyword="Mg")
    >>> TH = api.create(analysisservices, "AnalysisService", title="Total Hardness", Keyword="TH")

Create a calculation for Total Hardness:

    >>> calc = api.create(calculations, "Calculation", title="Total Hardness")

The `Formula` field references the keywords from Analysis Services::

    >>> calc.setFormula("[Ca] + [Mg]")
    >>> calc.processForm()

    >>> calc.getFormula()
    '[Ca] + [Mg]'

    >>> calc.getMinifiedFormula()
    '[Ca] + [Mg]'

Set the calculation to the `TH` analysis service:

    >>> TH.setCalculation(calc)

Create an new Sample:

    >>> sample = new_sample([Ca, Mg, TH])

Get the `TH` analysis:

    >>> th = get_analysis(sample, "TH")

The calculation of the analysis should be unchanged:

    >>> th_calc = th.getCalculation()
    >>> th_calc.getFormula()
    '[Ca] + [Mg]'

Now we change the calculation formula:

    >>> calc.setFormula("2 * ([Ca] + [Mg])")
    >>> calc.getFormula()
    '2 * ([Ca] + [Mg])'
    >>> calc.processForm()

The calculation of the analysis should be unchanged:

    >>> th_calc = th.getCalculation()
    >>> th_calc.getFormula()
    '[Ca] + [Mg]'
