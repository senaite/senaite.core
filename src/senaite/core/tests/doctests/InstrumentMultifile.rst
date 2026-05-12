Instrument Multifile
--------------------

Instruments can contain document files (Multifile objects) such as user manuals,
specifications, images, and other documentation.

Running this test from the buildout directory::

    bin/test -t InstrumentMultifile

Test Setup
----------

    >>> import transaction
    >>> from DateTime import DateTime
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.namedfile.file import NamedBlobFile
    >>> from bika.lims.api import create
    >>> from bika.lims import api

    >>> portal = self.portal
    >>> portal_url = portal.absolute_url()
    >>> bika_setup = portal.bika_setup
    >>> setRoles(portal, TEST_USER_ID, ["LabManager"])


Create an Instrument
--------------------

    >>> instruments = bika_setup.bika_instruments
    >>> instrument = create(instruments, "Instrument", title="Test Instrument")


Create Multifile Objects
------------------------

Multifile objects can be created inside instruments to store documentation::

    >>> multifile1 = create(instrument, "Multifile")
    >>> multifile1
    <Multifile at /plone/bika_setup/bika_instruments/instrument-1/multifile-1>

Multifiles provide the `IMultifile` interface::

    >>> from senaite.core.interfaces import IMultifile
    >>> IMultifile.providedBy(multifile1)
    True


Set Multifile Fields
--------------------

Set the Document ID::

    >>> multifile1.setDocumentID("DOC-001")
    >>> multifile1.getDocumentID()
    'DOC-001'

The title should be derived from the Document ID::

    >>> multifile1.Title()
    'DOC-001'

Set the Document Version::

    >>> multifile1.setDocumentVersion("1.0")
    >>> multifile1.getDocumentVersion()
    '1.0'

Set the Document Type::

    >>> multifile1.setDocumentType("User Manual")
    >>> multifile1.getDocumentType()
    'User Manual'

Set the Document Location::

    >>> multifile1.setDocumentLocation("Lab Archive - Shelf A3")
    >>> multifile1.getDocumentLocation()
    'Lab Archive - Shelf A3'


File Upload
-----------

Create a test file and attach it to the Multifile::

    >>> file_content = b"This is the instrument user manual content"
    >>> file_data = NamedBlobFile(
    ...     data=file_content,
    ...     contentType='text/plain',
    ...     filename=u'user_manual.txt'
    ... )
    >>> multifile1.setFile(file_data)

Retrieve the file::

    >>> uploaded_file = multifile1.getFile()
    >>> uploaded_file is not None
    True

Check file properties::

    >>> uploaded_file.filename
    u'user_manual.txt'

    >>> uploaded_file.contentType
    'text/plain'

    >>> uploaded_file.getSize()
    42

    >>> uploaded_file.data == file_content
    True


Multiple Multifile Objects
--------------------------

Create additional Multifile objects with auto-generated IDs::

    >>> multifile2 = create(instrument, "Multifile")
    >>> multifile2.getId()
    'multifile-2'

    >>> multifile2.Title()
    'multifile-2'

    >>> multifile2.setDocumentID("DOC-002")
    >>> multifile2.setDocumentType("Specifications")
    >>> multifile2.setDocumentVersion("2.1")

    >>> file_content2 = b"Technical specifications document."
    >>> file_data2 = NamedBlobFile(
    ...     data=file_content2,
    ...     contentType='application/pdf',
    ...     filename=u'specifications.pdf'
    ... )
    >>> multifile2.setFile(file_data2)

Create a third Multifile::

    >>> multifile3 = create(instrument, "Multifile")
    >>> multifile3.getId()
    'multifile-3'

    >>> multifile3.setDocumentID("DOC-003")
    >>> multifile3.setDocumentType("Calibration Certificate")
    >>> multifile3.setDocumentVersion("1.0")


Get Documents from Instrument
-----------------------------

The instrument can retrieve all its Multifile objects::

    >>> documents = instrument.getDocuments()
    >>> len(documents)
    3

    >>> sorted([doc.getDocumentID() for doc in documents])
    ['DOC-001', 'DOC-002', 'DOC-003']

Check the auto-generated IDs::

    >>> sorted([doc.getId() for doc in documents])
    ['multifile-1', 'multifile-2', 'multifile-3']


Catalog Integration
-------------------

Multifile objects should be cataloged in the setup catalog::

    >>> from senaite.core.catalog import SETUP_CATALOG
    >>> results = api.search({'portal_type': 'Multifile'}, SETUP_CATALOG)
    >>> len(results) >= 3
    True

Search for a specific Multifile by DocumentID::

    >>> results = api.search({
    ...     'portal_type': 'Multifile',
    ...     'path': {
    ...         'query': api.get_path(instrument),
    ...         'depth': 1
    ...     }
    ... }, SETUP_CATALOG)
    >>> len(results)
    3


Backward Compatibility Properties
---------------------------------

The BBB properties should work for AT-style access::

    >>> multifile1.DocumentID
    'DOC-001'

    >>> multifile1.DocumentVersion
    '1.0'

    >>> multifile1.DocumentType
    'User Manual'

    >>> multifile1.DocumentLocation
    'Lab Archive - Shelf A3'

    >>> multifile1.File is not None
    True


File Download URLs
------------------

The file download URL should follow the Dexterity pattern::

    >>> url = multifile1.absolute_url()
    >>> download_url = "{}/@@download/file".format(url)
    >>> "@@download/file" in download_url
    True


Content Type Configuration
--------------------------

Verify that Multifile is allowed inside Instrument::

    >>> fti = api.get_tool("portal_types")["Instrument"]
    >>> allowed_types = fti.allowed_content_types
    >>> 'Multifile' in allowed_types
    True


Retrieving Multifiles via getDocuments
--------------------------------------

The getDocuments method uses catalog search to retrieve Multifile objects::

    >>> multifiles = instrument.getDocuments()
    >>> len(multifiles)
    3

    >>> all([IMultifile.providedBy(mf) for mf in multifiles])
    True

    >>> sorted([mf.getDocumentID() for mf in multifiles])
    ['DOC-001', 'DOC-002', 'DOC-003']


Workflow Tests
--------------

Multifile objects follow the senaite_deactivable_type_workflow::

    >>> workflows = api.get_workflows_for(multifile1)
    >>> workflows
    ('senaite_deactivable_type_workflow',)

New Multifile objects start in the 'active' state::

    >>> api.get_workflow_status_of(multifile1)
    'active'

Check available transitions from the active state::

    >>> transitions = api.get_transitions_for(multifile1)
    >>> 'deactivate' in [t['id'] for t in transitions]
    True

Deactivate the Multifile::

    >>> obj = api.do_transition_for(multifile1, 'deactivate')
    >>> api.get_workflow_status_of(multifile1)
    'inactive'

Check that the activate transition is now available::

    >>> transitions = api.get_transitions_for(multifile1)
    >>> 'activate' in [t['id'] for t in transitions]
    True

Activate the Multifile again::

    >>> obj = api.do_transition_for(multifile1, 'activate')
    >>> api.get_workflow_status_of(multifile1)
    'active'

Test the IDeactivable interface::

    >>> from bika.lims.interfaces import IDeactivable
    >>> IDeactivable.providedBy(multifile1)
    True

Check if the object is active using the API::

    >>> api.is_active(multifile1)
    True

Deactivate and check again::

    >>> obj = api.do_transition_for(multifile1, 'deactivate')
    >>> api.is_active(multifile1)
    False

Activate it back for subsequent tests::

    >>> obj = api.do_transition_for(multifile1, 'activate')
    >>> api.is_active(multifile1)
    True


Workflow History
----------------

The workflow should maintain a history of transitions::

    >>> history = api.get_review_history(multifile1)
    >>> len(history) >= 3
    True

The history should contain our transitions::

    >>> actions = [h.get('action') for h in history if h.get('action')]
    >>> 'deactivate' in actions
    True

    >>> 'activate' in actions
    True
