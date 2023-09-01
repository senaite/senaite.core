# Synopsis

The query select widget allows the user to select one or more result values from
a catalog search or write an own value to the field.

The widget UI is implemented as a ReactJS component that is located here:

    senaite.core/webpack/app/widgets/queryselect/widget.js

This ReactJS component is initialized with `data-` attributes set in the
`input.pt` template. This is the main interface between the Python widget class
and the ReactJS UI component!

This widget uses the same ReactJS component as the `UIDReferenceWidget` and
shares therefore many similarities in the functionality.

The main difference between the `UIDReferenceWidget` and the `QuerySelectWidget`
is that the latter stores any text value instead of the UID only.


# Usage

The widget can be assigned to a field with the `diretives.widget` schema directive:

    >>> from plone.autoform import directives
    >>> from senaite.core.z3cform.widgets.queryselect import QuerySelectWidgetFactory
    >>> from zope import schema

    directives.widget("query_field", QuerySelectWidgetFactory)
    query_field = schema.TextLine(title="Query Select Field")


## Widget settings

To customize the widget behavior, the following settings can be passed to the
widget directive as *additional arguments*:

- `name`: The name of the submitted field.
          Default: Field name, e.g. `form.widgets.field_query`
          
- `id`: The element ID for the rendered widget.
        Default: Hyphenated field name, e.g. `form-widgets-query_field`

- `api_url`: The JSON API base URL to use.
             Default: `<portal_url>/@@API/senaite/v1`
             Note: A `search` endpoint is called for searches on the base URL!

- `values`: Stored value
            Default: Current stored value of the field

- `value_key`: The result item key where the value is looked up.
               Default: `uid`
               Note: This key must exist for each item in the JSON API response.

- `query`: The base catalog query to use.
           Default: `{}`
           Note: A class method name can be defined to compute the query on access.

- `catalog`: The catalog to use for the query.
             Default: `uid_catalog`


- `search_index`: The search index to use for the catalog query.
                  Default: `q` (recognized by `senaite.jsonapi`)
                  Note: The search_index should be a `ZCTextIndex`

- `search_wildcard`: If a `*` should be appended automatically to the search term.
                     Default: `True`

- `allow_user_value`: If the user can enter a custom value to the field.
                      Default: `False`

- `columns`: The columns to display for the search results dropdown table.
             Default: `[]`
             Note: A Column definition is a dictionary with the following keys:
                   - `name`: Refers to the key in the JSON result item
                   - `label`: Translated column label
                   - `aling`: Text alignment: `left`, `right`, `center`
                   - `width`: Width in percent, e.g. `70`

- `display_template`: Template to use for a selected value.
                      Default: `None`
                      Note: For the `QuerySelectWidget` the plain `value` is used.

- `limit`: Defines the displayed items on one result page.
           Default: `25`

- `multi_valued`: If more than one value can be selected
                  Default: `False`
                  Note: `List` field required if multiple values are allowed!

- `disabled`: Controls if the field should be `disabled` per default.
              Default: `False`

- `readonly`: Controls if the field should be `readonly` per default.
              Default: `False`

- `padding`: Defines how many pages before and after the current page should be visible.
             Default: `3`
             Note: This option affects the length of the batch navigation to
                   avoid horizontal overflow for more than e.g. 50 pages.


# Full example

This example shows how the widget can be used with most of the described settings configured:


    class IPatientSchema(model.Schema):

        directives.widget(
            "patient_id_query",
            QuerySelectWidgetFactory,
            catalog=PATIENT_CATALOG,
            query={
                "portal_type": "Patient",
                "is_active": True,
                "sort_on": "title",
                "sort_order": "ascending",
            },
            search_index="patient_searchable_id",
            display_template="${patient_id}",
            value_key="patient_id",
            search_wildcard=True,
            multi_valued=False,
            allow_user_value=True,
            columns=[
                {
                    "name": "patient_id",
                    "width": "30",
                    "align": "left",
                    "label": _(u"Patient ID"),
                }, {
                    "name": "firstname",
                    "width": "70",
                    "align": "left",
                    "label": _(u"Patient Name"),
                },
            ],
            limit=3,
        )
        patient_id_query = schema.List(
            title=_(u"label_patient_id_query", default=u"Patient ID Query"),
            description=_(u"Query patient IDs or enter a new ID"),
            required=False,
            value_type=schema.TextLine(),
        )
