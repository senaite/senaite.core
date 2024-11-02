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

import copy
import json
import re
from collections import OrderedDict
from datetime import datetime
from datetime import timedelta
from itertools import groupby

import Missing
import six
from AccessControl.PermissionRole import rolesForPermissionOn
from AccessControl.Permissions import copy_or_move as CopyOrMove
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims import logger
from bika.lims.interfaces import IClient
from bika.lims.interfaces import IContact
from bika.lims.interfaces import ILabContact
from DateTime import DateTime
from OFS.event import ObjectWillBeMovedEvent
from plone import api as ploneapi
from plone.api.exc import InvalidParameterError
from plone.app.layout.viewlets.content import ContentHistoryView
from plone.behavior.interfaces import IBehaviorAssignable
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.schema import SchemaInvalidatedEvent
from plone.dexterity.utils import addContentToContainer
from plone.dexterity.utils import createContent
from plone.dexterity.utils import resolveDottedName
from plone.i18n.normalizer.interfaces import IFileNameNormalizer
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize.volatile import DontCache
from Products.Archetypes.atapi import DisplayList
from Products.Archetypes.BaseObject import BaseObject
from Products.Archetypes.event import ObjectInitializedEvent
from Products.Archetypes.utils import mapply
from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.permissions import DeleteObjects
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.RegistrationTool import get_member_by_login_name
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import safe_unicode
from Products.PlonePAS.tools.memberdata import MemberData
from Products.ZCatalog.interfaces import ICatalogBrain
from senaite.core.interfaces import ITemporaryObject
from zope import globalrequest
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.container.contained import notifyContainerModified
from zope.event import notify
from zope.interface import alsoProvides
from zope.interface import directlyProvides
from zope.interface import noLongerProvides
from zope.lifecycleevent import ObjectMovedEvent
from zope.publisher.browser import TestRequest
from zope.schema import getFieldsInOrder
from zope.security.interfaces import Unauthorized

"""SENAITE LIMS Framework API

Please see tests/doctests/API.rst for documentation.

Architecural Notes:

Please add only functions that do a single thing for a single object.

Good: `def get_foo(brain_or_object)`
Bad:  `def get_foos(list_of_brain_objects)`

Why?

Because it makes things more complex. You can always use a pattern like this to
achieve the same::

    >>> foos = map(get_foo, list_of_brain_objects)

Please add for all functions a descriptive test in tests/doctests/API.rst.

Thanks.
"""

_marker = object()

UID_RX = re.compile("[a-z0-9]{32}$")

UID_CATALOG = "uid_catalog"
PORTAL_CATALOG = "portal_catalog"


class APIError(Exception):
    """Base exception class for bika.lims errors."""


def get_portal():
    """Get the portal object

    :returns: Portal object
    """
    return ploneapi.portal.getSite()


def get_setup():
    """Fetch the `bika_setup` folder.
    """
    portal = get_portal()
    return portal.get("bika_setup")


def get_bika_setup():
    """Fetch the `bika_setup` folder.
    """
    return get_setup()


def get_senaite_setup():
    """Fetch the new DX `setup` folder.
    """
    portal = get_portal()
    return portal.get("setup")


def create(container, portal_type, *args, **kwargs):
    """Creates an object in Bika LIMS

    This code uses most of the parts from the TypesTool
    see: `Products.CMFCore.TypesTool._constructInstance`

    :param container: container
    :type container: ATContentType/DexterityContentType/CatalogBrain
    :param portal_type: The portal type to create, e.g. "Client"
    :type portal_type: string
    :param title: The title for the new content object
    :type title: string
    :returns: The new created object
    """
    from bika.lims.utils import tmpID

    tmp_id = tmpID()
    id = kwargs.pop("id", "")
    title = kwargs.pop("title", "")

    # get the fti
    types_tool = get_tool("portal_types")
    fti = types_tool.getTypeInfo(portal_type)

    if fti.product:
        # create the AT object
        obj = _createObjectByType(portal_type, container, id or tmp_id)
        # update the object with values
        edit(obj, check_permissions=False, title=title, **kwargs)
        # auto-id if required
        if obj._at_rename_after_creation:
            obj._renameAfterCreation(check_auto_id=True)
        # we are no longer under creation
        obj.unmarkCreationFlag()
        # notify that the object was created
        notify(ObjectInitializedEvent(obj))
    else:
        content = createContent(portal_type, **kwargs)
        content.id = id
        content.title = title
        obj = addContentToContainer(container, content)

    return obj


def copy_object(source, container=None, portal_type=None, *args, **kwargs):
    """Creates a copy of the source object. If container is None, creates the
    copy inside the same container as the source. If portal_type is specified,
    creates a new object of this type, and copies the values from source fields
    to the destination object. Field values sent as kwargs have priority over
    the field values from source.

    :param source: object from which create a copy
    :type source: ATContentType/DexterityContentType/CatalogBrain
    :param container: destination container
    :type container: ATContentType/DexterityContentType/CatalogBrain
    :param portal_type: destination portal type
    :returns: The new created object
    """
    # Prevent circular dependencies
    from security import check_permission
    # Use same container as source unless explicitly set
    source = get_object(source)
    if not container:
        container = get_parent(source)

    # Use same portal type as source unless explicitly set
    if not portal_type:
        portal_type = get_portal_type(source)

    # Extend the fields to skip with defaults
    skip = kwargs.pop("skip", [])
    skip = set(skip)
    skip.update([
        "Products.Archetypes.Field.ComputedField",
        "UID",
        "id",
        "allowDiscussion",
        "contributors",
        "creation_date",
        "creators",
        "effectiveDate",
        "expirationDate",
        "language",
        "location",
        "modification_date",
        "rights",
        "subject",
    ])
    # Build a dict for complexity reduction
    skip = dict([(item, True) for item in skip])

    # Update kwargs with the field values to copy from source
    fields = get_fields(source)
    for field_name, field in fields.items():
        # Prioritize field values passed as kwargs
        if field_name in kwargs:
            continue
        # Skip framework internal fields by name
        if skip.get(field_name, False):
            continue
        # Skip fields of non-suitable types
        if hasattr(field, "getType") and skip.get(field.getType(), False):
            continue
        # Skip readonly fields
        if getattr(field, "readonly", False):
            continue
        # Skip non-readable fields
        perm = getattr(field, "read_permission", View)
        if perm and not check_permission(perm, source):
            continue

        # do not wake-up objects unnecessarily
        if hasattr(field, "getRaw"):
            field_value = field.getRaw(source)
        elif hasattr(field, "get_raw"):
            field_value = field.get_raw(source)
        elif hasattr(field, "getAccessor"):
            accessor = field.getAccessor(source)
            field_value = accessor()
        else:
            field_value = field.get(source)

        # Do a hard copy of value if mutable type
        if isinstance(field_value, (list, dict, set)):
            field_value = copy.deepcopy(field_value)
        kwargs.update({field_name: field_value})

    # Create a copy
    return create(container, portal_type, *args, **kwargs)


def edit(obj, check_permissions=True, **kwargs):
    """Updates the values of object fields with the new values passed-in
    """
    # Prevent circular dependencies
    from security import check_permission
    fields = get_fields(obj)
    for name, value in kwargs.items():
        field = fields.get(name, None)
        if not field:
            continue

        # cannot update readonly fields
        readonly = getattr(field, "readonly", False)
        if readonly:
            raise ValueError("Field '{}' is readonly".format(name))

        # check field writable permission
        if check_permissions:
            perm = getattr(field, "write_permission", ModifyPortalContent)
            if perm and not check_permission(perm, obj):
                raise Unauthorized("Field '{}' is not writeable".format(name))

        # Set the value
        if hasattr(field, "getMutator"):
            mutator = field.getMutator(obj)
            mapply(mutator, value)
        else:
            field.set(obj, value)


def move_object(obj, destination, check_constraints=True):
    """Moves the object to the destination folder

    This function has the same effect as:

        id = obj.getId()
        cp = origin.manage_cutObjects(id)
        destination.manage_pasteObjects(cp)

    but with slightly better performance. The code is mostly grabbed from
    OFS.CopySupport.CopyContainer_pasteObjects

    :param obj: object to move to destination
    :type obj: ATContentType/DexterityContentType/CatalogBrain/UID
    :param destination: destination container
    :type destination: ATContentType/DexterityContentType/CatalogBrain/UID
    :param check_constraints: constraints and permissions must be checked
    :type check_constraints: bool
    :returns: The moved object
    """
    # prevent circular dependencies
    from bika.lims.api.security import check_permission

    obj = get_object(obj)
    destination = get_object(destination)

    # make sure the object is not moved into itself
    if obj == destination:
        raise ValueError("Cannot move object into itself: {}".format(obj))

    # do nothing if destination is the same as origin
    origin = get_parent(obj)
    if origin == destination:
        return obj

    if check_constraints:

        # check origin object has CopyOrMove permission
        if not check_permission(CopyOrMove, obj):
            raise Unauthorized("Cannot move {}".format(obj))

        # check if portal type is allowed in destination object
        portal_type = get_portal_type(obj)
        pt = get_tool("portal_types")
        ti = pt.getTypeInfo(destination)
        if not ti.allowType(portal_type):
            raise ValueError("Disallowed subobject type: %s" % portal_type)

    id = get_id(obj)

    # notify that the object will be copied to destination
    obj._notifyOfCopyTo(destination, op=1)  # noqa

    # notify that the object will be moved to destination
    notify(ObjectWillBeMovedEvent(obj, origin, id, destination, id))

    # effectively move the object from origin to destination
    delete(obj, check_permissions=check_constraints, suppress_events=True)
    obj = aq_base(obj)
    destination._setObject(id, obj, set_owner=0, suppress_events=True)  # noqa
    obj = destination._getOb(id)  # noqa

    # since we used "suppress_events=True", we need to manually notify that the
    # object was moved and containers modified. This also makes the objects to
    # be re-catalogued
    notify(ObjectMovedEvent(obj, origin, id, destination, id))
    notifyContainerModified(origin)
    notifyContainerModified(destination)

    # make ownership implicit if possible, so it acquires the permissions from
    # the container
    obj.manage_changeOwnershipType(explicit=0)

    return obj


def uncatalog_object(obj, recursive=False):
    """Un-catalog the object from all catalogs

    :param obj: object to un-catalog
    :param recursive: recursively uncatalog all child objects
    :type obj: ATContentType/DexterityContentType
    """
    # un-catalog from registered catalogs
    obj.unindexObject()
    # explicitly un-catalog from uid_catalog
    uid_catalog = get_tool("uid_catalog")
    # the uids of uid_catalog are relative paths to portal root
    # see Products.Archetypes.UIDCatalog.UIDResolver.catalog_object
    url = "/".join(obj.getPhysicalPath()[2:])
    uid_catalog.uncatalog_object(url)

    if recursive:
        for child in obj.objectValues():
            uncatalog_object(child, recursive=recursive)


def catalog_object(obj, recursive=False):
    """Re-catalog the object

    :param obj: object to catalog
    :param recursive: recursively catalog all child objects
    :type obj: ATContentType/DexterityContentType
    """
    if is_at_content(obj):
        # explicitly re-catalog AT types at uid_catalog (DX types are
        # automatically reindexed in UID catalog on reindexObject)
        uc = get_tool("uid_catalog")
        # the uids of uid_catalog are relative paths to portal root
        # see Products.Archetypes.UIDCatalog.UIDResolver.catalog_object
        url = "/".join(obj.getPhysicalPath()[2:])
        uc.catalog_object(obj, url)
    obj.reindexObject()

    if recursive:
        for child in obj.objectValues():
            catalog_object(child, recursive=recursive)


def delete(obj, check_permissions=True, suppress_events=False):
    """Deletes the given object

    :param obj: object to un-catalog
    :param check_permissions: whether delete permission must be checked
    :param suppress_events: whether ondelete events have to be fired
    :type obj: ATContentType/DexterityContentType
    """
    from security import check_permission
    if check_permissions and not check_permission(DeleteObjects, obj):
        raise Unauthorized("Do not have permissions to remove this object")

    # un-catalog the object from all catalogs (uid_catalog included)
    uncatalog_object(obj)
    # delete the object
    parent = get_parent(obj)
    parent._delObject(obj.getId(), suppress_events=suppress_events)


def get_tool(name, context=None, default=_marker):
    """Get a portal tool by name

    :param name: The name of the tool, e.g. `senaite_setup_catalog`
    :type name: string
    :param context: A portal object
    :type context: ATContentType/DexterityContentType/CatalogBrain
    :returns: Portal Tool
    """

    # Try first with the context
    if context is not None:
        try:
            context = get_object(context)
            return getToolByName(context, name)
        except (APIError, AttributeError) as e:
            # https://github.com/senaite/bika.lims/issues/396
            logger.warn("get_tool::getToolByName({}, '{}') failed: {} "
                        "-> falling back to plone.api.portal.get_tool('{}')"
                        .format(repr(context), name, repr(e), name))
            return get_tool(name, default=default)

    # Try with the plone api
    try:
        return ploneapi.portal.get_tool(name)
    except InvalidParameterError:
        if default is not _marker:
            if isinstance(default, six.string_types):
                return get_tool(default)
            return default
        fail("No tool named '%s' found." % name)


def fail(msg=None):
    """API LIMS Error
    """
    if msg is None:
        msg = "Reason not given."
    raise APIError("{}".format(msg))


def is_object(brain_or_object):
    """Check if the passed in object is a supported portal content object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: Portal Object
    :returns: True if the passed in object is a valid portal content
    """
    if is_portal(brain_or_object):
        return True
    if is_supermodel(brain_or_object):
        return True
    if is_at_content(brain_or_object):
        return True
    if is_dexterity_content(brain_or_object):
        return True
    if is_brain(brain_or_object):
        return True
    return False


def get_object(brain_object_uid, default=_marker):
    """Get the full content object

    :param brain_object_uid: A catalog brain or content object or uid
    :type brain_object_uid: PortalObject/ATContentType/DexterityContentType
    /CatalogBrain/basestring
    :returns: The full object
    """
    if is_uid(brain_object_uid):
        return get_object_by_uid(brain_object_uid, default=default)
    elif is_supermodel(brain_object_uid):
        return brain_object_uid.instance
    if not is_object(brain_object_uid):
        if default is _marker:
            fail("{} is not supported.".format(repr(brain_object_uid)))
        return default
    if is_brain(brain_object_uid):
        return brain_object_uid.getObject()
    return brain_object_uid


def is_portal(brain_or_object):
    """Checks if the passed in object is the portal root object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: True if the object is the portal root object
    :rtype: bool
    """
    return ISiteRoot.providedBy(brain_or_object)


def is_brain(brain_or_object):
    """Checks if the passed in object is a portal catalog brain

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: True if the object is a catalog brain
    :rtype: bool
    """
    return ICatalogBrain.providedBy(brain_or_object)


def is_supermodel(brain_or_object):
    """Checks if the passed in object is a supermodel

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: True if the object is a catalog brain
    :rtype: bool
    """
    # avoid circular imports
    from senaite.app.supermodel.interfaces import ISuperModel
    return ISuperModel.providedBy(brain_or_object)


def is_dexterity_content(brain_or_object):
    """Checks if the passed in object is a dexterity content type

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: True if the object is a dexterity content type
    :rtype: bool
    """
    return IDexterityContent.providedBy(brain_or_object)


def is_at_content(brain_or_object):
    """Checks if the passed in object is an AT content type

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: True if the object is an AT content type
    :rtype: bool
    """
    return isinstance(brain_or_object, BaseObject)


def is_dx_type(portal_type):
    """Checks if the portal type is DX based

    :param portal_type: The portal type name to check
    :returns: True if the portal type is DX based
    """
    portal_types = get_tool("portal_types")
    fti = portal_types.getTypeInfo(portal_type)
    if fti.product:
        return False
    return True


def is_at_type(portal_type):
    """Checks if the portal type is AT based

    :param portal_type: The portal type name to check
    :returns: True if the portal type is AT based
    """
    return not is_dx_type(portal_type)


def is_folderish(brain_or_object):
    """Checks if the passed in object is folderish

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: True if the object is folderish
    :rtype: bool
    """
    if hasattr(brain_or_object, "is_folderish"):
        if callable(brain_or_object.is_folderish):
            return brain_or_object.is_folderish()
        return brain_or_object.is_folderish
    return IFolderish.providedBy(get_object(brain_or_object))


def get_portal_type(brain_or_object):
    """Get the portal type for this object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Portal type
    :rtype: string
    """
    if not is_object(brain_or_object):
        fail("{} is not supported.".format(repr(brain_or_object)))
    return brain_or_object.portal_type


def get_schema(brain_or_object):
    """Get the schema of the content

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Schema object
    """
    obj = get_object(brain_or_object)
    if is_portal(obj):
        fail("get_schema can't return schema of portal root")
    if is_dexterity_content(obj):
        pt = get_tool("portal_types")
        fti = pt.getTypeInfo(obj.portal_type)
        return fti.lookupSchema()
    if is_at_content(obj):
        return obj.Schema()
    fail("{} has no Schema.".format(brain_or_object))


def get_behaviors(portal_type):
    """List all behaviors

    :param portal_type: DX portal type name
    """
    portal_types = get_tool("portal_types")
    fti = portal_types.getTypeInfo(portal_type)
    if fti.product:
        raise TypeError("Expected DX type, got AT type instead.")
    return fti.behaviors


def enable_behavior(portal_type, behavior_id):
    """Enable behavior

    :param portal_type: DX portal type name
    :param behavior_id: The behavior to enable
    """
    portal_types = get_tool("portal_types")
    fti = portal_types.getTypeInfo(portal_type)
    if fti.product:
        raise TypeError("Expected DX type, got AT type instead.")

    if behavior_id not in fti.behaviors:
        fti.behaviors += (behavior_id, )
        # invalidate schema cache
        notify(SchemaInvalidatedEvent(portal_type))


def disable_behavior(portal_type, behavior_id):
    """Disable behavior

    :param portal_type: DX portal type name
    :param behavior_id: The behavior to disable
    """
    portal_types = get_tool("portal_types")
    fti = portal_types.getTypeInfo(portal_type)
    if fti.product:
        raise TypeError("Expected DX type, got AT type instead.")
    fti.behaviors = tuple(filter(lambda b: b != behavior_id, fti.behaviors))
    # invalidate schema cache
    notify(SchemaInvalidatedEvent(portal_type))


def get_fields(brain_or_object):
    """Get a name to field mapping of the object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Mapping of name -> field
    :rtype: OrderedDict
    """
    obj = get_object(brain_or_object)
    schema = get_schema(obj)
    if is_dexterity_content(obj):
        # get the fields directly provided by the interface
        fields = getFieldsInOrder(schema)
        # append the fields coming from behaviors
        behavior_assignable = IBehaviorAssignable(obj)
        if behavior_assignable:
            behaviors = behavior_assignable.enumerateBehaviors()
            for behavior in behaviors:
                fields.extend(getFieldsInOrder(behavior.interface))
        return OrderedDict(fields)
    return OrderedDict(schema)


def get_id(brain_or_object):
    """Get the Plone ID for this object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Plone ID
    :rtype: string
    """
    if is_brain(brain_or_object):
        if base_hasattr(brain_or_object, "getId"):
            return brain_or_object.getId
        if base_hasattr(brain_or_object, "id"):
            return brain_or_object.id
    return get_object(brain_or_object).getId()


def get_title(brain_or_object):
    """Get the Title for this object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Title
    :rtype: string
    """
    if is_brain(brain_or_object) and base_hasattr(brain_or_object, "Title"):
        return brain_or_object.Title
    return get_object(brain_or_object).Title()


def get_description(brain_or_object):
    """Get the Title for this object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Title
    :rtype: string
    """
    if is_brain(brain_or_object) \
            and base_hasattr(brain_or_object, "Description"):
        return brain_or_object.Description
    return get_object(brain_or_object).Description()


def get_uid(brain_or_object):
    """Get the Plone UID for this object

    :param brain_or_object: A single catalog brain or content object or an UID
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Plone UID
    :rtype: string
    """
    if is_uid(brain_or_object):
        return brain_or_object
    if is_portal(brain_or_object):
        return '0'
    if is_brain(brain_or_object) and base_hasattr(brain_or_object, "UID"):
        return brain_or_object.UID
    return get_object(brain_or_object).UID()


def get_url(brain_or_object):
    """Get the absolute URL for this object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Absolute URL
    :rtype: string
    """
    if is_brain(brain_or_object) and base_hasattr(brain_or_object, "getURL"):
        return brain_or_object.getURL()
    return get_object(brain_or_object).absolute_url()


def get_icon(thing, html_tag=True):
    """Get the icon of the content object

    :param thing: A single catalog brain, content object or portal_type
    :type thing: ATContentType/DexterityContentType/CatalogBrain/String
    :param html_tag: A value of 'True' returns the HTML tag, else the image url
    :type html_tag: bool
    :returns: HTML '<img>' tag if 'html_tag' is True else the image url
    :rtype: string
    """
    portal_type = thing
    if is_object(thing):
        portal_type = get_portal_type(thing)

    # Manual approach, because `plone.app.layout.getIcon` does not reliable
    # work for Contents coming from other catalogs than the
    # `portal_catalog`
    portal_types = get_tool("portal_types")
    fti = portal_types.getTypeInfo(portal_type)
    if not fti:
        fail("No type info for {}".format(repr(thing)))
    icon = fti.getIcon()
    if not icon:
        return ""
    url = "%s/%s" % (get_url(get_portal()), icon)
    if not html_tag:
        return url

    # build the img element
    if is_object(thing):
        title = get_title(thing)
    else:
        title = fti.Title()
    tag = '<img width="16" height="16" src="{url}" title="{title}" />'
    return tag.format(url=url, title=title)


def get_object_by_uid(uid, default=_marker):
    """Find an object by a given UID

    :param uid: The UID of the object to find
    :type uid: string
    :returns: Found Object or None
    """

    # nothing to do here
    if not uid:
        if default is not _marker:
            return default
        fail("get_object_by_uid requires UID as first argument; got {} instead"
             .format(uid))

    # we defined the portal object UID to be '0'::
    if uid == '0':
        return get_portal()

    brain = get_brain_by_uid(uid)

    if brain is None:
        if default is not _marker:
            return default
        fail("No object found for UID {}".format(uid))

    return get_object(brain)


def get_brain_by_uid(uid, default=None):
    """Query a brain by a given UID

    :param uid: The UID of the object to find
    :type uid: string
    :returns: ZCatalog brain or None
    """
    if not is_uid(uid):
        return default

    # we try to find the object with the UID catalog
    uc = get_tool(UID_CATALOG)

    # try to find the object with the reference catalog first
    brains = uc(UID=uid)
    if len(brains) != 1:
        return default
    return brains[0]


def get_object_by_path(path, default=_marker):
    """Find an object by a given physical path or absolute_url

    :param path: The physical path of the object to find
    :type path: string
    :returns: Found Object or None
    """

    # nothing to do here
    if not path:
        if default is not _marker:
            return default
        fail("get_object_by_path first argument must be a path; {} received"
             .format(path))

    portal = get_portal()
    portal_path = get_path(portal)
    portal_url = get_url(portal)

    # ensure we have a physical path
    if path.startswith(portal_url):
        request = get_request()
        path = "/".join(request.physicalPathFromURL(path))

    if not path.startswith(portal_path):
        if default is not _marker:
            return default
        fail("Not a physical path inside the portal.")

    if path == portal_path:
        return portal

    return portal.restrictedTraverse(path, default)


def get_path(brain_or_object):
    """Calculate the physical path of this object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Physical path of the object
    :rtype: string
    """
    if is_brain(brain_or_object):
        return brain_or_object.getPath()
    return "/".join(get_object(brain_or_object).getPhysicalPath())


def get_parent_path(brain_or_object):
    """Calculate the physical parent path of this object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Physical path of the parent object
    :rtype: string
    """
    if is_portal(brain_or_object):
        return get_path(get_portal())
    if is_brain(brain_or_object):
        path = get_path(brain_or_object)
        return path.rpartition("/")[0]
    return get_path(get_object(brain_or_object).aq_parent)


def get_parent(brain_or_object, **kw):
    """Locate the parent object of the content/catalog brain

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :param catalog_search: Use a catalog query to find the parent object
    :type catalog_search: bool
    :returns: parent object
    :rtype: ATContentType/DexterityContentType/PloneSite/CatalogBrain
    """

    if is_portal(brain_or_object):
        return get_portal()

    # BBB: removed `catalog_search` keyword
    if kw:
        logger.warn("API function `get_parent` no longer support keywords.")

    return get_object(brain_or_object).aq_parent


def search(query, catalog=_marker):
    """Search for objects.

    :param query: A suitable search query.
    :type query: dict
    :param catalog: A single catalog id or a list of catalog ids
    :type catalog: str/list
    :returns: Search results
    :rtype: List of ZCatalog brains
    """

    # query needs to be a dictionary
    if not isinstance(query, dict):
        fail("Catalog query needs to be a dictionary")

    # Portal types to query
    portal_types = query.get("portal_type", [])
    # We want the portal_type as a list
    if not isinstance(portal_types, (tuple, list)):
        portal_types = [portal_types]

    # The catalogs used for the query
    catalogs = []

    # The user did **not** specify a catalog
    if catalog is _marker:
        # Find the registered catalogs for the queried portal types
        for portal_type in portal_types:
            # Just get the first registered/default catalog
            catalogs.append(get_catalogs_for(
                portal_type, default=UID_CATALOG)[0])
    else:
        # User defined catalogs
        if isinstance(catalog, (list, tuple)):
            catalogs.extend(map(get_tool, catalog))
        else:
            catalogs.append(get_tool(catalog))

    # Cleanup: Avoid duplicate catalogs
    catalogs = list(set(catalogs)) or [get_uid_catalog()]

    # We only support **single** catalog queries
    if len(catalogs) > 1:
        fail("Multi Catalog Queries are not supported!")

    return catalogs[0](query)


def safe_getattr(brain_or_object, attr, default=_marker):
    """Return the attribute value

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :param attr: Attribute name
    :type attr: str
    :returns: Attribute value
    :rtype: obj
    """
    try:
        value = getattr(brain_or_object, attr, _marker)
        if value is _marker:
            if default is not _marker:
                return default
            fail("Attribute '{}' not found.".format(attr))
        if callable(value):
            return value()
        return value
    except Unauthorized:
        if default is not _marker:
            return default
        fail("You are not authorized to access '{}' of '{}'.".format(
            attr, repr(brain_or_object)))


def get_uid_catalog():
    """Get the UID catalog tool

    :returns: UID Catalog Tool
    """
    return get_tool(UID_CATALOG)


def get_portal_catalog():
    """Get the portal catalog tool

    :returns: Portal Catalog Tool
    """
    return get_tool(PORTAL_CATALOG)


def get_review_history(brain_or_object, rev=True):
    """Get the review history for the given brain or context.

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Workflow history
    :rtype: [{}, ...]
    """
    obj = get_object(brain_or_object)
    review_history = []
    try:
        workflow = get_tool("portal_workflow")
        review_history = workflow.getInfoFor(obj, 'review_history')
    except WorkflowException as e:
        message = str(e)
        logger.error("Cannot retrieve review_history on {}: {}".format(
            obj, message))
    if not isinstance(review_history, (list, tuple)):
        logger.error("get_review_history: expected list, received {}".format(
            review_history))
        review_history = []

    if isinstance(review_history, tuple):
        # Products.CMFDefault.DefaultWorkflow.getInfoFor always returns a
        # tuple when "review_history" is passed in:
        # https://github.com/zopefoundation/Products.CMFDefault/blob/master/Products/CMFDefault/DefaultWorkflow.py#L244
        #
        # On the other hand, Products.DCWorkflow.getInfoFor relies on
        # Expression.StateChangeInfo, that always returns a list, except when no
        # review_history is found:
        # https://github.com/zopefoundation/Products.DCWorkflow/blob/master/Products/DCWorkflow/DCWorkflow.py#L310
        # https://github.com/zopefoundation/Products.DCWorkflow/blob/master/Products/DCWorkflow/Expression.py#L94
        review_history = list(review_history)

    if rev is True:
        review_history.reverse()
    return review_history


def get_revision_history(brain_or_object):
    """Get the revision history for the given brain or context.

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Workflow history
    :rtype: obj
    """
    obj = get_object(brain_or_object)
    chv = ContentHistoryView(obj, safe_getattr(obj, "REQUEST", None))
    return chv.fullHistory()


def get_workflows_for(brain_or_object):
    """Get the assigned workflows for the given brain or context.

    Note: This function supports also the portal_type as parameter.

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Assigned Workflows
    :rtype: tuple
    """
    workflow = ploneapi.portal.get_tool("portal_workflow")
    if isinstance(brain_or_object, six.string_types):
        return workflow.getChainFor(brain_or_object)
    obj = get_object(brain_or_object)
    return workflow.getChainFor(obj)


def get_workflow_status_of(brain_or_object, state_var="review_state"):
    """Get the current workflow status of the given brain or context.

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :param state_var: The name of the state variable
    :type state_var: string
    :returns: Status
    :rtype: str
    """
    # Try to get the state from the catalog brain first
    if is_brain(brain_or_object):
        if state_var in brain_or_object.schema():
            return brain_or_object[state_var]

    # Retrieve the sate from the object
    workflow = get_tool("portal_workflow")
    obj = get_object(brain_or_object)
    return workflow.getInfoFor(ob=obj, name=state_var, default='')


def get_previous_worfklow_status_of(brain_or_object, skip=None, default=None):
    """Get the previous workflow status of the object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :param skip: Workflow states to skip
    :type skip: tuple/list
    :returns: status
    :rtype: str
    """

    skip = isinstance(skip, (list, tuple)) and skip or []
    history = get_review_history(brain_or_object)

    # Remove consecutive duplicates, some transitions might happen more than
    # once consecutively (e.g. publish)
    history = map(lambda i: i[0], groupby(history))

    for num, item in enumerate(history):
        # skip the current history entry
        if num == 0:
            continue
        status = item.get("review_state")
        if status in skip:
            continue
        return status
    return default


def get_creation_date(brain_or_object):
    """Get the creation date of the brain or object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Creation date
    :rtype: DateTime
    """
    created = getattr(brain_or_object, "created", None)
    if created is None:
        fail("Object {} has no creation date ".format(
             repr(brain_or_object)))
    if callable(created):
        return created()
    return created


def get_modification_date(brain_or_object):
    """Get the modification date of the brain or object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Modification date
    :rtype: DateTime
    """
    modified = getattr(brain_or_object, "modified", None)
    if modified is None:
        fail("Object {} has no modification date ".format(
             repr(brain_or_object)))
    if callable(modified):
        return modified()
    return modified


def get_review_status(brain_or_object):
    """Get the `review_state` of an object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Value of the review_status variable
    :rtype: String
    """
    if is_brain(brain_or_object) \
       and base_hasattr(brain_or_object, "review_state"):
        return brain_or_object.review_state
    return get_workflow_status_of(brain_or_object, state_var="review_state")


def is_active(brain_or_object):
    """Check if the workflow state of the object is 'inactive' or 'cancelled'.

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: False if the object is in the state 'inactive' or 'cancelled'
    :rtype: bool
    """
    if get_review_status(brain_or_object) in ["cancelled", "inactive"]:
        return False
    return True


def get_fti(portal_type, default=None):
    """Lookup the Dynamic Filetype Information for the given portal_type

    :param portal_type: The portal type to get the FTI for
    :returns: FTI or default value
    """
    if not is_string(portal_type):
        return default
    portal_types = get_tool("portal_types")
    fti = portal_types.getTypeInfo(portal_type)
    return fti or default


def get_catalogs_for(brain_or_object, default=PORTAL_CATALOG):
    """Get all registered catalogs for the given portal_type, catalog brain or
    content object

    NOTE: We pass in the `portal_catalog` as default in subsequent calls to
          work around the missing `uid_catalog` during snapshot creation when
          installing a fresh site!

    :param brain_or_object: The portal_type, a catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: List of supported catalogs
    :rtype: list
    """

    # only handle catalog lookups by portal_type internally
    if is_uid(brain_or_object) or is_object(brain_or_object):
        obj = get_object(brain_or_object)
        portal_type = get_portal_type(obj)
        return get_catalogs_for(portal_type)

    catalogs = []

    if not is_string(brain_or_object):
        raise APIError("Expected a portal_type string, got <%s>"
                       % type(brain_or_object))

    # at this point the brain_or_object is a portal_type
    portal_type = brain_or_object

    # check static portal_type -> catalog mapping first
    from senaite.core.catalog import get_catalogs_by_type
    catalogs = get_catalogs_by_type(portal_type)

    # no catalogs in static mapping
    # => Lookup catalogs by FTI
    if len(catalogs) == 0:
        fti = get_fti(portal_type)
        if fti.product:
            # AT content type
            # => Looup via archetype_tool
            archetype_tool = get_tool("archetype_tool")
            catalogs = archetype_tool.catalog_map.get(portal_type) or []
        else:
            # DX content type
            # => resolve the `_catalogs` attribute from the class
            klass = resolveDottedName(fti.klass)
            # XXX: Refactor multi-catalog behavior to not rely
            #      on this hidden `_catalogs` attribute!
            catalogs = getattr(klass, "_catalogs", [])

    # fetch the catalog objects
    catalogs = filter(None, map(lambda cid: get_tool(cid, None), catalogs))

    if len(catalogs) == 0:
        return [get_tool(default, default=PORTAL_CATALOG)]

    return list(catalogs)


def get_transitions_for(brain_or_object):
    """List available workflow transitions for all workflows

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: All possible available and allowed transitions
    :rtype: list[dict]
    """
    workflow = get_tool('portal_workflow')
    transitions = []
    instance = get_object(brain_or_object)
    for wfid in get_workflows_for(brain_or_object):
        wf = workflow[wfid]
        tlist = wf.getTransitionsFor(instance)
        transitions.extend([t for t in tlist if t not in transitions])
    return transitions


def do_transition_for(brain_or_object, transition):
    """Performs a workflow transition for the passed in object.

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: The object where the transtion was performed
    """
    if not isinstance(transition, six.string_types):
        fail("Transition type needs to be string, got '%s'" % type(transition))
    obj = get_object(brain_or_object)
    try:
        ploneapi.content.transition(obj, transition)
    except ploneapi.exc.InvalidParameterError as e:
        fail("Failed to perform transition '{}' on {}: {}".format(
             transition, obj, str(e)))
    return obj


def get_roles_for_permission(permission, brain_or_object):
    """Get a list of granted roles for the given permission on the object.

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Roles for the given Permission
    :rtype: list
    """
    obj = get_object(brain_or_object)
    allowed = set(rolesForPermissionOn(permission, obj))
    return sorted(allowed)


def is_versionable(brain_or_object, policy='at_edit_autoversion'):
    """Checks if the passed in object is versionable.

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: True if the object is versionable
    :rtype: bool
    """
    pr = get_tool("portal_repository")
    obj = get_object(brain_or_object)
    return pr.supportsPolicy(obj, 'at_edit_autoversion') \
        and pr.isVersionable(obj)


def get_version(brain_or_object):
    """Get the version of the current object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: The current version of the object, or None if not available
    :rtype: int or None
    """
    obj = get_object(brain_or_object)
    if not is_versionable(obj):
        return None
    return getattr(aq_base(obj), "version_id", 0)


def get_view(name, context=None, request=None, default=None):
    """Get the view by name

    :param name: The name of the view
    :type name: str
    :param context: The context to query the view
    :type context: ATContentType/DexterityContentType/CatalogBrain
    :param request: The request to query the view
    :type request: HTTPRequest object
    :returns: HTTP Request
    :rtype: Products.Five.metaclass View object
    """
    context = context or get_portal()
    request = request or get_request() or None
    view = queryMultiAdapter((get_object(context), request), name=name)
    if view is None:
        return default
    return view


def get_request():
    """Get the global request object

    :returns: HTTP Request
    :rtype: HTTPRequest object
    """
    return globalrequest.getRequest()


def get_test_request():
    """Get the TestRequest object
    """
    request = TestRequest()
    directlyProvides(request, IAttributeAnnotatable)
    return request


def get_group(group_or_groupname):
    """Return Plone Group

    :param group_or_groupname: Plone group or the name of the group
    :type groupname:  GroupData/str
    :returns: Plone GroupData
    """
    if not group_or_groupname:

        return None
    if hasattr(group_or_groupname, "_getGroup"):
        return group_or_groupname
    gtool = get_tool("portal_groups")
    return gtool.getGroupById(group_or_groupname)


def get_user(user_or_username):
    """Return Plone User

    :param user_or_username: Plone user or user id
    :returns: Plone MemberData
    """
    user = None
    if isinstance(user_or_username, MemberData):
        user = user_or_username
    if isinstance(user_or_username, six.string_types):
        user = get_member_by_login_name(get_portal(), user_or_username, False)
    return user


def get_user_properties(user_or_username):
    """Return User Properties

    :param user_or_username: Plone group identifier
    :returns: Plone MemberData
    """
    user = get_user(user_or_username)
    if user is None:
        return {}
    if not callable(user.getUser):
        return {}
    out = {}
    plone_user = user.getUser()
    for sheet in plone_user.listPropertysheets():
        ps = plone_user.getPropertysheet(sheet)
        out.update(dict(ps.propertyItems()))
    return out


def get_users_by_roles(roles=None):
    """Search Plone users by their roles

    :param roles: Plone role name or list of roles
    :type roles:  list/str
    :returns: List of Plone users having the role(s)
    """
    if not isinstance(roles, (tuple, list)):
        roles = [roles]
    mtool = get_tool("portal_membership")
    return mtool.searchForMembers(roles=roles)


def get_current_user():
    """Returns the current logged in user

    :returns: Current User
    """
    return ploneapi.user.get_current()


def get_user_contact(user, contact_types=['Contact', 'LabContact']):
    """Returns the associated contact of a Plone user

    If the user passed in has no contact associated, return None.
    The `contact_types` parameter filter the portal types for the search.

    :param: Plone user
    :contact_types: List with the contact portal types to search
    :returns: Contact associated to the Plone user or None
    """
    if not user:
        return None

    from senaite.core.catalog import CONTACT_CATALOG  # Avoid circular import
    query = {"portal_type": contact_types, "getUsername": user.getId()}
    brains = search(query, catalog=CONTACT_CATALOG)
    if not brains:
        return None

    if len(brains) > 1:
        # Oops, the user has multiple contacts assigned, return None
        contacts = map(lambda c: c.Title, brains)
        err_msg = "User '{}' is bound to multiple Contacts '{}'"
        err_msg = err_msg.format(user.getId(), ','.join(contacts))
        logger.error(err_msg)
        return None

    return get_object(brains[0])


def get_user_client(user_or_contact):
    """Returns the client of the contact of a Plone user

    If the user passed in has no contact or does not belong to any client,
    returns None.

    :param: Plone user or contact
    :returns: Client the contact of the Plone user belongs to
    """
    if not user_or_contact or ILabContact.providedBy(user_or_contact):
        # Lab contacts cannot belong to a client
        return None

    if not IContact.providedBy(user_or_contact):
        contact = get_user_contact(user_or_contact, contact_types=['Contact'])
        if IContact.providedBy(contact):
            return get_user_client(contact)
        return None

    client = get_parent(user_or_contact)
    if client and IClient.providedBy(client):
        return client

    return None


def get_user_fullname(user_or_contact):
    """Returns the fullname of the contact or Plone user.

    If the user has a linked contact, the fullname of the contact has priority
    over the value of the fullname property from the user

    :param: Plone user or contact
    :returns: Fullname of the contact or user
    """
    if IContact.providedBy(user_or_contact):
        return user_or_contact.getFullname()

    user = get_user(user_or_contact)
    if not user:
        return ""

    # contact's fullname has priority over user's
    contact = get_user_contact(user)
    if not contact:
        return user.getProperty("fullname")

    return contact.getFullname()


def get_user_email(user_or_contact):
    """Returns the email of the contact or Plone user.
    If the user has a linked contact, the email of the contact has priority
    over the value of the email property from the user
    :param: Plone user or contact
    :returns: Fullname of the contact or user
    """
    if IContact.providedBy(user_or_contact):
        return user_or_contact.getEmailAddress()

    user = get_user(user_or_contact)
    if not user:
        return ""

    # contact's email has priority over user's
    contact = get_user_contact(user)
    if not contact:
        return user.getProperty("email", default="")

    return contact.getEmailAddress()


def get_current_client():
    """Returns the current client the current logged in user belongs to, if any

    :returns: Client the current logged in user belongs to or None
    """
    return get_user_client(get_current_user())


def get_cache_key(brain_or_object):
    """Generate a cache key for a common brain or object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Cache Key
    :rtype: str
    """
    key = [
        get_portal_type(brain_or_object),
        get_id(brain_or_object),
        get_uid(brain_or_object),
        # handle different domains gracefully
        get_url(brain_or_object),
        # Return the microsecond since the epoch in GMT
        get_modification_date(brain_or_object).micros(),
    ]
    return "-".join(map(lambda x: str(x), key))


def bika_cache_key_decorator(method, self, brain_or_object):
    """Bika cache key decorator usable for

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Cache Key
    :rtype: str
    """
    if brain_or_object is None:
        raise DontCache
    return get_cache_key(brain_or_object)


def normalize_id(string):
    """Normalize the id

    :param string: A string to normalize
    :type string: str
    :returns: Normalized ID
    :rtype: str
    """
    if not isinstance(string, six.string_types):
        fail("Type of argument must be string, found '{}'"
             .format(type(string)))
    # get the id nomalizer utility
    normalizer = getUtility(IIDNormalizer).normalize
    return normalizer(string)


def normalize_filename(string):
    """Normalize the filename

    :param string: A string to normalize
    :type string: str
    :returns: Normalized ID
    :rtype: str
    """
    if not isinstance(string, six.string_types):
        fail("Type of argument must be string, found '{}'"
             .format(type(string)))
    # get the file nomalizer utility
    normalizer = getUtility(IFileNameNormalizer).normalize
    return normalizer(string)


def is_uid(uid, validate=False):
    """Checks if the passed in uid is a valid UID

    :param uid: The uid to check
    :param validate: If False, checks if uid is a valid 23 alphanumeric uid. If
    True, also verifies if a brain exists for the uid passed in
    :type uid: string
    :return: True if a valid uid
    :rtype: bool
    """
    if not isinstance(uid, six.string_types):
        return False
    if uid == '0':
        return True
    if len(uid) != 32:
        return False
    if not UID_RX.match(uid):
        return False
    if not validate:
        return True

    # Check if a brain for this uid exists
    uc = get_tool('uid_catalog')
    brains = uc(UID=uid)
    if brains:
        assert (len(brains) == 1)
    return len(brains) > 0


def is_date(date):
    """Checks if the passed in value is a valid Zope's DateTime

    :param date: The date to check
    :type date: DateTime
    :return: True if a valid date
    :rtype: bool
    """
    if not date:
        return False
    return isinstance(date, (DateTime, datetime))


def to_date(value, default=None):
    """Tries to convert the passed in value to Zope's DateTime

    :param value: The value to be converted to a valid DateTime
    :type value: str, DateTime or datetime
    :return: The DateTime representation of the value passed in or default
    """

    # cannot use bika.lims.deprecated (circular dependencies)
    import warnings
    warnings.simplefilter("always", DeprecationWarning)
    warn = "Deprecated: use senaite.core.api.dtime.to_DT instead"
    warnings.warn(warn, category=DeprecationWarning, stacklevel=2)
    warnings.simplefilter("default", DeprecationWarning)

    # prevent circular dependencies
    from senaite.core.api.dtime import to_DT
    date = to_DT(value)
    if not date:
        return to_DT(default)
    return date


def to_minutes(days=0, hours=0, minutes=0, seconds=0, milliseconds=0,
               round_to_int=True):
    """Returns the computed total number of minutes
    """
    total = float(days)*24*60 + float(hours)*60 + float(minutes) + \
        float(seconds)/60 + float(milliseconds)/1000/60
    return int(round(total)) if round_to_int else total


def to_dhm_format(days=0, hours=0, minutes=0, seconds=0, milliseconds=0):
    """Returns a representation of time in a string in xd yh zm format
    """
    minutes = to_minutes(days=days, hours=hours, minutes=minutes,
                         seconds=seconds, milliseconds=milliseconds)
    delta = timedelta(minutes=int(round(minutes)))
    d = delta.days
    h = delta.seconds // 3600
    m = (delta.seconds // 60) % 60
    m = m and "{}m ".format(str(m)) or ""
    d = d and "{}d ".format(str(d)) or ""
    if m and d:
        h = "{}h ".format(str(h))
    else:
        h = h and "{}h ".format(str(h)) or ""
    return "".join([d, h, m]).strip()


def to_int(value, default=_marker):
    """Tries to convert the value to int.
    Truncates at the decimal point if the value is a float

    :param value: The value to be converted to an int
    :return: The resulting int or default
    """
    if is_floatable(value):
        value = to_float(value)
    try:
        return int(value)
    except (TypeError, ValueError):
        if default is None:
            return default
        if default is not _marker:
            return to_int(default)
        fail("Value %s cannot be converted to int" % repr(value))


def is_floatable(value):
    """Checks if the passed in value is a valid floatable number

    :param value: The value to be evaluated as a float number
    :type value: str, float, int
    :returns: True if is a valid float number
    :rtype: bool"""
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False


def to_float(value, default=_marker):
    """Converts the passed in value to a float number

    :param value: The value to be converted to a floatable number
    :type value: str, float, int
    :returns: The float number representation of the passed in value
    :rtype: float
    """
    if not is_floatable(value):
        if default is not _marker:
            return to_float(default)
        fail("Value %s is not floatable" % repr(value))
    return float(value)


def float_to_string(value, default=_marker):
    """Convert a float value to string without exponential notation

    This function preserves the whole fraction

    :param value: The float value to be converted to a string
    :type value: str, float, int
    :returns: String representation of the float w/o exponential notation
    :rtype: str
    """
    if not is_floatable(value):
        if default is not _marker:
            return default
        fail("Value %s is not floatable" % repr(value))

    # Leave floatable string values unchanged
    if isinstance(value, six.string_types):
        return value

    value = float(value)
    str_value = str(value)

    if "." in str_value:
        # might be something like 1.23e-26
        front, back = str_value.split(".")
    else:
        # or 1e-07 for 0.0000001
        back = str_value

    if "e-" in back:
        fraction, zeros = back.split("e-")
        # we want to cover the faction and the zeros
        precision = len(fraction) + int(zeros)
        template = "{:.%df}" % precision
        str_value = template.format(value)
    elif "e+" in back:
        # positive numbers, e.g. 1e+16 don't need a fractional part
        str_value = "{:.0f}".format(value)

    # cut off trailing zeros
    if "." in str_value:
        str_value = str_value.rstrip("0").rstrip(".")

    return str_value


def to_searchable_text_metadata(value):
    """Parse the given metadata value to searchable text

    :param value: The raw value of the metadata column
    :returns: Searchable and translated unicode value or None
    """
    if not value:
        return u""
    if value is Missing.Value:
        return u""
    if is_uid(value):
        return u""
    if isinstance(value, (bool)):
        return u""
    if isinstance(value, (list, tuple)):
        values = map(to_searchable_text_metadata, value)
        values = filter(None, values)
        return " ".join(values)
    if isinstance(value, dict):
        return to_searchable_text_metadata(value.values())
    if is_date(value):
        from senaite.core.api.dtime import date_to_string
        return date_to_string(value, "%Y-%m-%d")
    if is_at_content(value):
        return to_searchable_text_metadata(get_title(value))
    if not isinstance(value, six.string_types):
        value = str(value)
    return safe_unicode(value)


def get_registry_record(name, default=None):
    """Returns the value of a registry record

    :param name: [required] name of the registry record
    :type name: str
    :param default: The value returned if the record is not found
    :type default: anything
    :returns: value of the registry record
    """
    return ploneapi.portal.get_registry_record(name, default=default)


def to_display_list(pairs, sort_by="key", allow_empty=True):
    """Create a Plone DisplayList from list items

    :param pairs: list of key, value pairs
    :param sort_by: Sort the items either by key or value
    :param allow_empty: Allow to select an empty value
    :returns: Plone DisplayList
    """
    dl = DisplayList()

    if isinstance(pairs, six.string_types):
        pairs = [pairs, pairs]
    for pair in pairs:
        # pairs is a list of lists -> add each pair
        if isinstance(pair, (tuple, list)):
            dl.add(*pair)
        # pairs is just a single pair -> add it and stop
        if isinstance(pair, six.string_types):
            dl.add(*pairs)
            break

    # add the empty option
    if allow_empty:
        dl.add("", "")

    # sort by key/value
    if sort_by == "key":
        dl = dl.sortedByKey()
    elif sort_by == "value":
        dl = dl.sortedByValue()

    return dl


def text_to_html(text, wrap="p", encoding="utf8"):
    """Convert `\n` sequences in the text to HTML `\n`

    :param text: Plain text to convert
    :param wrap: Toggle to wrap the text in a
    :returns: HTML converted and encoded text
    """
    if not text:
        return ""
    # handle text internally as unicode
    text = safe_unicode(text)
    # replace newline characters with HTML entities
    html = text.replace("\n", "<br/>")
    if wrap:
        html = u"<{tag}>{html}</{tag}>".format(
            tag=wrap, html=html)
    # return encoded html
    return html.encode(encoding)


def to_utf8(string, default=_marker):
    """Encode string to UTF8

    :param string: String to be encoded to UTF8
    :returns: UTF8 encoded string
    """
    if not isinstance(string, six.string_types):
        if default is _marker:
            fail("Expected string type, got '%s'" % type(string))
        return default
    return safe_unicode(string).encode("utf8")


def is_temporary(obj):
    """Returns whether the given object is temporary or not

    :param obj: the object to evaluate
    :returns: True if the object is temporary
    """
    if ITemporaryObject.providedBy(obj):
        return True

    obj_id = getattr(aq_base(obj), "id", None)
    if obj_id is None or UID_RX.match(obj_id):
        return True

    parent = aq_parent(aq_inner(obj))
    if not parent:
        return True

    parent_id = getattr(aq_base(parent), "id", None)
    if parent_id is None or UID_RX.match(parent_id):
        return True

    # Checks to see if we are created inside the portal_factory.
    # This might also happen for DX types in senaite.databox!
    meta_type = getattr(aq_base(parent), "meta_type", "")
    if meta_type == "TempFolder":
        return True

    return False


def mark_temporary(brain_or_object):
    """Mark the object as temporary
    """
    obj = get_object(brain_or_object)
    alsoProvides(obj, ITemporaryObject)


def unmark_temporary(brain_or_object):
    """Unmark the object as temporary
    """
    obj = get_object(brain_or_object)
    noLongerProvides(obj, ITemporaryObject)


def is_string(thing):
    """Checks if the passed in object is a string type

    :param thing: object to test
    :returns: True if the object is a string
    """
    return isinstance(thing, six.string_types)


def is_list(thing):
    """Checks if the passed in object is a list type

    :param thing: object to test
    :returns: True if the object is a list
    """
    return isinstance(thing, list)


def is_list_iterable(thing):
    """Checks if the passed in object can be iterated like a list

    :param thing: object to test
    :returns: True if the object is a list, tuple or set
    """
    return isinstance(thing, (list, tuple, set))


def parse_json(thing, default=""):
    """Parse from JSON

    :param thing: thing to parse
    :param default: value to return if cannot parse
    :returns: the object representing the JSON or default
    """
    try:
        return json.loads(thing)
    except (TypeError, ValueError):
        return default


def to_list(value):
    """Converts the value to a list

    :param value: the value to be represented as a list
    :returns: a list that represents or contains the value
    """
    if is_string(value):
        val = parse_json(value)
        if isinstance(val, (list, tuple, set)):
            value = val
    if not isinstance(value, (list, tuple, set)):
        value = [value]
    return list(value)
