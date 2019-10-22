# -*- coding: utf-8 -*-

import json
from xml.dom.minidom import parseString

from bika.lims import api
from bika.lims import logger
from bika.lims.interfaces import ISenaiteSiteRoot
from DateTime import DateTime
from OFS.interfaces import IOrderedContainer
from Products.Archetypes.interfaces import IBaseObject
from Products.CMFPlone.utils import _createObjectByType
from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.interfaces import INode
from Products.GenericSetup.interfaces import ISetupEnviron
from Products.GenericSetup.utils import ObjectManagerHelpers
from Products.GenericSetup.utils import XMLAdapterBase
from zope.component import adapts
from zope.component import queryMultiAdapter

from .config import SITE_ID

# Global UID mapping for reference fiedls
UID_MAP = {}

SKIP_TYPES = [
    "ARReport",
    "AnalysisRequest",
    "Attachment",
    "Batch",
    "Worksheet",
]


class SenaiteSiteXMLAdapter(XMLAdapterBase, ObjectManagerHelpers):
    adapts(ISenaiteSiteRoot, ISetupEnviron)

    def __init__(self, context, environ):
        super(SenaiteSiteXMLAdapter, self).__init__(context, environ)

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode("object")

        # remember the UID of the item for reference fields
        node.setAttribute("uid", "0")

        # Extract all contained objects
        node.appendChild(self._extractObjects())

        # TODO: Append acl_users

        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        obj_id = str(node.getAttribute("name"))
        self._logger.info("Imported '%r'" % obj_id)

    def _extractObjects(self):
        fragment = self._doc.createDocumentFragment()
        objects = self.context.objectValues()
        if not IOrderedContainer.providedBy(self.context):
            objects = list(objects)
            objects.sort(lambda x, y: cmp(x.getId(), y.getId()))
        for obj in objects:
            # Check if the object can be exported
            if not can_export(obj):
                logger.info("Skipping {}".format(repr(obj)))
                continue
            exporter = queryMultiAdapter((obj, self.environ), INode)
            if exporter:
                node = exporter.node
                if node is not None:
                    fragment.appendChild(exporter.node)
        return fragment


class ContentXMLAdapter(SenaiteSiteXMLAdapter):
    """Content XML Importer/Exporter
    """
    adapts(IBaseObject, ISetupEnviron)

    def __init__(self, context, environ):
        super(ContentXMLAdapter, self).__init__(context, environ)

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode("object")

        # remember the UID of the item for reference fields
        node.setAttribute("uid", self.context.UID())

        # remember the WF Status
        state = api.get_workflow_status_of(self.context)
        node.setAttribute("state", state)

        # Extract AuditLog
        node.appendChild(self._extractAuditLog(self.context))

        # Extract all fields of the current context
        node.appendChild(self._extractFields(self.context))

        # Extract all contained objects
        node.appendChild(self._extractObjects())

        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """

        # set workflow state
        self._initAuditLog(self.context, node)
        self._initWorkflow(self.context, node)
        self._initFields(self.context, node)

        # take a new snapshot
        api.snapshot.take_snapshot(self.context)

        self.context.reindexObject()

        obj_id = str(node.getAttribute("name"))
        self._logger.info("Imported '%r'" % obj_id)

    def _initAuditLog(self, context, node):
        for child in node.childNodes:
            if child.nodeName == "auditlog":
                snapshots = json.loads(child.firstChild.nodeValue)
                storage = api.snapshot.get_storage(context)
                storage[:] = map(json.dumps, snapshots)[:]
                return

    def _initWorkflow(self, context, node):
        state = node.getAttribute("state")

        if not state:
            return

        if state == api.get_workflow_status_of(context):
            return

        wf_state = {
            "action": None,
            "actor": None,
            "comments": "Generic Setup Import",
            "review_state": state,
            "time": DateTime(),
        }

        wf = api.get_tool("portal_workflow")
        wf_id = wf.getChainFor(context)[0]
        wf.setStatusOf(wf_id, context, wf_state)

    def _initFields(self, context, node):
        fields = api.get_fields(context)

        for child in node.childNodes:
            # we only handle filed nodes
            if child.nodeName != "field":
                continue

            name = child.getAttribute("name")
            field = fields.get(name)
            if field is None:
                self._logger.warning("Unrecognized field '{}'".format(name))
                continue

            importer = queryMultiAdapter((context, field, self.environ), INode)
            if importer:
                importer.uid_map = UID_MAP
                importer.node = child

    def _extractAuditLog(self, context):
        snapshots = api.snapshot.get_snapshots(self.context)
        node = self._doc.createElement("auditlog")
        child = self._doc.createTextNode(json.dumps(snapshots))
        node.appendChild(child)
        return node

    def _extractFields(self, context):
        fragment = self._doc.createDocumentFragment()

        fields = api.get_fields(context)
        for name, field in fields.items():
            # query the field adapter
            exporter = queryMultiAdapter((context, field, self.environ), INode)
            if not exporter:
                continue
            node = exporter.node
            if node is not None:
                fragment.appendChild(node)
        return fragment


def create_content_slugs(parent, parent_path, context):
    """Helper function to create initial content slugs
    """
    logger.info("create_content_slugs: parent={} parent_path={}".format(
        repr(parent), parent_path))
    path = "%s%s" % (parent_path, get_id(parent))
    filename = "%s.xml" % (path)
    items = dict(parent.objectItems())

    xml = context.readDataFile(filename)

    if xml is None:
        logger.warn("File not exists: '{}'".format(filename))
        return

    node = parseString(xml)

    if node.nodeName == "#document":
        node = node.firstChild

    name = node.getAttribute("name")
    uid = node.getAttribute("uid")
    logger.info("Processing ID '{}' (UID {}) in path '{}'"
                .format(name, uid, path))

    # remember the UID mapping
    UID_MAP[uid] = api.get_uid(parent)

    # set the UID
    if uid and api.is_at_content(parent):
        parent._setUID(uid)

    def is_object_node(n):
        return getattr(n, "nodeName", "") == "object"

    def get_child_nodes(n):
        return getattr(n, "childNodes", [])

    for child in get_child_nodes(node):
        if not is_object_node(child):
            continue

        child_id = child.getAttribute("name")
        portal_type = child.getAttribute("meta_type")
        obj = items.get(child_id)

        if not obj:
            # get the fti
            types_tool = api.get_tool("portal_types")
            fti = types_tool.getTypeInfo(portal_type)
            if fti and fti.product:
                obj = _createObjectByType(portal_type, parent, child_id)
            else:
                continue

        create_content_slugs(obj, path + "/", context)


def can_export(obj):
    """Decides if the object can be exported or not
    """
    if not api.is_object(obj):
        return False
    if api.get_portal_type(obj) in SKIP_TYPES:
        return False
    return True


def get_id(obj):
    if api.is_portal(obj):
        return SITE_ID
    return obj.getId().replace(" ", "_")


def exportObjects(obj, parent_path, context):
    """ Export subobjects recursively.
    """

    if not can_export(obj):
        logger.info("Skipping {}".format(repr(obj)))
        return

    exporter = queryMultiAdapter((obj, context), IBody)
    path = "%s%s" % (parent_path, get_id(obj))
    if exporter:
        if exporter.name:
            path = "%s%s" % (parent_path, exporter.name)
        filename = "%s%s" % (path, exporter.suffix)
        body = exporter.body
        if body is not None:
            context.writeDataFile(filename, body, exporter.mime_type)

    if getattr(obj, "objectValues", False):
        for sub in obj.objectValues():
            exportObjects(sub, path + "/", context)


def importObjects(obj, parent_path, context):
    """ Import subobjects recursively.
    """
    importer = queryMultiAdapter((obj, context), IBody)
    path = "%s%s" % (parent_path, get_id(obj))
    __traceback_info__ = path
    if importer:
        if importer.name:
            path = "%s%s" % (parent_path, importer.name)
        filename = "%s%s" % (path, importer.suffix)
        body = context.readDataFile(filename)
        if body is not None:
            importer.filename = filename  # for error reporting
            importer.body = body

    if getattr(obj, "objectValues", False):
        for sub in obj.objectValues():
            importObjects(sub, path + "/", context)


def export_xml(context):
    portal = context.getSite()
    exportObjects(portal, "", context)


def import_xml(context):
    portal = context.getSite()

    qi = api.get_tool("portal_quickinstaller")
    installed = qi.isProductInstalled("bika.lims")

    if not installed:
        logger.debug("Nothing to export.")
        return

    # create content slugs for UID references
    create_content_slugs(portal, "", context)

    # import objects
    importObjects(portal, "", context)
