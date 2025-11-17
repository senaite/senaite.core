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
-------------------------

Multifile objects can be created inside instruments to store documentation::

    >>> multifile1 = create(instrument, "Multifile")
    >>> multifile1
    <Multifile at /plone/bika_setup/bika_instruments/instrument-1/multifile-1>

Multifiles provide the `IMultifile` interface::

    >>> from senaite.core.interfaces import IMultifile
    >>> IMultifile.providedBy(multifile1)
    True


Set Multifile Fields
---------------------

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
---------------------------

Create additional Multifile objects with auto-generated IDs::

    >>> multifile2 = create(instrument, "Multifile")
    >>> multifile2.getId()
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
------------------------------

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
----------------------------------

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
---------------------------

Verify that Multifile is allowed inside Instrument::

    >>> fti = api.get_tool("portal_types")["Instrument"]
    >>> allowed_types = fti.allowed_content_types
    >>> 'Multifile' in allowed_types
    True


Object Values
-------------

The objectValues method should work correctly::

    >>> multifiles = instrument.objectValues('Multifile')
    >>> len(multifiles)
    3

    >>> all([IMultifile.providedBy(mf) for mf in multifiles])
    True
