# Data Manager

A data manager is an adapter that knows how to `get`, `query` and `set` named
values on the adapted context.

The original idea was adopted from `z3c.form.interfaces.IDataManager`.

However, instead of adapting the `context` and the `field`, we used in the
initial implementation only the `context` and looked up the fields by their
`name` to set the value.


## Why not adapt the field?

We use `IDataManager` in `senaite.app.listing` to update editable fields in
listings from the asynchronous `save_queue`.

This was done mainly to handle interim fields on Analyses, because we get there
just the name of the column to update, but not the field name where it initially
came from.

Another example is the Batchbook, where the context is a sample and the analysis
results are shown in columns, e.g. like the transposed view in worksheets.

Therefore, the data manager knows that we have to lookup an Analysis by the
given name instead of a field.


## Extending the functionality for fields

We would like to adopt this approach to refactor the logic from AT based fields into
context aware adapters.

To achieve this, we need an `IDataManager` multi-adapter that adapts the following:

- `context`: The actual owner of the field we want to set, e.g. `AnalysisRequest`
- `request`: The current request to allow easy overriding with a browser layer
- `field`: The interface of the field that is adapted

Furthermore, we want to have a `name` in case we want to have different adapter
implementation for e.g. `ITextField` on the same context.
