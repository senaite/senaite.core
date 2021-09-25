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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

import json
from xml.dom.minidom import parseString

from bika.lims import api
from bika.lims import logger
from bika.lims.interfaces import IAuditable
from bika.lims.interfaces import ISenaiteSiteRoot
from DateTime import DateTime
from OFS.interfaces import IOrderedContainer
from plone.dexterity.interfaces import IDexterityContainer
from plone.dexterity.interfaces import IDexterityItem
from Products.Archetypes.interfaces import IBaseObject
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.utils import safe_unicode
from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.interfaces import INode
from Products.GenericSetup.interfaces import ISetupEnviron
from Products.GenericSetup.utils import I18NURI
from Products.GenericSetup.utils import ObjectManagerHelpers
from Products.GenericSetup.utils import XMLAdapterBase
from senaite.core.p3compat import cmp
from zope.component import adapts
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component.interfaces import IFactory
from zope.event import notify
from zope.interface import alsoProvides
from zope.lifecycleevent import ObjectCreatedEvent

from .config import SITE_ID

# Skip user created contents
SKIP_EXPORT_TYPES = [
    "ARReport",
    "AnalysisRequest",
    "Attachment",
    "Batch",
    "ReferenceSample",
    "SupplyOrder",
    "Worksheet",
]

ID_MAP = {}


class SenaiteSiteXMLAdapter(XMLAdapterBase, ObjectManagerHelpers):
    """Adapter for the SENAITE root object (portal)
    """
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

        # Extract Groups
        node.appendChild(self._extractGroups(self.context))

        # Extract Users
        node.appendChild(self._extractUsers(self.context))

        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        obj_id = str(node.getAttribute("name"))

        if "acl_users" not in self.context:
            return

        # Add groups and users
        self._initGroups(self.context, node)
        self._initUsers(self.context, node)

        self._logger.info("Imported '%r'" % obj_id)

    def _initGroups(self, context, node):
        group_tool = api.get_tool("portal_groups")
        for child in node.childNodes:
            if child.nodeName != "groups":
                continue
            for cn in child.childNodes:
                if cn.nodeName != "group":
                    continue
                group_id = cn.firstChild.nodeValue
                group = api.user.get_group(group_id)
                if not group:
                    self._logger.info("Adding group {}".format(group_id))
                    roles = cn.getAttribute("roles").split(",")
                    group_tool.addGroup(group_id, roles=roles)
                    group = group_tool.getGroupById(group_id)

                # set the group properties
                group.setProperties(properties={
                    "title": cn.getAttribute("name"),
                    "email": cn.getAttribute("email"),
                })

    def _initUsers(self, context, node):
        reg_tool = api.get_tool("portal_registration")
        for child in node.childNodes:
            if child.nodeName != "users":
                continue
            for cn in child.childNodes:
                if cn.nodeName != "user":
                    continue
                user_id = cn.firstChild.nodeValue
                user = api.user.get_user(user_id)

                if not user: # add new user with password
                    self._logger.info("Adding user {}".format(user_id))
                    user = reg_tool.addMember(user_id, '12345') 

                # set the user properties
                user.setProperties(properties={
                    "fullname": cn.getAttribute("name"),
                    "email": cn.getAttribute("email"),
                })

                # add the user to the groups
                groups = cn.getAttribute("groups")
                if groups:
                    group_ids = groups.split(",")
                    api.user.add_group(group_ids, user_id)

    def _get_users(self):
        acl_users = api.get_tool("acl_users")
        return acl_users.getUsers()

    def _get_groups(self):
        acl_users = api.get_tool("acl_users")
        return acl_users.getGroups()

    def _get_roles_for_principal(self, principal):
        """Returs a list of roles for the user/group
        """
        ignored_roles = ["Authenticated"]
        roles = filter(lambda r: r not in ignored_roles,
                       principal.getRoles())
        return roles

    def _get_groups_for_principal(self, principal):
        """Returs a list of groups for the user/group
        """
        ignored_groups = ["AuthenticatedUsers"]
        groups = filter(lambda r: r not in ignored_groups,
                        principal.getGroupIds())
        return groups

    def _extractGroups(self, context):
        node = self._doc.createElement("groups")
        for group in self._get_groups():
            name = group.getGroupName()
            roles = self._get_roles_for_principal(group)
            child = self._doc.createElement("group")
            child.setAttribute("name", safe_unicode(name))
            child.setAttribute("roles", ",".join(roles))
            text = self._doc.createTextNode(group.getGroupId())
            child.appendChild(text)
            node.appendChild(child)
        return node

    def _extractUsers(self, context):
        node = self._doc.createElement("users")
        for user in self._get_users():
            name = user.getProperty("fullname")
            groups = self._get_groups_for_principal(user)
            child = self._doc.createElement("user")
            child.setAttribute("name", safe_unicode(name))
            child.setAttribute("email", user.getProperty("email"))
            child.setAttribute("groups", ",".join(groups))
            text = self._doc.createTextNode(user.getId())
            child.appendChild(text)
            node.appendChild(child)
        return node

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


class ATContentXMLAdapter(SenaiteSiteXMLAdapter):
    """AT Content XML Importer/Exporter
    """
    adapts(IBaseObject, ISetupEnviron)

    def __init__(self, context, environ):
        super(ATContentXMLAdapter, self).__init__(context, environ)

    def _getObjectNode(self, name, i18n=True):
        node = self._doc.createElement(name)
        # Attach the UID of the object as well
        node.setAttribute("id", api.get_id(self.context))
        node.setAttribute("uid", api.get_uid(self.context))
        node.setAttribute("name", api.get_id(self.context))
        node.setAttribute("meta_type", self.context.meta_type)
        node.setAttribute("portal_type", api.get_portal_type(self.context))
        i18n_domain = getattr(self.context, "i18n_domain", None)
        if i18n and i18n_domain:
            node.setAttributeNS(I18NURI, "i18n:domain", i18n_domain)
            self._i18n_props = ("title", "description")
        return node

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode("object")

        # remember the UID of the item for reference fields
        node.setAttribute("uid", api.get_uid(self.context))

        # remember the WF Status
        # TODO: Export the complete Review History
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

        # reindex the object
        self.context.reindexObject()

        # set a new snapshot
        # api.snapshot.take_snapshot(self.context)

        obj_id = str(node.getAttribute("name"))
        self._logger.info("Imported '%r'" % obj_id)

    def _initAuditLog(self, context, node):
        for child in node.childNodes:
            if child.nodeName == "auditlog":
                snapshots = json.loads(child.firstChild.nodeValue)
                storage = api.snapshot.get_storage(context)
                storage[:] = map(json.dumps, snapshots)[:]
                # make sure the object provides `IAuditable`
                alsoProvides(context, IAuditable)
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


class DXContainerXMLAdapter(ATContentXMLAdapter):
    """DX Container XML Importer/Exporter
    """
    adapts(IDexterityContainer, ISetupEnviron)

    def __init__(self, context, environ):
        super(DXContainerXMLAdapter, self).__init__(context, environ)


class DXItemXMLAdapter(ATContentXMLAdapter):
    """DX Item XML Importer/Exporter
    """
    adapts(IDexterityItem, ISetupEnviron)

    def __init__(self, context, environ):
        super(DXItemXMLAdapter, self).__init__(context, environ)


def create_content_slugs(parent, parent_path, context):
    """Helper function to create initial content slugs
    """
    logger.info("create_content_slugs: parent={} parent_path={}".format(
        repr(parent), parent_path))

    path = "%s%s" % (parent_path, get_id(parent))
    filename = "%s.xml" % (path)
    xml = context.readDataFile(filename)

    if xml is None:
        logger.error("File not found: '{}'".format(filename))
        return

    # parse the XML data
    node = parseString(xml)

    if node.nodeName == "#document":
        node = node.firstChild

    # read the node attributes
    name = node.getAttribute("name")
    uid = node.getAttribute("uid")
    logger.info("::: Processing '{}' (UID {}) in path '{}' :::"
                .format(name, uid, path))

    def is_object_node(n):
        return getattr(n, "nodeName", "") == "object"

    def get_child_nodes(n):
        return getattr(n, "childNodes", [])

    for child in get_child_nodes(node):
        # only process `<object ../>` nodes
        if not is_object_node(child):
            continue
        # extract node attributes (see `_exportNode` method)
        child_id = child.getAttribute("name")
        child_uid = child.getAttribute("uid")
        portal_type = child.getAttribute("portal_type")
        # get or create object
        obj = create_or_get(parent, child_id, child_uid, portal_type)
        # handle vanished objects
        if obj is None:
            logger.warn("Skipping object creation for '{}'".format(path))
            continue
        # get the id of the new object
        obj_id = api.get_id(obj)
        # track new ID -> old ID
        ID_MAP[obj_id] = child_id
        # recursively create contents
        create_content_slugs(obj, path + "/", context)


def create_or_get(parent, id, uid, portal_type):
    """Create or get the object
    """
    # return first level objects directly
    if api.is_portal(parent):
        return parent.get(id)
    elif api.get_setup() == parent:
        return parent.get(id)

    # query object by UID
    query = {
        "UID": uid,
        "portal_type": portal_type,
        "path": {
            "query": api.get_path(parent),
        }
    }
    results = api.search(query, "uid_catalog")
    if results:
        return api.get_object(results[0])

    # create object slug
    obj = None
    # get the fti
    types_tool = api.get_tool("portal_types")
    fti = types_tool.getTypeInfo(portal_type)
    # removed
    if not fti:
        return None
    # old style factory
    if fti.product:
        # Create AT Content Slug (we take the UID as ID to avoid clashes)
        obj = _createObjectByType(portal_type, parent, uid)
        # set the old UID to maintain references
        obj._setUID(uid)
        # IMPORTANT: this will generate a new ID by the ID Server config
        obj.processForm()
    else:
        # Create DX Content Slug
        factory = getUtility(IFactory, fti.factory)
        tmp_id = str(uid)
        obj = factory(tmp_id)
        if hasattr(obj, "_setPortalTypeName"):
            obj._setPortalTypeName(fti.getId())
        # set the old UID to maintain references
        setattr(obj, "_plone.uuid", uid)
        notify(ObjectCreatedEvent(obj))
        parent._setObject(tmp_id, obj)
        obj = parent._getOb(api.get_id(obj))

    return obj


def can_export(obj):
    """Decides if the object can be exported or not
    """
    if not api.is_object(obj):
        return False
    if api.get_portal_type(obj) in SKIP_EXPORT_TYPES:
        return False
    return True


def can_import(obj):
    """Decides if the object can be imported or not
    """
    if not api.is_object(obj):
        return False
    return True


def get_id(obj):
    if api.is_portal(obj):
        return SITE_ID
    oid = api.get_id(obj)
    # resolve id from mapping
    rid = ID_MAP.get(oid, oid)
    return rid.replace(" ", "_")


def exportObjects(obj, parent_path, context):
    """ Export subobjects recursively.
    """

    if not can_export(obj):
        logger.info("Skipping export of {}".format(repr(obj)))
        return

    if api.is_portal(obj):
        # explicitly instantiate the exporter to avoid adapter clash of
        # Products.CMFCore.exportimport.properties.PropertiesXMLAdapter
        exporter = SenaiteSiteXMLAdapter(obj, context)
    else:
        exporter = queryMultiAdapter((obj, context), IBody)

    path = "%s%s" % (parent_path, get_id(obj))
    if exporter:
        if exporter.name:
            path = "%s%s" % (parent_path, exporter.name)
        filename = "%s%s" % (path, exporter.suffix)
        body = exporter.body
        if body is not None:
            context.writeDataFile(filename, body, exporter.mime_type)
    else:
        raise ValueError("No exporter found for object: %r" % obj)

    if getattr(obj, "objectValues", False):
        for sub in obj.objectValues():
            exportObjects(sub, path + "/", context)


def importObjects(obj, parent_path, context):
    """ Import subobjects recursively.
    """

    if not can_import(obj):
        logger.info("Skipping import of {}".format(repr(obj)))
        return

    if api.is_portal(obj):
        # explicitly instantiate the importer to avoid adapter clash of
        # Products.CMFCore.exportimport.properties.PropertiesXMLAdapter
        importer = SenaiteSiteXMLAdapter(obj, context)
    else:
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
    installed = qi.isProductInstalled("senaite.core")

    if not installed:
        logger.debug("Nothing to import.")
        return

    if not context.readDataFile("senaite.xml"):
        logger.debug("Nothing to import.")
        return

    # create content slugs for UID references
    create_content_slugs(portal, "", context)

    # import objects
    importObjects(portal, "", context)
