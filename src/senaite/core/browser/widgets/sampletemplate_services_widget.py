# -*- coding: utf-8 -*-

import collections
from bika.lims import bikaMessageFactory as _
from plone.memoize import view
from bika.lims import api
from senaite.core.interfaces import ISampleTemplate

from .services_widget import ServicesWidget


class SampleTemplateServicesWidget(ServicesWidget):
    """Listing widget for Sample Template Services
    """

    # def __init__(self, field, request):
    #     super(SampleTemplateServicesWidget, self).__init__(field, request)

    def update(self):
        super(SampleTemplateServicesWidget, self).update()

        length = len(self.columns)
        items = list(self.columns.items())
        items.insert(length - 1, (
            "Partition", {
                "title": _(
                    u"listing_services_column_partition",
                    default=u"Partition"
                ),
                "sortable": False
            }))
        self.columns = collections.OrderedDict(items)
        self.review_states[0]["columns"] = self.columns.keys()

    @view.memoize
    def get_editable_columns(self):
        """Return editable fields
        """
        columns = []
        if self.is_edit_allowed():
            columns = ["Partition", "Hidden"]
        return columns

    @view.memoize
    def get_partition_choices(self):
        if not ISampleTemplate.providedBy(self.context):
            return [{
                "ResultValue": "part-1",
                "ResultText": "Part 1"
            }]

        partition_choices = []
        for num, part in enumerate(self.context.getPartitions()):
            part_id = part.get("part_id")
            self.partition_choices.append({
                "ResultValue": part_id,
                "ResultText": part_id.capitalize().replace("-", " "),
            })
        return partition_choices

    def extract(self):
        """Extract the value from the request for the field
        """
        form = self.request.form
        selected = form.get(self.select_checkbox_name, [])

        if not selected:
            return []

        # extract the data from the form for the field
        records = []
        hidden_services = form.get("Hidden", {})
        for uid in selected:
            records.append({
                "uid": uid,
                "hidden": hidden_services.get(uid) == "on",
                # TBD: add partition
            })

        return records

    def folderitem(self, obj, item, index):
        """Service triggered each time an item is iterated in folderitems.

        :obj: the instance of the class to be foldered
        :item: dict containing the properties of the object to be used by
            the template
        :index: current index of the item
        """
        item = super(SampleTemplateServicesWidget, self).folderitem(
            obj, item, index)
        obj = api.get_object(obj)
        uid = api.get_uid(obj)
        record = self.records.get(uid, {}) or {}

        # get the partition setting
        partition = "part-1"
        if record:
            partition = record.get("part_id")

        item["allow_edit"] = self.get_editable_columns()
        item["Partition"] = partition
        item["choices"]["Partition"] = self.get_partition_choices()

        return item
