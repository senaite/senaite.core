# Data Grid Widget

A Custom version of `collective.z3cform.datagridfield`:

- https://pypi.org/project/collective.z3cform.datagridfield
- https://github.com/collective/collective.z3cform.datagridfield


## Description

The widget basically maintains a list of dictionaries, aka. a records field.
In SENAITE, we use `senaite.core.schema.fields.DataGridField` for this, which is
a sub-class of a standard `zope.schema.List` field.
The rows are defined as a `DataGridRow` in the `value_type` of the field, where
the schema of each row is defined by an interface definition.


## Usage

The DGF is defined in the schema interface of the content type:

```python
from plone.autoform import directives
from plone.namedfile.field import NamedBlobFile
from plone.supermodel import model
from senaite.core import senaiteMessageFactory as _
from senaite.core.schema.fields import DataGridField
from senaite.core.schema.fields import DataGridRow
from senaite.core.z3cform.widgets.datagrid import DataGridRowFileWidget
from senaite.core.z3cform.widgets.datagrid import DataGridWidget
from zope import schema
from zope.interface import Interface


class ICertificateRecord(Interface):
    """Record schema of the DGF
    """

    title = schema.TextLine(title=u"Title", required=False)
    directives.widget("certificate", DataGridRowFileWidget)
    certificate = NamedBlobFile(
        title=_(
            u"title_certificate_file",
            default=u"Certificate File"
        ),
        description=_(
            u"description_certificate_file",
            default=u""
        ),
        required=True,
    )


class ITracerSchema(model.Schema):
    """Content fields
    """

    directives.widget("certificates", DataGridWidget, allow_insert=False, allow_reorder=True)
    certificates = DataGridField(
        title=_(
            u"title_tracer_certificates",
            default=u"Certificates"
        ),
        description=_(
            u"description_tracer_certificates",
            default=u"Assigned certificates for this tracer"
        ),
        value_type=DataGridRow(schema=ICertificateRecord),
        required=False,
        missing_value=[],
    )
```


## Handle files in records

To allow files in a Data Grid Row, the custom `DataGridRowFileWidget` must be used.
This widget ensures that files are correctly handled and updated.

💡 Tip:

It is also possible to download these files directly from the field itself, by

```
..content/++field++certificates/@@download/0/certificate
```

where `certificates` is the DGF, the `0` is the row to select and `certificate`
is the schema field where that handles the file.


☝️ Note:

When using files in a Data Grid Row, the DGF must be configured with
`allow_insert=False` (see example above).


## TODO

- Fix behavior for `allow_insert=True` when using file rows

  Currently, the Data Grid Widget adds a `+` button for each row when it is
  configured with `allow_insert=True`. This button adds a new row directly below
  the row where the button was clicked.

  However, the new row is a copy of the template row and the input fields have
  all the same name (containing a `TT` in the name), which causes the files that
  were added to these rows to be submitted as a list.

