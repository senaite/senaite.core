Sample analyses
---------------

Integration test for sample analyses and to measure the performance of the
sample creation process.


Running this test from the buildout directory::

    bin/test test_textual_doctests -t SampleAnalyses


Test Setup
..........

Imports:

    >>> from bika.lims import api
    >>> from senaite.core.api import dtime
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest as crar
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from bika.lims.api import do_transition_for
    >>> from DateTime import DateTime

Test User:

    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> setRoles(portal, TEST_USER_ID, ['Manager',])

Helpers:

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

    >>> def timestamp(format="%Y-%m-%d"):
    ...     return DateTime().strftime(format)

    >>> def new_sample(**kw):
    ...     client = kw.get("client")
    ...     contact = kw.get("contact")
    ...     sampletype = kw.get("sampletype")
    ...     samplepoint = kw.get("samplepoint")
    ...     calculation = kw.get("calculation")
    ...     services = kw.get("services")
    ...     values = {
    ...         "Client": client,
    ...         "Contact": contact,
    ...         "DateSampled": timestamp(),
    ...         "SampleType": sampletype,
    ...         "SamplePoint": samplepoint,
    ...         "Calculation": calculation,
    ...     }
    ...     service_uids = map(api.get_uid, services)
    ...     return crar(client, request, values, service_uids)

    >>> def try_transition(object, transition_id, target_state_id):
    ...      success = do_action_for(object, transition_id)[0]
    ...      state = api.get_workflow_status_of(object)
    ...      return success and state == target_state_id

    >>> def submit_analyses(sample):
    ...     for analysis in sample.getAnalyses():
    ...         analsis = api.get_object(analysis)
    ...         analysis.setResult(13)
    ...         do_action_for(analysis, "submit")

    >>> def get_analysis_by_keyword(sample, keyword):
    ...     for analysis in sample.getAnalyses():
    ...         if analysis.getKeyword == keyword:
    ...             return api.get_object(analysis)


Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = api.get_setup()
    >>> clients = portal.clients
    >>> sampletypes = setup.bika_sampletypes
    >>> labcontacts = setup.bika_labcontacts
    >>> departments = setup.bika_departments
    >>> categories = setup.bika_analysiscategories
    >>> services = setup.bika_analysisservices
    >>> samplepoints = setup.bika_samplepoints
    >>> calculations = setup.bika_calculations

Settings:

    >>> setup.setSelfVerificationEnabled(True)

Environment:

    >>> client1 = api.create(clients, "Client", Name="NARALABS", ClientID="NB")
    >>> contact1 = api.create(client1, "Contact", Firstname="Jordi", Surname="Puiggené")

    >>> client2 = api.create(clients, "Client", Name="RIDING BYTES", ClientID="RB")
    >>> contact2 = api.create(client2, "Contact", Firstname="Ramon", Surname="Bartl")

    >>> sampletype = api.create(sampletypes, "SampleType", title="Water", Prefix="H2O", MinimumVolume="100 ml")
    >>> samplepoint = api.create(samplepoints, "SamplePoint", title="Lake Nowhere")
    >>> labcontact = api.create(labcontacts, "LabContact", Firstname="Mahatma", Lastname="Ghandi")
    >>> department = api.create(departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(categories, "AnalysisCategory", title="Metals", Department=department)

    >>> Cu = api.create(services, "AnalysisService", title="Copper", Keyword="Cu", Price="10", Category=category)
    >>> Fe = api.create(services, "AnalysisService", title="Iron", Keyword="Fe", Price="20", Category=category)
    >>> Ag = api.create(services, "AnalysisService", title="Silver", Keyword="Ag", Price="30", Category=category)
    >>> Au = api.create(services, "AnalysisService", title="Gold", Keyword="Au", Price="40", Category=category)
    >>> AgAu = api.create(services, "AnalysisService", title="TotalAgAu", Keyword="AgAu", Price="50", Category=category)

    >>> int_Fac = {'keyword': 'Fac', 'title': 'Factor', 'value': 1, 'type': 'int', 'hidden': False, 'unit': ''}

    >>> calc = api.create(calculations, "Calculation", title="Calculation")
    >>> calc.setInterimFields([int_Fac])
    >>> calc.setFormula("([Au] + [Ag]) * [Fac]")
    >>> AgAu.setCalculation(calc)

    >>> uncertainties = [
    ...    {"intercept_min":  0, "intercept_max":  5, "errorvalue": 0.1},
    ...    {"intercept_min":  5, "intercept_max": 10, "errorvalue": 0.2},
    ...    {"intercept_min": 10, "intercept_max": 20, "errorvalue": 0.3},
    ... ]
    >>> AgAu.setUncertainties(uncertainties)

    >>> SAMPLEDATA1 = {
    ...     "client": client1,
    ...     "contact": contact1,
    ...     "sampletype": sampletype,
    ...     "samplepoint": samplepoint,
    ...     "calculation": calc,
    ...     "services": [Cu, Fe, Ag, Au, AgAu],
    ... }


Check Analyses
--------------

Create a new sample:

    >>> sample = new_sample(**SAMPLEDATA1)
    >>> api.get_workflow_status_of(sample)
    'sample_due'

Check fields and methods:

    >>> service = AgAu
    >>> keyword = service.getKeyword()

    >>> analysis = get_analysis_by_keyword(sample, keyword)

    >>> analysis.Title() == analysis.getAnalysisService().Title()
    True

    >>> analysis.getAnalysisService() == service
    True

    >>> analysis.getKeyword() == analysis.getAnalysisService().getKeyword()
    True

    >>> analysis.getRequest() == sample
    True

    >>> analysis.getRequestID() == sample.getId()
    True

    >>> analysis.isSampleReceived()
    False

    >>> analysis.getHidden()
    False

    >>> analysis.getPrice() == service.getPrice()
    True

    >>> analysis.getClient() == SAMPLEDATA1.get("client")
    True

    >>> analysis.getSampleType() == SAMPLEDATA1.get("sampletype")
    True

    >>> analysis.getSamplePoint() == SAMPLEDATA1.get("samplepoint")
    True

    >>> analysis.getCalculation() == SAMPLEDATA1.get("calculation")
    True

    >>> analysis.getCalculation().getFormula()
    '([Au] + [Ag]) * [Fac]'

    >>> deps = analysis.getDependencies()
    >>> sorted(map(lambda d: d.getKeyword(), deps))
    ['Ag', 'Au']


Receive the sample:

    >>> try_transition(sample, "receive", "sample_received")
    True

    >>> list(sorted(set(map(api.get_workflow_status_of, sample.getAnalyses()))))
    ['unassigned']


Test results capturing:

    >>> analysis.getResult()
    ''

    >>> analysis.setInterimValue("Fac", 2)

    >>> ag = get_analysis_by_keyword(sample, "Ag")
    >>> ag.setResult(2.5)

    >>> au = get_analysis_by_keyword(sample, "Au")
    >>> au.setResult(1.5)

    >>> analysis.calculateResult()
    True

    >>> analysis.getResult()
    '8.0'

    >>> analysis.getUncertainty()
    '0.2'


    >>> try_transition(analysis, "submit", "to_be_verified")
    True

    >>> try_transition(analysis, "verify", "verified")
    True
