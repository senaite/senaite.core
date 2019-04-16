# -*- coding: utf-8 -*-

import collections
import json

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.interfaces import IAuditable
from bika.lims.subscribers.auditlog import get_storage
from bika.lims.utils import t
from plone.memoize import view
from Products.CMFPlone.i18nl10n import ulocalized_time
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class HasAuditLog(BrowserView):
    """Helper View to check if the context provides the IAuditable interface
    """
    def __call__(self):
        return IAuditable.providedBy(self.context)


class AuditLogView(BikaListingView):
    """Audit View
    """
    template = ViewPageTemplateFile("templates/audit.pt")
    diff_template = ViewPageTemplateFile("templates/audit_diff.pt")

    def __init__(self, context, request):
        super(AuditLogView, self).__init__(context, request)

        self.show_select_column = False
        self.show_search = False
        self.pagesize = 5

        self.icon = "{}/{}/{}".format(
            self.portal_url,
            "++resource++bika.lims.images",
            "%s_big.png" % context.portal_type.lower())

        self.title = "Audit Log for {}".format(api.get_title(context))

        self.columns = collections.OrderedDict((
            ("version", {
                "title": _("Version"), "sortable": False}),
            ("modified", {
                "title": _("Date Modified"), "sortable": False}),
            ("actor", {
                "title": _("Actor"), "sortable": False}),
            ("remote_address", {
                "title": _("Remote IP"), "sortable": False}),
            ("action", {
                "title": _("Action"), "sortable": False}),
            ("review_state", {
                "title": _("Workflow State"), "sortable": False}),
            ("comment", {
                "title": _("Comment"), "sortable": False}),
            ("diff", {
                "title": _("Changes"), "sortable": False}),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": "All",
                "contentFilter": {},
                "columns": self.columns.keys(),
            }
        ]

    def update(self):
        """Update hook
        """
        super(AuditLogView, self).update()

    def make_empty_item(self, **kw):
        """Create a new empty item
        """
        item = {
            "uid": None,
            "before": {},
            "after": {},
            "replace": {},
            "allow_edit": [],
            "disabled": False,
            "state_class": "state-active",
        }
        item.update(**kw)
        return item

    @view.memoize
    def get_snapshots(self):
        """Get all snapshots from the storage

        :returns: List of snapshots
        """
        snapshots = get_storage(self.context)
        return map(json.loads, snapshots)

    def to_localized_time(self, date, **kw):
        """Converts the given date to a localized time string
        """
        date = api.to_date(date, default=None)
        if date is None:
            return ""
        # default options
        options = {
            "long_format": True,
            "time_only": False,
            "context": self.context,
            "request": self.request,
            "domain": "senaite.core",
        }
        options.update(kw)
        return ulocalized_time(date, **options)

    @view.memoize
    def get_fieldnames(self):
        """Returns a list of schema fields
        """
        fields = api.get_fields(self.context)
        return fields.keys()

    def get_snapshot_by_version(self, version):
        """Get a snapshot by version
        """
        if version < 0:
            return None
        snapshots = self.get_snapshots()
        if version > len(snapshots):
            return None
        return snapshots[version]

    def diff_snapshots(self, snapshot_a, snapshot_b):
        """Returns a diff of two given snapshots (dictionaries)

        :param snapshot_a: First snapshot
        :param snapshot_b: Second snapshot
        :returns: Dictionary of field/value pairs that differ
        """
        if not all(map(lambda x: isinstance(x, dict),
                       [snapshot_a, snapshot_b])):
            return {}

        diffs = {}
        fieldnames = self.get_fieldnames()
        for key_a, value_a in snapshot_a.iteritems():
            # skip non-schema keys
            if key_a not in fieldnames:
                continue

            # get the value of the second snapshot
            value_b = snapshot_b.get(key_a)
            # get the diff between the two values
            diff = self.diff_values(value_a, value_b)
            if diff is not None:
                field = self.get_field_by_name(key_a)
                label = field.widget.label or key_a
                diffs[label] = diff
        return diffs

    def get_field_by_name(self, name):
        """Get a schema field by name
        """
        return self.context.getField(name)

    def diff_values(self, value_a, value_b):
        """Returns a human-readable diff between two values

        :param value_a: First value to compare
        :param value_b: Second value to compare
        :returns a list of diff tuples
        """

        v_A = self.process_value(value_a)
        v_B = self.process_value(value_b)

        # No changes
        if v_A == v_B:
            return None

        diffs = []
        diffs.append((v_A, v_B))
        return diffs

    def process_value(self, value):
        """Convert the value into a human readable diff string
        """
        if not value:
            value = _("Not set")
        # XXX: bad data, e.g. in AS Method field
        elif value == "None":
            value = _("Not set")
        elif api.is_uid(value):
            value = self.get_title_or_id_from_uid(value)
        elif api.is_date(value):
            value = self.to_localized_time(api.to_date(value))
        elif isinstance(value, (list, tuple)):
            value = map(self.process_value, value)
            value = "  ".join(value)
        elif isinstance(value, unicode):
            value = api.safe_unicode(value).encode("utf8")
        return str(value)

    def get_title_or_id_from_uid(self, uid):
        """Returns the title or ID from the given UID
        """
        try:
            obj = api.get_object_by_uid(uid)
        except api.APIError:
            return "<Deleted Object {}>".format(uid)

        title_or_id = api.get_title(obj) or api.get_id(obj)
        logger.info("get_title_or_id_from_uid: {} -> {}"
                    .format(uid, title_or_id))
        return title_or_id

    def render_diff(self, diff):
        """Render the diff template

        :param diff: Dictionary of fieldname -> diffs
        :returns: Rendered HTML template
        """
        return self.diff_template(self, diff=diff)

    def get_snapshot_version(self, snapshot):
        """Returns the version of the given snapshot
        """
        snapshots = self.get_snapshots()
        return snapshots.index(snapshot)

    def get_snapshot_metadata(self, snapshot):
        """Returns the snapshot metadata
        """
        return snapshot.get("metadata", {})

    def translate_state(self, s):
        """Translate the given state string
        """
        if not isinstance(s, basestring):
            return s
        s = s.capitalize().replace("_", " ")
        return t(_(s))

    def folderitems(self):
        """Generate folderitems for each version
        """
        items = []
        # get the snapshots
        snapshots = self.get_snapshots()
        # reverse the order to get the most recent change first
        snapshots = list(reversed(snapshots))
        # set the total number of items
        self.total = len(snapshots)
        # slice a batch
        batch = snapshots[self.limit_from:self.limit_from+self.pagesize]

        for snapshot in batch:
            item = self.make_empty_item(**snapshot)
            # get the version of the snapshot
            version = self.get_snapshot_version(snapshot)

            # Version
            item["version"] = version

            # get the metadata of the diff
            metadata = self.get_snapshot_metadata(snapshot)

            # Modification Date
            m_date = metadata.get("modified")
            item["modified"] = self.to_localized_time(m_date)

            # Actor
            actor = metadata.get("actor")
            if actor:
                properties = api.get_user_properties(actor)
                item["actor"] = properties.get("fullname", actor)

            # Remote Address
            remote_address = metadata.get("remote_address")
            item["remote_address"] = remote_address

            # Action
            action = metadata.get("action")
            item["action"] = self.translate_state(action)

            # Review State
            review_state = metadata.get("review_state")
            item["review_state"] = self.translate_state(review_state)

            # Change Comment
            comment = metadata.get("comment")
            item["comment"] = comment

            # get the previous snapshot
            prev_snapshot = self.get_snapshot_by_version(version-1)
            if prev_snapshot:
                prev_metadata = self.get_snapshot_metadata(prev_snapshot)
                prev_review_state = prev_metadata.get("review_state")
                if prev_review_state != review_state:
                    item["replace"]["review_state"] = "{} &rarr; {}".format(
                        self.translate_state(prev_review_state),
                        self.translate_state(review_state))

                # Rendered Diff
                diff = self.diff_snapshots(snapshot, prev_snapshot)
                item["diff"] = self.render_diff(diff)

            # append the item
            items.append(item)

        return items
