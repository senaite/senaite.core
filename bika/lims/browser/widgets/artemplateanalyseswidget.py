# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import collections
from operator import itemgetter

from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import get_image
from bika.lims.utils import t
from plone.memoize import view
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import TypesWidget
from zope.i18n.locales import locales


class ARTemplateAnalysesView(BikaListingView):
    """ bika listing to display Analyses table for an ARTemplate.
    """

    def __init__(self, context, request):
        super(ARTemplateAnalysesView, self).__init__(context, request)

        self.catalog = "bika_setup_catalog"
        self.contentFilter = {
            "portal_type": "AnalysisService",
            "sort_on": "sortable_title",
            "inactive_state": "active"
        }
        self.context_actions = {}

        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_column_toggles = False
        self.show_select_column = True
        self.pagesize = 999999
        self.allow_edit = True
        self.show_search = False
        self.omit_form = True

        self.categories = []
        self.selected = []
        self.do_cats = self.context.bika_setup.getCategoriseAnalysisServices()
        if self.do_cats:
            self.show_categories = True
            self.expand_all_categories = False
            self.ajax_categories = True
            self.category_index = "getCategoryTitle"

        self.partition_choices = []
        for part in self.context.getPartitions():
            part_id = part.get("part_id")
            self.partition_choices.append({
                "ResultValue": part_id,
                "ResultText": part_id,
            })

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Service"),
                "index": "sortable_title",
                "sortable": False}),
            ("Price", {
                "title": _("Price"),
                "sortable": False}),
            ("Partition", {
                "title": _("Partition"),
                "sortable": False}),
            ("Hidden", {
                "title": _("Hidden"),
                "sortable": False,
                "type": "boolean"}),
        ))

        columns = ["Title", "Price", "Partition", "Hidden"]
        if not self.show_prices():
            columns.remove("Price")

        self.review_states = [
            {
                "id": "default",
                "title": _("All"),
                "contentFilter": {"inactive_state": "active"},
                "transitions": [],
                "columns": columns,
            }
        ]

        services = self.context.getAnalysisServicesSettings()
        self.selected = map(itemgetter("uid"), services)
        self.fieldvalue = self.context.getAnalyses()

    def update(self):
        """Update hook
        """
        super(ARTemplateAnalysesView, self).update()
        self.allow_edit = self.is_edit_allowed()

    @view.memoize
    def show_prices(self):
        """Checks if prices should be shown or not
        """
        setup = api.get_setup()
        return setup.getShowPrices()

    @view.memoize
    def get_currency_symbol(self):
        """Get the currency Symbol
        """
        locale = locales.getLocale('en')
        setup = api.get_setup()
        currency = setup.getCurrency()
        return locale.numbers.currencies[currency].symbol

    @view.memoize
    def is_edit_allowed(self):
        """Check if edit is allowed
        """
        current_user = api.get_current_user()
        roles = current_user.getRoles()
        if "LabManager" in roles:
            return True
        if "Manager" in roles:
            return True
        return False

    @view.memoize
    def get_editable_columns(self):
        """Return editable fields
        """
        columns = ["Partition", "Hidden"]
        return columns

    def is_service_hidden(self, service):
        """Checks if the service is hidden
        """
        uid = api.get_uid(service)
        settings = self.context.getAnalysisServiceSettings(uid)
        return settings.get("hidden", service.getHidden())

    def folderitem(self, obj, item, index):
        """Service triggered each time an item is iterated in folderitems.

        The use of this service prevents the extra-loops in child objects.

        :obj: the instance of the class to be foldered
        :item: dict containing the properties of the object to be used by
            the template
        :index: current index of the item
        """
        # ensure we have an object and not a brain
        obj = api.get_object(obj)
        uid = api.get_uid(obj)

        # get the category
        category = obj.getCategoryTitle()
        item["category"] = category
        if category not in self.categories:
            self.categories.append(category)

        item["Price"] = obj.getPrice()
        item["allow_edit"] = self.get_editable_columns()
        item["required"].append("Partition")
        item["choices"]["Partition"] = self.partition_choices
        item["Hidden"] = self.is_service_hidden(obj)
        item["selected"] = uid in self.selected

        # Icons
        after_icons = ""
        if obj.getAccredited():
            after_icons += get_image(
                "accredited.png", title=t(_("Accredited")))
        if obj.getAttachmentOption() == "r":
            after_icons += get_image(
                "attach_reqd.png", title=t(_("Attachment required")))
        if obj.getAttachmentOption() == "n":
            after_icons += get_image(
                "attach_no.png", title=t(_('Attachment not permitted')))
        if after_icons:
            item["after"]["Title"] = after_icons

        return item

    def folderitems(self):
        """XXX refactor if possible to non-classic mode
        """
        items = super(ARTemplateAnalysesView, self).folderitems()
        self.categories.sort()
        return items


class ARTemplateAnalysesWidget(TypesWidget):
    """AR Template Analyses Widget
    """
    _properties = TypesWidget._properties.copy()
    _properties.update({
        "macro": "bika_widgets/artemplateanalyseswidget",
        "helper_js": ("bika_widgets/artemplateanalyseswidget.js",),
        "helper_css": ("bika_widgets/artemplateanalyseswidget.css",),
    })

    security = ClassSecurityInfo()

    security.declarePublic("process_form")

    def process_form(self, instance, field, form, **kwargs):
        """Return a list of dictionaries fit for ARTemplate/Analyses field
           consumption.
        """
        value = []

        service_uids = form.get("uids", None)
        Partitions = form.get("Partition", None)

        if Partitions and service_uids:
            Partitions = Partitions[0]
            for service_uid in service_uids:
                if service_uid in Partitions.keys() \
                   and Partitions[service_uid] != '':
                    value.append({
                        "service_uid": service_uid,
                        "partition": Partitions[service_uid]
                    })

        if instance.portal_type == "ARTemplate":
            # Hidden analyses?
            outs = []
            hiddenans = form.get("Hidden", {})
            if service_uids:
                for uid in service_uids:
                    hidden = hiddenans.get(uid, "") == "on"
                    outs.append({"uid": uid, "hidden": hidden})
            instance.setAnalysisServicesSettings(outs)

        return value, {}

    security.declarePublic("Analyses")

    def Analyses(self, field, allow_edit=False):
        """Render Analyses Listing Table
        """
        instance = getattr(self, "instance", field.aq_parent)
        view = api.get_view(
            "table_ar_template_analyses", context=instance)
        # Call listing hooks
        view.update()
        view.before_render()
        return view.ajax_contents_table()


registerWidget(ARTemplateAnalysesWidget,
               title="AR Template Analyses Layout",
               description=("AR Template Analyses Layout"))
