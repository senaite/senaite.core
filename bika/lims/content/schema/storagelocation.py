# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Products.Archetypes.Field import StringField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import StringWidget
from bika.lims import bikaMessageFactory as _
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaSchema

SiteTitle = StringField(
    'SiteTitle',
    storage=Storage,
    widget=StringWidget(
        label=_("Site Title"),
        description=_("Title of the site")
    )
)
SiteCode = StringField(
    'SiteCode',
    storage=Storage,
    widget=StringWidget(
        label=_("Site Code"),
        description=_("Code for the site")
    )
)
SiteDescription = StringField(
    'SiteDescription',
    storage=Storage,
    widget=StringWidget(
        label=_("Site Description"),
        description=_("Description of the site")
    )
)
LocationTitle = StringField(
    'LocationTitle',
    storage=Storage,
    widget=StringWidget(
        label=_("Location Title"),
        description=_("Title of location")
    )
)
LocationCode = StringField(
    'LocationCode',
    storage=Storage,
    widget=StringWidget(
        label=_("Location Code"),
        description=_("Code for the location")
    )
)
LocationDescription = StringField(
    'LocationDescription',
    storage=Storage,
    widget=StringWidget(
        label=_("Location Description"),
        description=_("Description of the location")
    )
)
LocationType = StringField(
    'LocationType',
    storage=Storage,
    widget=StringWidget(
        label=_("Location Type"),
        description=_("Type of location")
    )
)
ShelfTitle = StringField(
    'ShelfTitle',
    storage=Storage,
    widget=StringWidget(
        label=_("Shelf Title"),
        description=_("Title of the shelf")
    )
)
ShelfCode = StringField(
    'ShelfCode',
    storage=Storage,
    widget=StringWidget(
        label=_("Shelf Code"),
        description=_("Code the the shelf")
    )
)
ShelfDescription = StringField(
    'ShelfDescription',
    storage=Storage,
    widget=StringWidget(
        label=_("Shelf Description"),
        description=_("Description of the shelf")
    )
)

schema = BikaSchema.copy() + Schema((
    SiteTitle,
    SiteCode,
    SiteDescription,
    LocationTitle,
    LocationCode,
    LocationDescription,
    LocationType,
    ShelfTitle,
    ShelfCode,
    ShelfDescription
))
schema['title'].widget.label = _('Address')
schema['description'].widget.visible = True
