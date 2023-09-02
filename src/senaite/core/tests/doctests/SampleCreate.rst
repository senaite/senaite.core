Sample creation
---------------

Integration test for sample analyses and to measure the performance of the
sample creation process.


Running this test from the buildout directory::

    bin/test test_textual_doctests -t SampleCreate


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
    >>> setup.setAutoreceiveSamples(True)

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

    >>> container1 = api.create(setup.sample_containers, "SampleContainer", title="Glass Bottle", Capacity="500ml")
    >>> container2 = api.create(setup.sample_containers, "SampleContainer", title="Plastic Bottle", Capacity="500ml")

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


Sample create performance
-------------------------

Measure sample create performance of samples:

    >>> from cProfile import Profile
    >>> from time import time

    >>> samples = []
    >>> start = time()

    >>> def create_test_samples():
    ...     for x in range(10):
    ...         s = new_sample(**SAMPLEDATA1)
    ...         samples.append(s)

    >>> prof = Profile()
    >>> rval = prof.runcall(create_test_samples)
    >>> prof.dump_stats("/tmp/create_samples.prof")
    >>> end = time()

    >>> total = "%.2f" % (end - start)
    >>> total

Check if all samples were created:

    >>> len(samples)
    10

    >>> map(api.get_id, samples)
    ['H2O-0001', 'H2O-0002', 'H2O-0003', 'H2O-0004', 'H2O-0005', 'H2O-0006', 'H2O-0007', 'H2O-0008', 'H2O-0009', 'H2O-0010']

Check if all analyses were created:

    >>> uc = api.get_tool("uid_catalog")
    >>> results = uc({"portal_type": "Analysis"})
    >>> len(results)
    50
