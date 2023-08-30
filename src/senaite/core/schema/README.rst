Custom Schema Fields
====================

This package contains custom fields for dexterity based SENAITE contents.


UID reference field
-------------------

Added in PR: https://github.com/senaite/senaite.core/pull/1864

This field used the object UIDs to create references between two or more objects.

Example::

  from plone.dexterity.content import Container
  from plone.supermodel import model
  from senaite.core import senaiteMessageFactory as _
  from senaite.core.interfaces import IObject
  from zope import schema
  from zope.interface import implementer
  from senaite.core.schema import UIDReferenceField
  from senaite.core.z3cform.widgets.uidreference import UIDReferenceWidgetFactory
  from plone.autoform import directives

  class IObjectSchema(model.Schema):
      """Schema definition for client object
      """

      title = schema.TextLine(
          title=_(u"Name"),
          description=_(
              u"Client object name"),
          required=True)

      description = schema.Text(
          title=_(u"Description"),
          description=_(
              u"Description of the client object"),
          required=False)

      route = UIDReferenceField(
          title=_(u"Route"),
          allowed_types=("ObjectRoute", ),
          multi_valued=True,
          description=_(
              u"Client object route"),
          required=True)

      directives.widget(
          "route",
          UIDReferenceWidgetFactory,
          catalog="senaite_catalog_setup",
          query={
              "portal_type": "ObjectRoute",
              "is_active": True,
              "sort_on": "title",
              "sort_order": "ascending",
          },
          display_template="<a href='${url}'>${title} ${description}</a>",
          columns=[
              {
                  "name": "title",
                  "width": "30",
                  "align": "left",
                  "label": _(u"Title"),
              }, {
                  "name": "description",
                  "width": "70",
                  "align": "left",
                  "label": _(u"Description"),
              },
          ],
          limit=2,
      )


  @implementer(IObject, IObjectSchema)
  class Object(Container):
      """Client object
      """


Field attributes
................

The following settings can be done on field level:

- `allowed_types`

Tuple of allowed contenttypes to be referenced.
This value is validated in field.
Omitting the value means that all types are allowed.

- `multi_valued`

`True`/`False` if multiple references are allowed on the field.
Default value is `True`


Widget attributes
.................

The following settings can be done in `directives.widget`:

- `catalog`

The search catalog to use.
Default value is `uid_catalog`

- `query`

The catalog query to use for the search.

- `display_template`

Custom template to display the item.
Default template is `<a href='${url}'>${title} ${description}</a>`
NOTE: Any keys that come with the JSON search response can be used.


- `columns`

Column config for the search results table popup.
This is a list of dict objects with the following keys:

  - `name`: field name
  - `label`: field title
  - `width`: column width (default `auto`)
  - `align`: column alignment (default `left`)


- `limit`

This defines how many items are listed on one page.
Default value is 25.
