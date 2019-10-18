# -*- coding: utf-8 -*-

from xml.dom.minidom import parseString

from bika.lims import api
from bika.lims import logger
from Products.Archetypes.interfaces import IBaseObject
from Products.CMFPlone.utils import _createObjectByType
from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.interfaces import INode
from Products.GenericSetup.interfaces import ISetupEnviron
# from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import ObjectManagerHelpers
from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import importObjects
from zope.component import adapts
from zope.component import queryMultiAdapter

# Global UID mapping for reference fiedls
UID_MAP = {}

# Skip types and contents
SKIP_TYPES = [
    "AnalysisRequest",
]


class ContentXMLAdapter(XMLAdapterBase, ObjectManagerHelpers):
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

        # Extract all fields of the current context
        node.appendChild(self._extractFields(self.context))

        # Extract all contained objects
        node.appendChild(self._extractObjects())

        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        self._initFields(self.context, node)
        self.context.reindexObject()

        obj_id = str(node.getAttribute("name"))
        self._logger.info("Imported '%r'" % obj_id)

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
    """Helper function to create initial content slugs for UID mapping
    """
    logger.info("create_content_slugs: parent={} parent_path={}".format(
        repr(parent), parent_path))
    path = "%s%s" % (parent_path, parent.getId().replace(" ", "_"))
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
            if fti.product:
                obj = _createObjectByType(portal_type, parent, child_id)
            else:
                continue

        create_content_slugs(obj, path + "/", context)


def exportObjects(obj, parent_path, context):
    """Export subobjects recursively.
    """
    portal_type = api.get_portal_type(obj)
    if portal_type in SKIP_TYPES:
        logger.info("Skipping {}".format(repr(obj)))
        return

    exporter = queryMultiAdapter((obj, context), IBody)
    path = "%s%s" % (parent_path, obj.getId().replace(" ", "_"))
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


def export_xml(context):
    portal = context.getSite()
    exportObjects(portal.bika_setup, "", context)
    exportObjects(portal.methods, "", context)
    exportObjects(portal.clients, "", context)


def import_xml(context):
    portal = context.getSite()

    # create content slugs for UID references
    create_content_slugs(portal.bika_setup, "", context)
    create_content_slugs(portal.methods, "", context)
    create_content_slugs(portal.clients, "", context)

    # import objects
    importObjects(portal.bika_setup, "", context)
    importObjects(portal.methods, "", context)
    importObjects(portal.clients, "", context)
