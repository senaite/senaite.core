MultiUploadField
================

MultiUploadField is a field that allows multiple file uploads to be attached
to a content object. Files are stored as separate File or Image objects within
the container, and their UIDs are stored in the field.

This test covers the complete upload workflow including the cluster-safe
temporary storage mechanism that allows uploads to be shared across multiple
ZEO client instances.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t MultiUploadField


Needed Imports
--------------

    >>> import json
    >>> import transaction
    >>> from bika.lims import api
    >>> from plone.namedfile.file import NamedBlobFile
    >>> from plone.namedfile.file import NamedBlobImage
    >>> from senaite.core.schema import MultiUploadField
    >>> from zope.interface import Interface
    >>> from zope.interface import implementer


Variables
---------

    >>> portal = self.portal
    >>> request = self.request


Test User
---------

We need certain permissions to create and access objects used in this test,
so here we will assume the role of Lab Manager.

    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> setRoles(portal, TEST_USER_ID, ["LabManager"])


Test Content Type
-----------------

First, let's create a simple test content type with a MultiUploadField:

    >>> from plone.dexterity.content import Container
    >>> from plone.dexterity.fti import DexterityFTI
    >>> from zope import schema as zschema

    >>> @implementer(Interface)
    ... class ITestDocument(Interface):
    ...     """Test document interface"""
    ...     attachments = MultiUploadField(
    ...         title=u"Attachments",
    ...         required=False,
    ...     )

    >>> from plone.dexterity.content import Container
    >>> class TestDocument(Container):
    ...     """Test document"""
    ...     pass



Field Behavior
--------------

Test that the MultiUploadField stores UIDs correctly:

    >>> field = MultiUploadField(title=u"Test Field")
    >>> field.__name__ = "test_field"


Creating a Test Document
------------------------

Create a client to hold test documents:

    >>> clients = portal.clients
    >>> client = api.create(clients, "Client", title="Test Client")
    >>> client_path = api.get_path(client)


Testing Temporary Upload Storage
--------------------------------

Before simulating file uploads, let's test the storage directly:

    >>> from senaite.core.z3cform.widgets.multiupload.storage import get_storage

    >>> storage = get_storage()

Store a test upload:

    >>> test_data = b"Test data for storage"
    >>> success = storage.store(
    ...     "test-storage-uuid",
    ...     u"test.txt",
    ...     "text/plain",
    ...     test_data
    ... )
    >>> success
    True

    >>> transaction.commit()

Retrieve the upload:

    >>> retrieved = storage.retrieve("test-storage-uuid")
    >>> retrieved["filename"]
    u'test.txt'

    >>> retrieved["content_type"]
    'text/plain'

    >>> retrieved["data"] == test_data
    True

    >>> "timestamp" in retrieved
    True

Remove the upload:

    >>> removed = storage.remove("test-storage-uuid")
    >>> removed
    True

Verify it's gone:

    >>> storage.retrieve("test-storage-uuid") is None
    True

Attempt to retrieve non-existent upload:

    >>> storage.retrieve("non-existent-uuid") is None
    True


Simulating File Upload
----------------------

Let's simulate the file upload process:

1. Create some test file data:

    >>> file_data_1 = b"This is test file 1"
    >>> file_data_2 = b"This is test file 2"
    >>> file_data_3 = b"PNG image data here"


2. Store files in shared ZODB storage (simulating upload handler):

    >>> from senaite.core.z3cform.widgets.multiupload.storage import get_storage

    >>> storage = get_storage()

    >>> upload_uuid_1 = "test-uuid-1"
    >>> upload_uuid_2 = "test-uuid-2"
    >>> upload_uuid_3 = "test-uuid-3"

Store each upload in the shared storage:

    >>> storage.store(upload_uuid_1, u"test1.txt", "text/plain", file_data_1)
    True

    >>> storage.store(upload_uuid_2, u"test2.txt", "text/plain", file_data_2)
    True

    >>> storage.store(upload_uuid_3, u"test3.png", "image/png", file_data_3)
    True

Commit the transaction so the storage is persisted:

    >>> transaction.commit()


3. Simulate form submission with upload UUIDs:

    >>> request.form["attachments.data"] = json.dumps([
    ...     upload_uuid_1,
    ...     upload_uuid_2,
    ...     upload_uuid_3,
    ... ])


4. Manually create File/Image objects (normally done by subscriber):

    >>> from senaite.core.interfaces import IMultiUploadFileCreator
    >>> from zope.component import getMultiAdapter

Let's create the files using the adapter and retrieve from storage:

    >>> created_uids = []
    >>> for upload_uuid in [upload_uuid_1, upload_uuid_2, upload_uuid_3]:
    ...     # Retrieve file data from shared storage
    ...     file_data_dict = storage.retrieve(upload_uuid)
    ...     filename = file_data_dict["filename"]
    ...     content_type = file_data_dict["content_type"]
    ...     data = file_data_dict["data"]
    ...
    ...     # Determine if image or file
    ...     is_image = content_type.startswith("image/")
    ...     portal_type = "SimpleImage" if is_image else "SimpleFile"
    ...
    ...     # Create the file/image object
    ...     if is_image:
    ...         blob = NamedBlobImage(
    ...             data=data,
    ...             filename=filename,
    ...             contentType=content_type
    ...         )
    ...         obj = api.create(client, portal_type, title=filename, image=blob)
    ...     else:
    ...         blob = NamedBlobFile(
    ...             data=data,
    ...             filename=filename,
    ...             contentType=content_type
    ...         )
    ...         obj = api.create(client, portal_type, title=filename, file=blob)
    ...
    ...     created_uids.append(api.get_uid(obj))
    ...
    ...     # Clean up storage after creating the file
    ...     removed = storage.remove(upload_uuid)

    >>> len(created_uids)
    3

Verify uploads were removed from storage after processing:

    >>> storage.retrieve(upload_uuid_1) is None
    True

    >>> storage.retrieve(upload_uuid_2) is None
    True

    >>> storage.retrieve(upload_uuid_3) is None
    True


5. Set the field value with the created UIDs:

    >>> client.attachments = created_uids
    >>> client.reindexObject()
    >>> transaction.commit()


Verify Files Were Created
-------------------------

Check that files exist in the document:

    >>> len(client.objectIds())
    3

Check the portal types:

    >>> types = [api.get_portal_type(api.get_object(uid)) for uid in created_uids]
    >>> types.sort()
    >>> types
    ['SimpleFile', 'SimpleFile', 'SimpleImage']


Retrieve Files from Field
-------------------------

    >>> retrieved_uids = client.attachments
    >>> len(retrieved_uids)
    3

    >>> retrieved_uids == created_uids
    True


Get File Objects
----------------

    >>> files = [api.get_object(uid) for uid in retrieved_uids]
    >>> len(files)
    3

Check file titles:

    >>> titles = [api.get_title(f) for f in files]
    >>> titles.sort()
    >>> titles
    ['test1.txt', 'test2.txt', 'test3.png']


Download URLs
-------------

Test that we can get proper download URLs:

    >>> from senaite.core.z3cform.widgets.multiupload.widget import MultiUploadWidget
    >>> widget = MultiUploadWidget(request)

For SimpleFiles:

    >>> file_obj = [f for f in files if api.get_portal_type(f) == "SimpleFile"][0]
    >>> file_url = widget.get_download_url(file_obj)
    >>> "@@download/file" in file_url
    True

For SimpleImages:

    >>> image_obj = [f for f in files if api.get_portal_type(f) == "SimpleImage"][0]
    >>> image_url = widget.get_download_url(image_obj)
    >>> "@@download/image" in image_url
    True


File Deletion
-------------

Test that removing a UID from the field allows for file deletion:

    >>> original_count = len(client.attachments)
    >>> original_count
    3

Remove the first UID:

    >>> uid_to_remove = created_uids[0]
    >>> remaining_uids = [uid for uid in created_uids if uid != uid_to_remove]
    >>> client.attachments = remaining_uids
    >>> len(client.attachments)
    2

The file object still exists (deletion happens via adapter in subscriber):

    >>> obj_to_remove = api.get_object(uid_to_remove)
    >>> api.get_title(obj_to_remove)
    'test1.txt'

Simulate deletion via adapter:

    >>> from senaite.core.interfaces import IMultiUploadFileRemover
    >>> from zope.component import getAdapter
    >>> remover = getAdapter(client, IMultiUploadFileRemover)
    >>> obj_id = obj_to_remove.getId()
    >>> obj_id in client.objectIds()
    True

    >>> remover.remove([uid_to_remove])

Verify the file was deleted:

    >>> obj_id in client.objectIds()
    False

Verify the field still has the remaining files:

    >>> len(client.attachments)
    2


Field Validation
----------------

The field should accept a list of UIDs:

    >>> field.validate(created_uids[:2])

The field should accept an empty list:

    >>> field.validate([])

The field should validate strings (UIDs):

    >>> field.validate([api.get_uid(client)])


Widget Add Form Detection
-------------------------

Test the is_add_form method:

    >>> from z3c.form.interfaces import IAddForm
    >>> from zope.interface import alsoProvides

Create a mock form:

    >>> class MockForm(object):
    ...     pass

    >>> add_form = MockForm()
    >>> alsoProvides(add_form, IAddForm)

    >>> widget = MultiUploadWidget(request)
    >>> widget.form = add_form
    >>> widget.is_add_form()
    True

    >>> edit_form = MockForm()
    >>> widget.form = edit_form
    >>> widget.is_add_form()
    False
