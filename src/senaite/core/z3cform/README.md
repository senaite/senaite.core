# SENAITE Widgets

This package contains widgets for Dexterity fields.

A widget is redered as HTML element for input, display and hidden modes.
It is not bound to a sepecific field and needs just a request to be created.

However, in SENAITE we often define a specific field for a widget and provide
only for this field a factory function.

## When to define an explicit field

Some attributes make more sense to keep them on field level, e.g. in the
`UIDReferenceField` we like to define if it is multi-valued or in the `IntField`
we define the min/max values.

One of the reasons is that the field setter might be also called from the JSON
API and must be validated before being set.
