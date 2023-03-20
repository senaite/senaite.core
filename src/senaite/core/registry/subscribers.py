# -*- coding: utf-8 -*-

from bika.lims import api
from senaite.core.api import label as label_api
from senaite.core.registry import get_registry_record

labels_initialized = False


def update_label_types(object, event):
    """Update label enabled types

    NOTE: The settings are thread local!

    This means that in multi client environments the settings are not reflected
    in the other instances.

    A restart of these instances is required, so that the `init_labels` handler
    below marks the classes appropriately.
    """
    # get the types that support labels directly
    enabled_types = object.label_enabled_portal_types
    plone_utils = api.get_tool("plone_utils")
    friendly_types = plone_utils.getUserFriendlyTypes()
    for portal_type in friendly_types:
        if portal_type not in enabled_types:
            label_api.disable_labels_for_type(portal_type)
        else:
            label_api.enable_labels_for_type(portal_type)


def init_labels(site, event):
    """Initialize labels for enabled portal types after startup

    This is a multi-subscriber to `zope.component.interfaces.ISite` and
    `zope.traversing.interfaces.BeforeTraverseEvent`.

    This is required because the Zope Component Architecture (Site Manager) is
    set for each request and is required here to lookup the registry settings.

    Also see `zope.site.site.threadSiteSubscriber`.

    We use a global variable to ensure it is only run once per instance.
    """
    global labels_initialized
    if labels_initialized:
        return
    enabled_types = get_registry_record("label_enabled_portal_types")
    if not enabled_types:
        labels_initialized = True
        return
    for portal_type in enabled_types:
        label_api.enable_labels_for_type(portal_type)
    labels_initialized = True
