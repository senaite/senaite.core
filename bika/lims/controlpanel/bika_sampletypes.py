# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import collections
import json

import plone
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import ISampleTypes
from bika.lims.utils import get_link
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder
from plone.app.folder.folder import ATFolderSchema
from plone.app.layout.globals.interfaces import IViewView
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from zope.interface.declarations import implements


# TODO: Separate content and view into own modules!


class SampleTypesView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(SampleTypesView, self).__init__(context, request)

        self.catalog = "bika_setup_catalog"

        self.contentFilter = {
            "portal_type": "SampleType",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        }

        self.context_actions = {
            _("Add"): {
                "url": "createObject?type_name=SampleType",
                "permission": "Add portal content",
                "icon": "++resource++bika.lims.images/add.png"}
        }

        self.title = self.context.translate(_("Sample Types"))
        self.icon = "{}/{}".format(
            self.portal_url,
            "/++resource++bika.lims.images/sampletype_big.png"
        )

        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Sample Type"),
                "index": "sortable_title"}),
            ("Description", {
                "title": _("Description"),
                "index": "description",
                "toggle": True}),
            ("getHazardous", {
                "title": _("Hazardous"),
                "toggle": True}),
            ("getPrefix", {
                "title": _("Prefix"),
                "toggle": True}),
            ("getMinimumVolume", {
                "title": _("Minimum Volume"),
                "toggle": True}),
            ("RetentionPeriod", {
                "title": _("Retention Period"),
                "toggle": True}),
            ("SampleMatrix", {
                "title": _("SampleMatrix"),
                "toggle": True}),
            ("ContainerType", {
                "title": _("Default Container"),
                "toggle": True}),
            ("getSamplePoints", {
                "title": _("Sample Points"),
                "toggle": True}),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _("Active"),
                "contentFilter": {"inactive_state": "active"},
                "transitions": [{"id": "deactivate"}, ],
                "columns": self.columns.keys(),
            }, {
                "id": "inactive",
                "title": _("Dormant"),
                "contentFilter": {"inactive_state": "inactive"},
                "transitions": [{"id": "activate"}, ],
                "columns": self.columns.keys(),
            }, {
                "id": "all",
                "title": _("All"),
                "contentFilter": {},
                "columns": self.columns.keys(),
            }
        ]

    def before_render(self):
        """Before template render hook
        """
        # Don't allow any context actions
        self.request.set("disable_border", 1)

    def folderitem(self, obj, item, index):
        """Service triggered each time an item is iterated in folderitems.

        The use of this service prevents the extra-loops in child objects.

        :obj: the instance of the class to be foldered
        :item: dict containing the properties of the object to be used by
            the template
        :index: current index of the item
        """

        title = obj.Title()
        description = obj.Description()
        url = obj.absolute_url()

        item["Description"] = description

        item["replace"]["Title"] = get_link(url, value=title)

        retention_period = obj.getRetentionPeriod()
        if retention_period:
            hours = retention_period["hours"]
            minutes = retention_period["minutes"]
            days = retention_period["days"]
            item["RetentionPeriod"] = _("hours: {} minutes: {} days: {}"
                                        .format(hours, minutes, days))
        else:
            item["RetentionPeriod"] = ""

        sample_matrix = obj.getSampleMatrix()
        if sample_matrix:
            title = sample_matrix.Title()
            url = sample_matrix.absolute_url()
            item["SampleMatrix"] = title
            item["replace"]["SampleMatrix"] = get_link(url, value=title)
        else:
            item["SampleMatrix"] = ""

        container_type = obj.getContainerType()
        if container_type:
            title = container_type.Title()
            url = container_type.absolute_url()
            item["ContainerType"] = title
            item["replace"]["ContainerType"] = get_link(url, value=title)
        else:
            item["ContainerType"] = ""

        sample_points = obj.getSamplePoints()
        if sample_points:
            links = map(
                lambda sp: get_link(sp.absolute_url(),
                                    value=sp.Title(),
                                    css_class="link"),
                sample_points)
            item["replace"]["getSamplePoints"] = ", ".join(links)
        else:
            item["getSamplePoints"] = ""

        return item


class ajax_SampleTypes(BrowserView):
    """Autocomplete data source for sample types field

    return JSON data [string,string]
    if "samplepoint" is in the request, it's expected to be a title string
    The objects returned will be filtered by samplepoint's SampleTypes.
    if no items are found, all items are returned.

    If term is a one or two letters, return items that begin with them
        If there aren't any, return items that contain them
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        bsc = getToolByName(self.context, "bika_setup_catalog")
        term = safe_unicode(self.request.get("term", "")).lower()
        items = []
        if not term:
            return json.dumps(items)
        samplepoint = safe_unicode(self.request.get("samplepoint", ""))
        # Strip "Lab: " from sample point titles
        samplepoint = samplepoint.replace("%s: " % _("Lab"), "")
        if samplepoint and len(samplepoint) > 1:
            sp = bsc(
                portal_type="SamplePoint",
                inactive_state="active",
                title=samplepoint
            )
            if not sp:
                return json.dumps([])
            sp = sp[0].getObject()
            items = sp.getSampleTypes()
        if not items:
            items = bsc(
                portal_type="SampleType",
                inactive_state="active",
                sort_on="sortable_title",
            )
            if term and len(term) < 3:
                # Items that start with A or AA
                items = [
                    s.getObject() for s in items
                    if s.title.lower().startswith(term)
                ]
                if not items:
                    # or, items that contain A or AA
                    items = [
                        s.getObject() for s in items
                        if s.title.lower().find(term) > -1]
            else:
                # or, items that contain term.
                items = [
                    s.getObject() for s in items
                    if s.title.lower().find(term) > -1]

        items = [callable(s.Title) and s.Title() or s.title
                 for s in items]
        return json.dumps(items)


schema = ATFolderSchema.copy()


class SampleTypes(ATFolder):
    """Sample Types Folder
    """
    implements(ISampleTypes)
    displayContentsTab = False
    schema = schema


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(SampleTypes, PROJECTNAME)
