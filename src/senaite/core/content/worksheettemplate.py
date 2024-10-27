# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions
from bika.lims import api
from bika.lims import deprecated
from bika.lims import senaiteMessageFactory as _
from bika.lims.interfaces import IDeactivable
from plone.supermodel import model
from plone.autoform import directives
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.schema import UIDReferenceField
from senaite.core.schema.fields import DataGridRow
from senaite.core.content.base import Container
from senaite.core.config.widgets import get_default_columns
from senaite.core.interfaces import IWorksheetTemplate
from senaite.core.z3cform.widgets.number import NumberWidget
from senaite.core.z3cform.widgets.datagrid import DataGridWidgetFactory
from senaite.core.z3cform.widgets.uidreference import UIDReferenceWidgetFactory
from senaite.core.z3cform.widgets.listing.widget import ListingWidgetFactory
from zope import schema
from zope.interface import Interface
from zope.interface import implementer
from zope.schema.vocabulary import SimpleVocabulary
from z3c.form.interfaces import DISPLAY_MODE
from six.moves.urllib.parse import parse_qs


def get_query_num_positions():
    request = api.get_request()
    if request:
        params = dict(parse_qs(request["QUERY_STRING"]))
        values = params.get("num_positions")
        return int(values[0]) if values else 0
    return 0


def default_layout_positions(count_positions=None, start_pos=0):
    """Generate preset for Template Layout for new WorksheetTemplate with query
    string parameter 'num_positions' or generate preset from edit form

    :param count_positions: number of positions for Worksheet
    :param start_pos: Index for starting first position
    :returns: Array of object for description layout of worksheet
    """
    num_positions = get_query_num_positions()
    if count_positions:
        num_positions = int(count_positions)

    default_value = []
    for i in range(num_positions):
        default_value.append({
            "pos": start_pos + i + 1,
            "type": "a",
            "blank_ref": [],
            "control_ref": [],
            "reference_proxy": None,
            "dup_proxy": None,
            "dup": None,
        })
    return default_value


class IWorksheetTemplateServiceRecord(Interface):
    """Record schema for selected services
    """
    uid = schema.TextLine(
        title=_(u"title_service_uid", default=u"Service UID")
    )


class ILayoutRecord(Interface):
    """Record schema for layout worksheet
    """

    directives.widget("pos", klass="field")
    pos = schema.Int(
        title=_(
            u"title_layout_record_pos",
            default=u"Position"
        ),
        required=True,
        default=1,
    )

    directives.widget("type", klass="field")
    type = schema.Choice(
        title=_(
            u"title_layout_record_type",
            default=u"Analysis Type"
        ),
        vocabulary="senaite.core.vocabularies.analysis_types",
        required=True,
        default=u"a",
    )

    directives.widget(
        "blank_ref",
        UIDReferenceWidgetFactory,
        catalog=SETUP_CATALOG,
        query={
            "portal_type": "ReferenceDefinition",
            "is_active": True,
            "sort_limit": 5,
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        },
        display_template="<a href='${url}'>${title}</a>",
        columns=get_default_columns,
        limit=5,
    )
    directives.mode(blank_ref="hidden")
    blank_ref = UIDReferenceField(
        title=_(
            u"title_layout_record_blank_ref",
            default=u"Blank Reference"
        ),
        allowed_types=("ReferenceDefinition",),
        multi_valued=False,
        required=False,
    )

    directives.widget(
        "control_ref",
        UIDReferenceWidgetFactory,
        catalog=SETUP_CATALOG,
        query={
            "portal_type": "ReferenceDefinition",
            "is_active": True,
            "sort_limit": 5,
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        },
        display_template="<a href='${url}'>${title}</a>",
        columns=get_default_columns,
        limit=5,
    )
    directives.mode(control_ref="hidden")
    control_ref = UIDReferenceField(
        title=_(
            u"title_layout_record_control_ref",
            default=u"Control Reference"
        ),
        allowed_types=("ReferenceDefinition",),
        multi_valued=False,
        required=False,
    )

    directives.widget("reference_proxy", klass="field")
    reference_proxy = schema.Choice(
        title=_(
            u"title_layout_record_reference_proxy",
            default=u"Reference"
        ),
        vocabulary="senaite.core.vocabularies.reference_definition",
        required=False,
        default=None,
    )

    directives.widget("dup_proxy", klass="field")
    dup_proxy = schema.Choice(
        title=_(
            u"title_layout_record_dup_proxy",
            default=u"Duplicate Of"
        ),
        source=SimpleVocabulary.fromValues([0]),
        required=False,
        default=None,
    )

    directives.mode(dup="hidden")
    dup = schema.Int(
        title=_(
            u"title_layout_record_dup",
            default=u"Duplicate Of"
        ),
        required=False,
        default=None,
    )


class IWorksheetTemplateSchema(model.Schema):
    """Schema interface
    """

    title = schema.TextLine(
        title=_(
            u"title_worksheettemplate_title",
            default=u"Name"
        ),
        required=True,
    )

    description = schema.Text(
        title=_(
            u"title_worksheettemplate_description",
            default=u"Description"
        ),
        required=False,
    )

    directives.widget(
        "restrict_to_method",
        UIDReferenceWidgetFactory,
        catalog=SETUP_CATALOG,
        query={
            "portal_type": "Method",
            "is_active": True,
            "sort_limit": 5,
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        },
        display_template="<a href='${url}'>${title}</a>",
        columns=get_default_columns,
        limit=5,
    )
    restrict_to_method = UIDReferenceField(
        title=_(
            u"label_worksheettemplate_restrict_to_method",
            default=u"Restrict to Method"
        ),
        description=_(
            u"description_worksheettemplate_restrict_to_method",
            default=u"Restrict the available analysis services and "
                    u"instruments to those with the selected method.<br/>"
                    u"In order to apply this change to the services list, "
                    u"you should save the change first."
        ),
        allowed_types=("Method",),
        multi_valued=False,
        required=False,
    )

    directives.widget(
        "instrument",
        UIDReferenceWidgetFactory,
        catalog=SETUP_CATALOG,
        query="get_instrument_query",
        display_template="<a href='${url}'>${title}</a>",
        columns=get_default_columns,
        limit=5,
    )
    instrument = UIDReferenceField(
        title=_(
            u"label_worksheettemplate_instrument",
            default=u"Preferred instrument"
        ),
        description=_(u"description_worksheettemplate_instrument",
                      default=u"Select the preferred instrument"),
        allowed_types=("Instrument",),
        multi_valued=False,
        required=False,
    )

    model.fieldset(
        "layout",
        label=_(
            u"label_fieldset_worksheettemplate_layout",
            default=u"Layout"
        ),
        fields=[
            "num_of_positions",
            "template_layout",
        ]
    )

    directives.widget(
        "num_of_positions",
        NumberWidget,
        klass="num-positions")
    num_of_positions = schema.Int(
        title=_(
            u"title_worksheettemplate_num_of_positions",
            default=u"Number of Positions"
        ),
        required=False,
        defaultFactory=get_query_num_positions,
        min=0,
        default=0,
    )

    directives.widget(
        "template_layout",
        DataGridWidgetFactory,
        allow_insert=False,
        allow_delete=False,
        allow_reorder=False,
        auto_append=False,
        templates = {
            DISPLAY_MODE: "ws_template_datagrid_display.pt",
        })
    template_layout = schema.List(
        title=_(
            u"title_worksheettemplate_template_layout",
            default=u"Worksheet Layout"
        ),
        description=_(
            u"description_worksheettemplate_template_layout",
            default=u"Specify the size of the Worksheet, e.g. corresponding "
                    u"to a specific instrument's tray size. "
                    u"Then select an Analysis 'type' per Worksheet position. "
                    u"Where QC samples are selected, also select which "
                    u"Reference Sample should be used. "
                    u"If a duplicate analysis is selected, indicate which "
                    u"sample position it should be a duplicate of"
        ),
        value_type=DataGridRow(schema=ILayoutRecord),
        defaultFactory=default_layout_positions,
        required=True,
    )

    model.fieldset(
        "analyses",
        label=_(u"label_fieldset_worksheettemplate_analyses",
                default=u"Analyses"),
        fields=[
            "services",
        ]
    )

    # Services
    directives.widget(
        "services",
        ListingWidgetFactory,
        listing_view="worksheettemplate_services_widget"
    )
    services = schema.List(
        title=_(
            u"title_worksheettemplate_services",
            default=u"Analysis Services"
        ),
        description=_(
            u"description_worksheettemplate_services",
            default=u"Select which Analyses should be included on the "
                    u"Worksheet"
        ),
        value_type=DataGridRow(schema=IWorksheetTemplateServiceRecord),
        default=[],
        required=False,
    )


@implementer(IWorksheetTemplate, IWorksheetTemplateSchema, IDeactivable)
class WorksheetTemplate(Container):
    """Worksheet Template type
    """
    # Catalogs where this type will be catalogued
    _catalogs = [SETUP_CATALOG]

    security = ClassSecurityInfo()

    @security.protected(permissions.View)
    def getRawRestrictToMethod(self):
        method = self.getRestrictToMethod()
        if method:
            return method.UID()
        return None

    @security.protected(permissions.View)
    def getRestrictToMethod(self):
        accessor = self.accessor("restrict_to_method")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setRestrictToMethod(self, value):
        mutator = self.mutator("restrict_to_method")
        mutator(self, value)

    # BBB: AT schema field property
    RestrictToMethod = property(getRestrictToMethod, setRestrictToMethod)

    @security.protected(permissions.View)
    def getRawInstrument(self):
        instrument = self.getInstrument()
        if instrument:
            return instrument.UID()
        return None

    @security.protected(permissions.View)
    def getInstrument(self):
        accessor = self.accessor("instrument")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setInstrument(self, value):
        mutator = self.mutator("instrument")
        mutator(self, value)

    # BBB: AT schema field property
    Instrument = property(getInstrument, setInstrument)

    @security.protected(permissions.View)
    def getNumOfPositions(self):
        accessor = self.accessor("num_of_positions")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setNumOfPositions(self, value):
        if value == "":
            value = 0
        nums = int(value)
        mutator = self.mutator("num_of_positions")
        mutator(self, nums)
        layout = self.getTemplateLayout()
        len_layout = len(layout)
        if nums == 0:
            layout = []
        elif len_layout == 0 and nums > 0:
            # create default layout of 'nums' rows
            layout = default_layout_positions(nums)
        elif nums > len_layout:
            rows = nums - len_layout
            # added count 'rows' rows for layout
            # starting from index 'len_layout'
            layout = layout + default_layout_positions(rows, len_layout)
        elif nums < len_layout:
            # save firsts of 'nums' rows
            layout = layout[:nums]
        self.setTemplateLayout(layout)

    NumOfPositions = property(getNumOfPositions, setNumOfPositions)

    @security.protected(permissions.View)
    def getTemplateLayout(self):
        accessor = self.accessor("template_layout")
        return accessor(self) or []

    @security.protected(permissions.ModifyPortalContent)
    def setTemplateLayout(self, value):
        mutator = self.mutator("template_layout")
        mutator(self, value)
        num_pos = len(value)
        if num_pos != self.getNumOfPositions():
            self.setNumOfPositions(num_pos)

    # BBB: AT schema field property
    Layout = property(getTemplateLayout, setTemplateLayout)

    @security.protected(permissions.View)
    def getRawServices(self):
        """Return the raw value of the services field

        >>> self.getRawServices()
        ['<uid>', ...]

        :returns: List of uid's
        """
        accessor = self.accessor("services")
        services = accessor(self)
        if services:
            return [s.get("uid") for s in services]
        return []

    @deprecated(comment="If you need to get the service, use getRawServices",
                replacement="getRawServices")
    @security.protected(permissions.View)
    def getRawService(self):
        return self.getRawServices()

    @security.protected(permissions.View)
    def getServices(self):
        """Returns a list of service objects

        >>> self.getServices()
        [<AnalysisService at ...>,  <AnalysisService at ...>, ...]

        :returns: List of analysis service objects
        """
        services_uids = self.getRawServices()
        return list(map(api.get_object, services_uids))

    @security.protected(permissions.ModifyPortalContent)
    def setServices(self, value):
        """Set services for the template

        This method accepts either a list of analysis service objects, a list
        of analysis service UIDs or a list of analysis profile service records
        containing the key `uid`:

        >>> self.setServices([<AnalysisService at ...>, ...])
        >>> self.setServices(['353e1d9bd45d45dbabc837114a9c41e6', '...', ...])
        >>> self.setServices([{'uid': '...'}, ...])

        Raises a TypeError if the value does not match any allowed type.
        """
        if not isinstance(value, list):
            value = [value]

        records = []
        for v in value:
            uid = ""
            if isinstance(v, dict):
                uid = api.get_uid(v.get("uid"))
            elif api.is_object(v):
                uid = api.get_uid(v)
            elif api.is_uid(v):
                uid = v
            else:
                raise TypeError(
                    "Expected object, uid or record, got %r" % type(v))
            records.append({
                "uid": uid,
            })

        mutator = self.mutator("services")
        mutator(self, records)

    # BBB: AT schema field property
    Services = property(getServices, setServices)

    @security.private
    def get_instrument_query(self):
        """Return the preferred instruments
        """
        query = {
            "portal_type": "Instrument",
            "is_active": True,
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        }

        # Restrict available instruments to those with the selected method
        method = self.getRestrictToMethod()
        if method:
            # prepare subquery
            method_uid = method.UID()
            uids = []
            brains = api.search(query, SETUP_CATALOG)
            for brain in brains:
                uid = api.get_uid(brain)
                instrument = api.get_object(brain)
                if method_uid in instrument.getRawMethods():
                    uids.append(uid)
            # create a simple UID query
            query = {"UID": uids}
        return query
