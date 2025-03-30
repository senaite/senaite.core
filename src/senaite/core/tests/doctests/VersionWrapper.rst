Version Wrapper
---------------

An adapter that can wrap any content and provide versioned attributes

Running this test from the buildout directory::

    bin/test test_textual_doctests -t VersionWrapper


Test Setup
..........

Needed Imports:

    >>> from bika.lims import api
    >>> from bika.lims.api.snapshot import *
    >>> from senaite.core.interfaces import IVersionWrapper
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from DateTime import DateTime
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD
    >>> from zope.lifecycleevent import modified
    >>> from zope.event import notify


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

    >>> def receive_sample(sample):
    ...     do_action_for(sample, "receive")

    >>> def get_analysis(sample, id):
    ...     ans = sample.getAnalyses(getId=id, full_objects=True)
    ...     if len(ans) != 1:
    ...         return None
    ...     return ans[0]

    >>> def notify_edited(content):
    ...     if api.is_at_content(content):
    ...         content.processForm()
    ...     elif api.is_dexterity_content(content):
    ...         modified(content)


Environment Setup
.................

Setup the testing environment:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup
    >>> bikasetup = portal.bika_setup
    >>> date_now = DateTime().strftime("%Y-%m-%d")
    >>> date_future = (DateTime() + 5).strftime("%Y-%m-%d")
    >>> setRoles(portal, TEST_USER_ID, ['LabManager', ])
    >>> user = api.get_current_user()


LIMS Setup
..........

Setup the Lab for testing:

    >>> bikasetup.setSelfVerificationEnabled(True)
    >>> analysisservices = bikasetup.bika_analysisservices
    >>> categories = setup.analysiscategories
    >>> calculations = bikasetup.bika_calculations
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH")
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> labcontact = api.create(bikasetup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.departments, "Department", title="Chemistry", Manager=labcontact)
    >>> sampletype = api.create(setup.sampletypes, "SampleType", title="Water", Prefix="Water")
    >>> category = api.create(categories, "AnalysisCategory", title="Metals", Department=department)


Versionable AT Content Wrapper
..............................

We create an AT Calculation for this test:

    >>> calc = api.create(calculations, "Calculation", title="Total Hardness", Formula="[Ca] + [Mg]")

    >>> api.is_at_content(calc)
    True

The initial version should be 0:

    >>> get_version(calc)
    0

Fetch the version wrapper:

    >>> at_wrapper = IVersionWrapper(calc)

We should have transparent access to the underlying content methods:

    >>> at_wrapper.getFormula()
    '[Ca] + [Mg]'

We can also get the cloned instance:

    >>> at_clone = at_wrapper.get_clone()
    >>> api.get_workflow_status_of(at_clone)
    'active'

Now we change the calculation formula:

    >>> calc.setFormula("([Ca] + [Mg]) * 2")
    >>> notify_edited(calc)

The version should be increased:

    >>> get_version(calc)
    1

Although the changes are reflected by the content itself:

    >>> calc.getFormula()
    '([Ca] + [Mg]) * 2'

The version wrapper retains the previous version:

    >>> at_wrapper.getFormula()
    '[Ca] + [Mg]'

Unless we load the latest version:

    >>> at_wrapper.load_latest_version()

    >>> at_wrapper.getFormula()
    '([Ca] + [Mg]) * 2'

We change it back again to the original value:

    >>> calc.setFormula("[Ca] + [Mg]")
    >>> notify_edited(calc)


Sample Calculaiton
..................

Create some Analysis Services with unique Keywords:

    >>> Ca = api.create(analysisservices, "AnalysisService", title="Calcium", Keyword="Ca", Category=category)
    >>> Mg = api.create(analysisservices, "AnalysisService", title="Magnesium", Keyword="Mg", Category=category)
    >>> TH = api.create(analysisservices, "AnalysisService", title="Total Hardness", Keyword="TH", Calculation=calc)

Create an new Sample:

    >>> sample = new_sample([TH])
    >>> receive_sample(sample)

Get the contained `Cu` Analysis:

    >>> ca = get_analysis(sample, Ca.getKeyword())
    >>> mg = get_analysis(sample, Mg.getKeyword())
    >>> th = get_analysis(sample, TH.getKeyword())

TODO: We need a history aware UID reference field to provide the right version wrapped calculation here:

    >>> th_calc = th.getCalculation()

Get the version on creation:

    >>> th_calc_version = get_version(th_calc)
    >>> th_calc_version
    2

    >>> th_calc_wrapper = IVersionWrapper(th_calc)
    >>> th_calc_wrapper.load_version(th_calc_version)

    >>> th_calc_wrapper.getFormula()
    '[Ca] + [Mg]'

We simulate now a change in the calculation:o

    >>> calc.setTitle("Double Total Hardness")
    >>> calc.setFormula("2 * ([Ca] + [Mg])")
    >>> notify_edited(calc)
    >>> calc.getFormula()
    '2 * ([Ca] + [Mg])'

The version should be bumped:

    >>> get_version(th_calc)
    3

However, the wrapper still contains the previous version:

    >>> th_calc_wrapper.get_version()
    2

And the old title abd formula:

    >>> th_calc_wrapper.Title()
    'Total Hardness'

    >>> th_calc_wrapper.getFormula()
    '[Ca] + [Mg]'


Versionable DX Content Wrapper
..............................

Create a new Dexterity object:

    >>> dept = api.create(setup.departments, "Department", title="Clinical Lab", DepartmentID="CL", Manager=labcontact)

    >>> api.is_dexterity_content(dept)
    True

The initial version should be 0:

    >>> get_version(dept)
    0

Fetch the version wrapper:

    >>> dx_wrapper = IVersionWrapper(dept)

We should have transparent access to the underlying content methods:

    >>> dx_wrapper.getDepartmentID()
    'CL'

Now we change the department ID:

    >>> dept.setDepartmentID("CLab")
    >>> notify_edited(dept)

The version should be increased:

    >>> get_version(dept)
    1

Although the changes are reflected by the content itself:

    >>> dept.getDepartmentID()
    'CLab'

The version wrapper retains the previous version:

    >>> dx_wrapper.getDepartmentID()
    'CL'

Unless we load the latest version:

    >>> dx_wrapper.load_latest_version()

    >>> dx_wrapper.getDepartmentID()
    'CLab'


Values returned by the wrapper match with those from the field
..............................................................

When processing the values of a snapshot, the system tries to match the
value with that required by the field type of the content object. This
principle applies for both AT content types and DX types.

If the value for the field is not set, the system returns `None` as the value
without doing any conversion. For instance, the `SortKey` field from service
does not have a default value set, but the expected type is `float`. When not
set, system returns `None` as the value instead of a `float` type:

    >>> Ca.getSortKey() is None
    True

    >>> wrapper = IVersionWrapper(Ca)
    >>> wrapper.getSortKey() is None
    True

    >>> Ca.setSortKey("23.5")
    >>> notify_edited(Ca)
    >>> Ca.getSortKey()
    23.5

    >>> wrapper.load_latest_version()
    >>> wrapper.getSortKey()
    23.5

Likewise, when a string field has an empty value set instead of a `None` the
system remains consistent with the value from the original object:

    >>> Ca.getShortTitle()
    ''

    >>> wrapper.getShortTitle()
    ''

    >>> Ca.setShortTitle(None)
    >>> notify_edited(Ca)
    >>> Ca.getShortTitle() is None
    True

    >>> wrapper.load_latest_version()
    >>> wrapper.getShortTitle() is None
    True

Other AT-specific field types that are still in use might have special
requirements too. Note these fields will be definitely removed once all
content types are migrated to DX, but we keep them here into account for
legacy and consistency reasons:

- `DurationField` type:

    >>> Ca.getMaxTimeAllowed()
    {'hours': 0, 'minutes': 0, 'days': 5}

    >>> wrapper = IVersionWrapper(Ca)
    >>> wrapper.getMaxTimeAllowed()
    {'hours': 0, 'minutes': 0, 'days': 5}

- `AddressField` type:

    >>> client.getPhysicalAddress()
    {}

    >>> wrapper = IVersionWrapper(client)
    >>> wrapper.getPhysicalAddress()
    {}

    >>> subfields = ["address", "city", "zip", "state", "country"]
    >>> address = {key: "My %s" % key for key in subfields}
    >>> client.setPhysicalAddress(address)
    >>> notify_edited(client)
    >>> sorted(client.getPhysicalAddress().values())
    ['My address', 'My city', 'My country', 'My state', 'My zip']

    >>> wrapper.load_latest_version()
    >>> sorted(wrapper.getPhysicalAddress().values())
    ['My address', 'My city', 'My country', 'My state', 'My zip']

- `EmailsField` type:

    >>> client.getCCEmails()
    ''

    >>> wrapper.getCCEmails()
    ''

- `ARAnalysesField` type:

    >>> sample = new_sample([Ca, Mg])
    >>> receive_sample(sample)
    >>> wrapper = IVersionWrapper(sample)

    >>> analyses = sample.getAnalyses(full_objects=True)
    >>> a_uids = [api.get_uid(an) for an in analyses]

    >>> analyses = wrapper.getAnalyses(full_objects=True)
    >>> w_uids = [api.get_uid(an) for an in analyses]

    >>> sorted(a_uids) == sorted(w_uids)
    True

    >>> analyses = sorted(sample.getRawAnalyses())
    >>> analyses == sorted(wrapper.getRawAnalyses())
    True

- `UIDReferenceField` type:

    >>> sample.getContact() == wrapper.getContact()
    True

    >>> sample.getRawContact() == wrapper.getRawContact()
    True
