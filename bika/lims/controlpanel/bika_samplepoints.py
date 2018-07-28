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
from bika.lims.interfaces import ISamplePoints
from bika.lims.utils import get_link
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder
from plone.app.folder.folder import ATFolderSchema
from plone.app.layout.globals.interfaces import IViewView
from Products.Archetypes import PloneMessageFactory as _p
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from zope.interface.declarations import implements


# TODO: Separate content and view into own modules!


class SamplePointsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(SamplePointsView, self).__init__(context, request)

        self.catalog = "bika_setup_catalog"
        self.contentFilter = {
            "portal_type": "SamplePoint",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        }

        self.context_actions = {
            _("Add"): {
                "url": "createObject?type_name=SamplePoint",
                "permission": "Add portal content",
                "icon": "++resource++bika.lims.images/add.png"}
        }

        self.title = self.context.translate(_("Sample Points"))
        self.icon = "{}/{}".format(
            self.portal_url,
            "/++resource++bika.lims.images/samplepoint_big.png"
        )
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Sample Point"),
                "index": "sortable_title"}),
            ("Description", {
                "title": _("Description"),
                "index": "Description",
                "toggle": True}),
            ("Owner", {
                "title": _p("Owner"),
                "sortable": False,
                "toggle": True}),
            ("getComposite", {
                "title": _("Composite"),
                "sortable": False,
                "toggle": False}),
            ("SampleTypes", {
                "title": _("Sample Types"),
                "index": "getSampleTypeTitle",
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

        item["replace"]["Title"] = get_link(url, value=title)
        item["Description"] = description

        sample_types = obj.getSampleTypes()
        if sample_types:
            links = map(
                lambda st: get_link(st.absolute_url(),
                                    value=st.Title(),
                                    css_class="link"),
                sample_types)
            item["replace"]["SampleTypes"] = ", ".join(links)
        else:
            item["SampleTypes"] = ""

        parent = obj.aq_parent
        if parent.portal_type == "Client":
            item["Owner"] = parent.aq_parent.Title()
            item["replace"]["Owner"] = get_link(
                parent.absolute_url(), value=parent.getName())
        else:
            item["Owner"] = self.context.bika_setup.laboratory.Title()

        return item


class ajax_SamplePoints(BrowserView):
    """ The autocomplete data source for sample point selection widgets.
        Returns a JSON list of sample point titles.

    Request parameters:

    - sampletype: if specified, it's expected to be the title
        of a SamplePoint object.  Optionally, the string 'Lab: ' might be
        prepended, to distinguish between Lab and Client objects.

    - term: the string which will be searched against all SamplePoint
        titles.

    - _authenticator: The plone.protect authenticator.
    """

    def filter_list(self, items, searchterm):
        if searchterm and len(searchterm) < 3:
            # Items that start with A or AA
            res = [s.getObject() for s in items
                   if s.title.lower().startswith(searchterm)]
            if not res:
                # or, items that contain A or AA
                res = [s.getObject() for s in items
                       if s.title.lower().find(searchterm) > -1]
        else:
            # or, items that contain searchterm.
            res = [s.getObject() for s in items
                   if s.title.lower().find(searchterm) > -1]
        return res

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        term = safe_unicode(self.request.get('term', '')).lower()
        items = []
        if not term:
            return json.dumps(items)
        # Strip "Lab: " from sample point title
        term = term.replace("%s: " % _("Lab"), "")
        sampletype = safe_unicode(self.request.get("sampletype", ""))
        if sampletype and len(sampletype) > 1:
            st = bsc(
                portal_type="SampleType",
                title=sampletype,
                inactive_state="active",
            )
            if not st:
                return json.dumps([])
            st = st[0].getObject()
            items = [o.Title() for o in st.getSamplePoints()]

        if not items:
            client_items = lab_items = []

            # User (client) sample points
            if self.context.portal_type in ("Client", "AnalysisRequest"):
                if self.context.portal_type == "Client":
                    client_path = self.context.getPhysicalPath()
                else:
                    client_path = self.context.aq_parent.getPhysicalPath()
                client_items = list(
                    bsc(portal_type="SamplePoint",
                        path={"query": "/".join(client_path), "level": 0},
                        inactive_state="active",
                        sort_on="sortable_title"))

            # Global (lab) sample points
            sample_points = self.context.bika_setup.bika_samplepoints
            lab_path = sample_points.getPhysicalPath()
            lab_items = list(
                bsc(portal_type="SamplePoint",
                    path={"query": "/".join(lab_path), "level": 0},
                    inactive_state="active",
                    sort_on="sortable_title"))
            client_items = [callable(s.Title) and s.Title() or s.title
                            for s in self.filter_list(client_items, term)]
            lab_items = [callable(s.Title) and s.Title() or s.title
                         for s in self.filter_list(lab_items, term)]
            lab_items = ["%s: %s" % (_("Lab"), safe_unicode(i))
                         for i in lab_items]
            items = client_items + lab_items

        return json.dumps(items)


schema = ATFolderSchema.copy()


class SamplePoints(ATFolder):
    implements(ISamplePoints)
    displayContentsTab = False
    schema = schema


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(SamplePoints, PROJECTNAME)
