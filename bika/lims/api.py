# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Acquisition import aq_base
from AccessControl.PermissionRole import rolesForPermissionOn

from Products.CMFPlone.utils import base_hasattr
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.interfaces import IFolderish
from Products.Archetypes.BaseObject import BaseObject
from Products.ZCatalog.interfaces import ICatalogBrain
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName

from zope import globalrequest
from zope.event import notify
from zope.interface import implements
from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.component.interfaces import IFactory
from zope.component.interfaces import ObjectEvent
from zope.component.interfaces import IObjectEvent
from zope.lifecycleevent import modified
from zope.lifecycleevent import ObjectCreatedEvent
from zope.security.interfaces import Unauthorized

from plone import api as ploneapi
from plone.memoize.volatile import DontCache
from plone.api.exc import InvalidParameterError
from plone.dexterity.interfaces import IDexterityContent
from plone.app.layout.viewlets.content import ContentHistoryView
from plone.i18n.normalizer.interfaces import IFileNameNormalizer
from plone.i18n.normalizer.interfaces import IIDNormalizer

from bika.lims import logger

"""Bika LIMS Framework API

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


class BikaLIMSError(Exception):
    """Base exception class for bika.lims errors."""


class IBikaTransitionEvent(IObjectEvent):
    """Bika WF transition event interface"""


class IBikaBeforeTransitionEvent(IBikaTransitionEvent):
    """Fired before the transition is invoked"""


class IBikaAfterTransitionEvent(IBikaTransitionEvent):
    """Fired after the transition done"""


class IBikaTransitionFailedEvent(IBikaTransitionEvent):
    """Fired if the transition failed"""


class BikaTransitionEvent(ObjectEvent):
    """Bika WF transition event"""
    def __init__(self, obj, transition, exception=None):
        ObjectEvent.__init__(self, obj)
        self.obj = obj
        self.transition = transition
        self.exception = exception


class BikaBeforeTransitionEvent(BikaTransitionEvent):
    implements(IBikaBeforeTransitionEvent)


class BikaAfterTransitionEvent(BikaTransitionEvent):
    implements(IBikaAfterTransitionEvent)


class BikaTransitionFailedEvent(BikaTransitionEvent):
    implements(IBikaTransitionFailedEvent)


def get_portal():
    """Get the portal object

    :returns: Portal object
    """
    return ploneapi.portal.getSite()


def get_bika_setup():
    """Fetch the `bika_setup` folder.
    """
    portal = get_portal()
    return portal.get("bika_setup")


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
        # notifies ObjectWillBeAddedEvent, ObjectAddedEvent and ContainerModifiedEvent
        container._setObject(tmp_id, obj)
        # we get the object here with the current object id, as it might be renamed
        # already by an event handler
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
        except (BikaLIMSError, AttributeError) as e:
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
    """Bika LIMS Error
    """
    if msg is None:
        msg = "Reason not given."
    raise BikaLIMSError("{}".format(msg))


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


def get_object(brain_or_object):
    """Get the full content object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: PortalObject/ATContentType/DexterityContentType
    /CatalogBrain
    :returns: The full object
    """
    if not is_object(brain_or_object):
        fail("{} is not supported.".format(repr(brain_or_object)))
    if is_brain(brain_or_object):
        return brain_or_object.getObject()
    return brain_or_object


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
    """Get the list of fields from the object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: List of fields
    :rtype: list
    """
    obj = get_object(brain_or_object)
    schema = get_schema(obj)
    if is_dexterity_content(obj):
        names = schema.names()
        fields = map(lambda name: schema.get(name), names)
        return dict(zip(names, fields))
    return dict(zip(schema.keys(), schema.fields()))


def get_id(brain_or_object):
    """Get the Plone ID for this object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Plone ID
    :rtype: string
    """
    if is_brain(brain_or_object) and base_hasattr(brain_or_object, "getId"):
        return brain_or_object.getId
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

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Plone UID
    :rtype: string
    """
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
    # work for Bika Contents coming from other catalogs than the
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

    # we try to find the object with both catalogs
    pc = get_portal_catalog()
    uc = get_tool("uid_catalog")

    # try to find the object with the reference catalog first
    brains = uc(UID=uid)
    if brains:
        return brains[0].getObject()

    # try to find the object with the portal catalog
    res = pc(UID=uid)
    if not res:
        if default is not _marker:
            return default
        fail("No object found for UID {}".format(uid))

    return get_object(res[0])


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

    pc = get_portal_catalog()
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

    res = pc(path=dict(query=path, depth=0))
    if not res:
        if default is not _marker:
            return default
        fail("Object at path '{}' not found".format(path))
    return get_object(res[0])


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
        fail("Multi Catalog Queries are not supported, please specify a catalog.")

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
        logger.error("get_review_history: expected list, recieved {}".format(
            review_history))
        review_history = []
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
    workflow = get_tool("portal_workflow")
    obj = get_object(brain_or_object)
    return workflow.getInfoFor(ob=obj, name=state_var)


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


def get_cancellation_status(brain_or_object, default="active"):
    """Get the `cancellation_state` of an object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Value of the review_status variable
    :rtype: String
    """
    if is_brain(brain_or_object):
        return getattr(brain_or_object, "cancellation_state", default)
    workflows = get_workflows_for(brain_or_object)
    if 'bika_cancellation_workflow' not in workflows:
        return default
    return get_workflow_status_of(brain_or_object, 'cancellation_state')


def get_inactive_status(brain_or_object, default="active"):
    """Get the `cancellation_state` of an objct

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Value of the review_status variable
    :rtype: String
    """
    if is_brain(brain_or_object):
        return getattr(brain_or_object, "inactive_state", default)
    workflows = get_workflows_for(brain_or_object)
    if 'bika_inactive_workflow' not in workflows:
        return default
    return get_workflow_status_of(brain_or_object, 'inactive_state')


def is_active(brain_or_object):
    """Check if the workflow state of the object is 'inactive' or 'cancelled'.

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: False if the object is in the state 'inactive' or 'cancelled'
    :rtype: bool
    """
    if get_inactive_status(brain_or_object) == "inactive":
        return False
    if get_cancellation_status(brain_or_object) == "cancelled":
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
    # notify the BeforeTransitionEvent
    notify(BikaBeforeTransitionEvent(obj, transition))
    try:
        ploneapi.content.transition(obj, transition)
    except ploneapi.exc.InvalidParameterError as e:
        # notify the TransitionFailedEvent
        notify(BikaTransitionFailedEvent(obj, transition, exception=e))
        fail("Failed to perform transition '{}' on {}: {}".format(
             transition, obj, str(e)))
    # notify the AfterTransitionEvent
    notify(BikaAfterTransitionEvent(obj, transition))
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


def get_view(name, context=None, request=None):
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
    return getMultiAdapter((get_object(context), request), name=name)


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
    if not user_or_username:
        return None
    if hasattr(user_or_username, "getUserId"):
        return ploneapi.user.get(user_or_username.getUserId())
    return ploneapi.user.get(userid=user_or_username)


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
        fail("Type of argument must be string, found '{}'".format(type(string)))
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
        fail("Type of argument must be string, found '{}'".format(type(string)))
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
    if len(uid) != 32:
        return False
    if not validate:
        return True

    # Check if a brain for this uid exists
    uc = get_tool('uid_catalog')
    brains = uc(UID=uid)
    if brains:
        assert (len(brains) == 1)
    return len(brains) > 0
