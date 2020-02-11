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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

import re
from collections import OrderedDict
from datetime import datetime
from datetime import timedelta

import Missing
from AccessControl.PermissionRole import rolesForPermissionOn
from Acquisition import aq_base
from bika.lims import logger
from bika.lims.interfaces import IClient
from bika.lims.interfaces import IContact
from bika.lims.interfaces import ILabContact
from DateTime import DateTime
from DateTime.interfaces import DateTimeError
from plone import api as ploneapi
from plone.api.exc import InvalidParameterError
from plone.app.layout.viewlets.content import ContentHistoryView
from plone.behavior.interfaces import IBehaviorAssignable
from plone.dexterity.interfaces import IDexterityContent
from plone.i18n.normalizer.interfaces import IFileNameNormalizer
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize.volatile import DontCache
from Products.Archetypes.atapi import DisplayList
from Products.Archetypes.BaseObject import BaseObject
from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.RegistrationTool import get_member_by_login_name
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import safe_unicode
from Products.PlonePAS.tools.memberdata import MemberData
from Products.ZCatalog.interfaces import ICatalogBrain
from zope import globalrequest
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component.interfaces import IFactory
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from zope.lifecycleevent import modified
from zope.schema import getFieldsInOrder
from zope.security.interfaces import Unauthorized

"""SENAITE LIMS Framework API

Please see bika.lims/docs/API.rst for documentation.

Architecural Notes:

Please add only functions that do a single thing for a single object.

Good: `def get_foo(brain_or_object)`
Bad:  `def get_foos(list_of_brain_objects)`

Why?

Because it makes things more complex. You can always use a pattern like this to
achieve the same::

    >>> foos = map(get_foo, list_of_brain_objects)

Please add for all of your functions a descriptive test in docs/API.rst.

Thanks.
"""

_marker = object()

UID_RX = re.compile("[a-z0-9]{32}$")


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
    if kwargs.get("title") is None:
        kwargs["title"] = "New {}".format(portal_type)

    # generate a temporary ID
    tmp_id = tmpID()

    # get the fti
    types_tool = get_tool("portal_types")
    fti = types_tool.getTypeInfo(portal_type)

    if fti.product:
        obj = _createObjectByType(portal_type, container, tmp_id)
    else:
        # newstyle factory
        factory = getUtility(IFactory, fti.factory)
        obj = factory(tmp_id, *args, **kwargs)
        if hasattr(obj, '_setPortalTypeName'):
            obj._setPortalTypeName(fti.getId())
        notify(ObjectCreatedEvent(obj))
        # notifies ObjectWillBeAddedEvent, ObjectAddedEvent and
        # ContainerModifiedEvent
        container._setObject(tmp_id, obj)
        # we get the object here with the current object id, as it might be
        # renamed already by an event handler
        obj = container._getOb(obj.getId())

    # handle AT Content
    if is_at_content(obj):
        obj.processForm()

    # Edit after processForm; processForm does AT unmarkCreationFlag.
    obj.edit(**kwargs)

    # explicit notification
    modified(obj)
    return obj


def get_tool(name, context=None, default=_marker):
    """Get a portal tool by name

    :param name: The name of the tool, e.g. `portal_catalog`
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
        return get_object_by_uid(brain_object_uid)
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


def get_icon(brain_or_object, html_tag=True):
    """Get the icon of the content object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :param html_tag: A value of 'True' returns the HTML tag, else the image url
    :type html_tag: bool
    :returns: HTML '<img>' tag if 'html_tag' is True else the image url
    :rtype: string
    """
    # Manual approach, because `plone.app.layout.getIcon` does not reliable
    # work for Contents coming from other catalogs than the
    # `portal_catalog`
    portal_types = get_tool("portal_types")
    fti = portal_types.getTypeInfo(brain_or_object.portal_type)
    icon = fti.getIcon()
    if not icon:
        return ""
    url = "%s/%s" % (get_url(get_portal()), icon)
    if not html_tag:
        return url
    tag = '<img width="16" height="16" src="{url}" title="{title}" />'.format(
        url=url, title=get_title(brain_or_object))
    return tag


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
    uc = get_tool("uid_catalog")

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


def get_parent(brain_or_object, catalog_search=False):
    """Locate the parent object of the content/catalog brain

    The `catalog_search` switch uses the `portal_catalog` to do a search return
    a brain instead of the full parent object. However, if the search returned
    no results, it falls back to return the full parent object.

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :param catalog_search: Use a catalog query to find the parent object
    :type catalog_search: bool
    :returns: parent object
    :rtype: ATContentType/DexterityContentType/PloneSite/CatalogBrain
    """

    if is_portal(brain_or_object):
        return get_portal()

    # Do a catalog search and return the brain
    if catalog_search:
        parent_path = get_parent_path(brain_or_object)

        # parent is the portal object
        if parent_path == get_path(get_portal()):
            return get_portal()

        # get the catalog tool
        pc = get_portal_catalog()

        # query for the parent path
        results = pc(path={
            "query": parent_path,
            "depth": 0})

        # No results fallback: return the parent object
        if not results:
            return get_object(brain_or_object).aq_parent

        # return the brain
        return results[0]

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
                portal_type, default="portal_catalog")[0])
    else:
        # User defined catalogs
        if isinstance(catalog, (list, tuple)):
            catalogs.extend(map(get_tool, catalog))
        else:
            catalogs.append(get_tool(catalog))

    # Cleanup: Avoid duplicate catalogs
    catalogs = list(set(catalogs)) or [get_portal_catalog()]

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


def get_portal_catalog():
    """Get the portal catalog tool

    :returns: Portal Catalog Tool
    """
    return get_tool("portal_catalog")


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
    if isinstance(brain_or_object, basestring):
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
    if is_brain(brain_or_object):
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


def get_catalogs_for(brain_or_object, default="portal_catalog"):
    """Get all registered catalogs for the given portal_type, catalog brain or
    content object

    :param brain_or_object: The portal_type, a catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: List of supported catalogs
    :rtype: list
    """
    archetype_tool = get_tool("archetype_tool", None)
    if not archetype_tool:
        # return the default catalog
        return [get_tool(default)]

    catalogs = []

    # get the registered catalogs for portal_type
    if is_object(brain_or_object):
        catalogs = archetype_tool.getCatalogsByType(
            get_portal_type(brain_or_object))
    if isinstance(brain_or_object, basestring):
        catalogs = archetype_tool.getCatalogsByType(brain_or_object)

    if not catalogs:
        return [get_tool(default)]
    return catalogs


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
    if not isinstance(transition, basestring):
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
    if isinstance(user_or_username, basestring):
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

    query = {'portal_type': contact_types, 'getUsername': user.id}
    brains = search(query, catalog='portal_catalog')
    if not brains:
        return None

    if len(brains) > 1:
        # Oops, the user has multiple contacts assigned, return None
        contacts = map(lambda c: c.Title, brains)
        err_msg = "User '{}' is bound to multiple Contacts '{}'"
        err_msg = err_msg.format(user.id, ','.join(contacts))
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
    if not isinstance(string, basestring):
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
    if not isinstance(string, basestring):
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
    if not isinstance(uid, basestring):
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
    if isinstance(value, DateTime):
        return value
    if not value:
        if default is None:
            return None
        return to_date(default)
    try:
        if isinstance(value, str) and '.' in value:
            # https://docs.plone.org/develop/plone/misc/datetime.html#datetime-problems-and-pitfalls
            return DateTime(value, datefmt='international')
        return DateTime(value)
    except (TypeError, ValueError, DateTimeError):
        return to_date(default)


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
        return value.strftime("%Y-%m-%d")
    if is_at_content(value):
        return to_searchable_text_metadata(get_title(value))
    if not isinstance(value, basestring):
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

    if isinstance(pairs, basestring):
        pairs = [pairs, pairs]
    for pair in pairs:
        # pairs is a list of lists -> add each pair
        if isinstance(pair, (tuple, list)):
            dl.add(*pair)
        # pairs is just a single pair -> add it and stop
        if isinstance(pair, basestring):
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
