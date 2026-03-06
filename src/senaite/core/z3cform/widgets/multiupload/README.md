# MultiUpload Widget

The MultiUpload widget provides a user-friendly interface for uploading multiple files (images or documents) to SENAITE objects. It features drag-and-drop functionality, preview thumbnails, and seamless integration with SENAITE's content types.

## Overview

The widget handles file uploads in two phases:

1. **Upload Phase**: Files are uploaded via AJAX and stored temporarily
2. **Save Phase**: When the form is saved, temporary uploads are converted to permanent File/Image objects

This two-phase approach provides immediate user feedback during uploads while maintaining transaction safety during form submission.

## Architecture

### Components

**Widget (`widget.py`)**
- z3c.form widget for MultiUploadField
- Renders the React-based upload interface
- Manages field data (list of File/Image UIDs)

**Upload Handler (`handler.py`)**
- Browser view: `@@multiupload_handler`
- Accepts AJAX file uploads from the widget
- Stores files temporarily with a unique UUID
- Returns upload metadata to the client

**Temporary Storage (`storage.py`)**
- Cluster-safe ZODB-based storage for uploaded files
- Uses portal annotations with OOBTree for concurrent access
- Self-cleaning: automatically removes expired uploads
- Shared across all ZEO client instances

**Event Subscriber (`subscribers/multiupload.py`)**
- Triggered on object add/modify events
- Converts temporary uploads to permanent File/Image objects
- Handles file deletion when removed from fields
- Cleans up temporary storage after processing

### Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. User uploads file via drag & drop                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. AJAX POST to @@multiupload_handler                      │
│    - File data sent to handler                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Handler stores file in temporary ZODB storage           │
│    - Generates UUID (e.g., "a1b2c3d4-...")                 │
│    - Stores: {filename, content_type, data, timestamp}     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Handler returns UUID to client                          │
│    Response: {"id": "uuid", "filename": "...", ...}        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Widget stores UUID in hidden field                      │
│    - Displayed as preview/thumbnail to user                │
│    - Multiple files = multiple UUIDs                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. User clicks "Save" on form                              │
│    - Form submits with UUIDs + existing File UIDs          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. Event handler processes MultiUploadField fields         │
│    - Retrieves file data from storage by UUID              │
│    - Creates File/Image objects as children                │
│    - Updates field with new File UIDs                      │
│    - Removes temporary uploads from storage                │
└─────────────────────────────────────────────────────────────┘
```

## Usage

### Defining a MultiUpload Field

```python
from senaite.core.schema import MultiUploadField
from zope.interface import Interface

class IMyContent(Interface):
    """My content type schema"""

    attachments = MultiUploadField(
        title=u"Attachments",
        description=u"Upload multiple files or images",
        required=False,
    )
```

### Accessing Uploaded Files

```python
from bika.lims import api

# Get the object
obj = api.get_object(brain_or_uid)

# Get uploaded files (returns list of File/Image objects)
files = obj.attachments

# Iterate through files
for file_obj in files:
    filename = file_obj.file.filename
    content_type = file_obj.file.contentType
    size = file_obj.file.getSize()
    data = file_obj.file.data
```

### Programmatic File Addition

```python
from senaite.core.interfaces import IMultiUploadFileCreator
from zope.component import getMultiAdapter

# Get the field
field = IMyContent["attachments"]

# Get the creator adapter
creator = getMultiAdapter((obj, field), IMultiUploadFileCreator)

# Create a File object
file_obj = creator.create(
    filename=u"document.pdf",
    content_type="application/pdf",
    data=binary_data
)

# Add to field
current = obj.attachments or []
obj.attachments = current + [file_obj]
```

## Temporary Storage

### How It Works

Uploaded files are stored temporarily in a shared ZODB container until the form is saved:

- **Storage Location**: `IAnnotations(portal)["senaite.core.multiupload.storage"]`
- **Structure**: OOBTree with UUID keys
- **Expiration**: 2 hours (default)
- **Self-Cleaning**: Every 100 operations

### Cluster Safety

The storage is designed for clustered environments:

- **Shared via ZEO**: All instances access the same ZODB container
- **Concurrent Safe**: OOBTree handles concurrent writes with ZODB conflict resolution
- **No Sticky Sessions**: Uploads and form saves can hit different instances

### Concurrency Model

Multiple users can upload simultaneously without conflicts:

```python
# User A uploads
container["uuid-a"] = UploadRecord(...)  # Stored

# User B uploads (concurrent)
container["uuid-b"] = UploadRecord(...)  # Stored

# No conflict: Different keys, OOBTree merges automatically
```

### Self-Cleaning

Inspired by `plone.memoize.CleanupDict`:

1. Counter increments on each `store()` operation
2. Every 100 operations, cleanup runs automatically
3. Uploads older than 2 hours are removed
4. Counter resets after cleanup

## Configuration

### Storage Settings

Edit `storage.py` to adjust:

```python
# Maximum age before uploads are removed (seconds)
DEFAULT_EXPIRATION_SECONDS = 7200  # 2 hours

# Operations between automatic cleanups
CLEANUP_INTERVAL = 100
```

### Manual Cleanup

Trigger cleanup programmatically:

```python
from senaite.core.z3cform.widgets.multiupload.storage import get_storage

storage = get_storage()
removed = storage.cleanup(max_age_seconds=3600)  # 1 hour
logger.info("Removed {} expired uploads".format(removed))
```

### Monitoring

Check instance logs for storage activity:

```
INFO: Stored upload a1b2c3d4-... for file report.pdf (51234 bytes)
INFO: Auto-cleanup triggered after 100 operations
INFO: Cleaned up 5 expired upload(s)
INFO: Removed upload a1b2c3d4-...
WARNING: Upload e5f6g7h8-... not found in storage
```

## Troubleshooting

### Files Not Appearing After Upload

**Symptom**: Files upload successfully but don't appear on the object after save.

**Possible Causes**:
1. Upload UUID not found in storage
2. Event handler not triggered
3. Field not properly configured

**Debug Steps**:
```python
# Check storage contents
from senaite.core.z3cform.widgets.multiupload.storage import get_storage

storage = get_storage()
container = storage._get_container()
print("Uploads in storage:", len(container))
print("UUIDs:", list(container.keys()))

# Check if file data exists
file_data = storage.retrieve("uuid-here")
print("File data:", file_data)
```

### High Memory Usage

**Symptom**: Instance memory grows significantly.

**Possible Causes**:
1. Large files stored in memory
2. Cleanup not running
3. Many expired uploads not removed

**Solutions**:
```python
# Force cleanup
storage = get_storage()
removed = storage.cleanup(max_age_seconds=1800)  # 30 minutes

# Check container size
container = storage._get_container()
total_size = sum(
    len(record.data) for record in container.values()
)
print("Storage size: {} MB".format(total_size / 1024 / 1024))
```

### ZODB Conflict Errors

**Symptom**: ConflictError in logs during high upload volume.

**Expected Behavior**: ZODB automatically retries conflicted transactions (up to 3 times).

**If Persistent**:
- Check that CLEANUP_INTERVAL isn't too low (increases writes)
- Verify OOBTree is used (not regular dict)
- Review concurrent upload patterns

## API Reference

### Storage API

```python
from senaite.core.z3cform.widgets.multiupload.storage import get_storage

storage = get_storage(context=None)

# Store upload
success = storage.store(
    upload_id="uuid",
    filename=u"file.pdf",
    content_type="application/pdf",
    data=binary_data
)

# Retrieve upload
file_data = storage.retrieve("uuid")
# Returns: {"filename": "...", "content_type": "...",
#           "data": b"...", "timestamp": 123456789}

# Remove upload
removed = storage.remove("uuid")

# Cleanup expired uploads
count = storage.cleanup(max_age_seconds=7200)
```

### Handler API

```python
# AJAX POST to @@multiupload_handler
# Content-Type: multipart/form-data

# Response:
{
    "id": "uuid-string",
    "filename": "document.pdf",
    "content_type": "application/pdf",
    "size": 51234,
    "status": "success"
}
```

## Development

### Running Tests

Run the comprehensive doctest for MultiUploadField:

```bash
bin/test-senaite -t MultiUploadField
```

This test covers:
- Temporary upload storage operations
- File upload simulation
- File/Image creation from uploads
- Storage cleanup after processing
- Field validation
- File deletion via adapter

### Adding Custom File Types

Implement `IMultiUploadFileCreator` adapter:

```python
from senaite.core.interfaces import IMultiUploadFileCreator
from zope.component import adapter
from zope.interface import implementer

@implementer(IMultiUploadFileCreator)
@adapter(IMyContent, IMultiUploadField)
class MyFileCreator(object):

    def __init__(self, context, field):
        self.context = context
        self.field = field

    def create(self, filename, content_type, data):
        # Custom File/Image creation logic
        file_id = self.generate_id(filename)
        self.context.invokeFactory("File", file_id)
        file_obj = self.context[file_id]
        file_obj.file = NamedBlobFile(
            data=data,
            filename=filename,
            contentType=content_type
        )
        return file_obj
```

### Extending Storage

Subclass `TemporaryUploadStorage` for custom behavior:

```python
from senaite.core.z3cform.widgets.multiupload.storage import (
    TemporaryUploadStorage
)

class MyCustomStorage(TemporaryUploadStorage):

    def store(self, upload_id, filename, content_type, data):
        # Custom validation
        if len(data) > 10 * 1024 * 1024:  # 10MB
            logger.error("File too large: {}".format(filename))
            return False

        # Call parent implementation
        return super(MyCustomStorage, self).store(
            upload_id, filename, content_type, data
        )
```

## License

This is part of SENAITE.CORE and is licensed under GPLv2.
