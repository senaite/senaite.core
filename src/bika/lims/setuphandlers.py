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

import itertools

from Acquisition import aq_base
from bika.lims import api
from bika.lims import logger
from bika.lims.catalog import getCatalogDefinitions
from bika.lims.catalog import setup_catalogs
from bika.lims.catalog.catalog_utilities import addZCTextIndex
from plone import api as ploneapi
from senaite.core.upgrade.utils import temporary_allow_type

PROFILE_ID = "profile-bika.lims:default"

GROUPS = [
    {
        "id": "Analysts",
        "title": "Analysts",
        "roles": ["Analyst"],
    }, {
        "id": "Clients",
        "title": "Clients",
        "roles": ["Client"],
    }, {
        "id": "LabClerks",
        "title": "Lab Clerks",
        "roles": ["LabClerk"],
    }, {
        "id": "LabManagers",
        "title": "Lab Managers",
        "roles": ["LabManager"],
    }, {
        "id": "Preservers",
        "title": "Preservers",
        "roles": ["Preserver"],
    }, {
        "id": "Publishers",
        "title": "Publishers",
        "roles": ["Publisher"],
    }, {
        "id": "Verifiers",
        "title": "Verifiers",
        "roles": ["Verifier"],
    }, {
        "id": "Samplers",
        "title": "Samplers",
        "roles": ["Sampler"],
    }, {
        "id": "RegulatoryInspectors",
        "title": "Regulatory Inspectors",
        "roles": ["RegulatoryInspector"],
    }, {
        "id": "SamplingCoordinators",
        "title": "Sampling Coordinator",
        "roles": ["SamplingCoordinator"],
    }
]

NAV_BAR_ITEMS_TO_HIDE = (
    # List of items to hide from navigation bar
    "pricelists",
)


CONTENTS_TO_DELETE = (
    # List of items to delete
    "Members",
    "news",
    "events",
)

CATALOG_MAPPINGS = (
    # portal_type, catalog_ids
    ("ARTemplate", ["bika_setup_catalog", "portal_catalog"]),
    ("AnalysisCategory", ["bika_setup_catalog"]),
    ("AnalysisProfile", ["bika_setup_catalog", "portal_catalog"]),
    ("AnalysisService", ["bika_setup_catalog", "portal_catalog"]),
    ("AnalysisSpec", ["bika_setup_catalog"]),
    ("Attachment", ["portal_catalog"]),
    ("AttachmentType", ["bika_setup_catalog"]),
    ("Batch", ["bika_catalog", "portal_catalog"]),
    ("BatchLabel", ["bika_setup_catalog"]),
    ("Calculation", ["bika_setup_catalog", "portal_catalog"]),
    ("Container", ["bika_setup_catalog"]),
    ("ContainerType", ["bika_setup_catalog"]),
    ("Department", ["bika_setup_catalog", "portal_catalog"]),
    ("Instrument", ["bika_setup_catalog", "portal_catalog"]),
    ("InstrumentLocation", ["bika_setup_catalog", "portal_catalog"]),
    ("InstrumentType", ["bika_setup_catalog", "portal_catalog"]),
    ("LabContact", ["bika_setup_catalog", "portal_catalog"]),
    ("LabProduct", ["bika_setup_catalog", "portal_catalog"]),
    ("Manufacturer", ["bika_setup_catalog", "portal_catalog"]),
    ("Method", ["bika_setup_catalog", "portal_catalog"]),
    ("Multifile", ["bika_setup_catalog"]),
    ("Preservation", ["bika_setup_catalog"]),
    ("ReferenceDefinition", ["bika_setup_catalog", "portal_catalog"]),
    ("ReferenceSample", ["bika_catalog", "portal_catalog"]),
    ("SampleCondition", ["bika_setup_catalog"]),
    ("SampleMatrix", ["bika_setup_catalog"]),
    ("SamplePoint", ["bika_setup_catalog", "portal_catalog"]),
    ("SampleType", ["bika_setup_catalog", "portal_catalog"]),
    ("SamplingDeviation", ["bika_setup_catalog"]),
    ("StorageLocation", ["bika_setup_catalog", "portal_catalog"]),
    ("SubGroup", ["bika_setup_catalog"]),
    ("Supplier", ["bika_setup_catalog", "portal_catalog"]),
    ("WorksheetTemplate", ["bika_setup_catalog", "portal_catalog"]),
)

INDEXES = (
    # catalog, id, indexed attribute, type
    ("portal_catalog", "Analyst", "", "FieldIndex"),
    ("portal_catalog", "sample_uid", "", "KeywordIndex"),
)

COLUMNS = (
    # catalog, column name
    ("portal_catalog", "Analyst"),
)

ALLOWED_STYLES = [
    "color",
    "background-color"
]


def setup_handler(context):
    """SENAITE setup handler
    """

    if context.readDataFile("bika.lims_various.txt") is None:
        return

    logger.info("SENAITE setup handler [BEGIN]")

    portal = context.getSite()

    # Run Installers
    hide_navbar_items(portal)
    reindex_content_structure(portal)
    setup_groups(portal)
    setup_catalog_mappings(portal)
    setup_core_catalogs(portal)
    add_dexterity_portal_items(portal)
    add_dexterity_setup_items(portal)
    # XXX P5: Fix HTML filtering
    # setup_html_filter(portal)

    # Set CMF Form actions
    setup_form_controller_actions(portal)

    logger.info("SENAITE setup handler [DONE]")


def hide_navbar_items(portal):
    """Hide root items in navigation
    """
    logger.info("*** Hide Navigation Items ***")

    # Get the list of object ids for portal
    object_ids = portal.objectIds()
    object_ids = filter(lambda id: id in object_ids, NAV_BAR_ITEMS_TO_HIDE)
    for object_id in object_ids:
        item = portal[object_id]
        item.setExcludeFromNav(True)
        item.reindexObject()


def reindex_content_structure(portal):
    """Reindex contents generated by Generic Setup
    """
    logger.info("*** Reindex content structure ***")

    def reindex(obj, recurse=False):
        # skip catalog tools etc.
        if api.is_object(obj):
            obj.reindexObject()
        if recurse and hasattr(aq_base(obj), "objectValues"):
            map(reindex, obj.objectValues())

    setup = api.get_setup()
    setupitems = setup.objectValues()
    rootitems = portal.objectValues()

    for obj in itertools.chain(setupitems, rootitems):
        logger.info("Reindexing {}".format(repr(obj)))
        reindex(obj)


def setup_groups(portal):
    """Setup roles and groups
    """
    logger.info("*** Setup Roles and Groups ***")

    portal_groups = api.get_tool("portal_groups")

    for gdata in GROUPS:
        group_id = gdata["id"]
        # create the group and grant the roles
        if group_id not in portal_groups.listGroupIds():
            logger.info("+++ Adding group {title} ({id})".format(**gdata))
            portal_groups.addGroup(group_id,
                                   title=gdata["title"],
                                   roles=gdata["roles"])
        # grant the roles to the existing group
        else:
            ploneapi.group.grant_roles(
                groupname=gdata["id"],
                roles=gdata["roles"],)
            logger.info("+++ Granted group {title} ({id}) the roles {roles}"
                        .format(**gdata))


def setup_catalog_mappings(portal):
    """Setup portal_type -> catalog mappings
    """
    logger.info("*** Setup Catalog Mappings ***")

    at = api.get_tool("archetype_tool")
    for portal_type, catalogs in CATALOG_MAPPINGS:
        at.setCatalogsByType(portal_type, catalogs)


def setup_core_catalogs(portal):
    """Setup core catalogs
    """
    logger.info("*** Setup Core Catalogs ***")

    # Setting up all LIMS catalogs defined in catalog folder
    setup_catalogs(portal, getCatalogDefinitions())

    to_reindex = []
    for catalog, name, attribute, meta_type in INDEXES:
        c = api.get_tool(catalog)
        indexes = c.indexes()
        if name in indexes:
            logger.info("*** Index '%s' already in Catalog [SKIP]" % name)
            continue

        logger.info("*** Adding Index '%s' for field '%s' to catalog ..."
                    % (meta_type, name))

        # do we still need ZCTextIndexes?
        if meta_type == "ZCTextIndex":
            addZCTextIndex(c, name)
        else:
            c.addIndex(name, meta_type)

        # get the new created index
        index = c._catalog.getIndex(name)
        # set the indexed attributes
        if hasattr(index, "indexed_attrs"):
            index.indexed_attrs = [attribute or name]

        to_reindex.append((c, name))
        logger.info("*** Added Index '%s' for field '%s' to catalog [DONE]"
                    % (meta_type, name))

    # catalog columns
    for catalog, name in COLUMNS:
        c = api.get_tool(catalog)
        if name not in c.schema():
            logger.info("*** Adding Column '%s' to catalog '%s' ..."
                        % (name, catalog))
            c.addColumn(name)
            logger.info("*** Added Column '%s' to catalog '%s' [DONE]"
                        % (name, catalog))
        else:
            logger.info("*** Column '%s' already in catalog '%s'  [SKIP]"
                        % (name, catalog))
            continue

    for catalog, name in to_reindex:
        logger.info("*** Indexing new index '%s' ..." % name)
        catalog.manage_reindexIndex(name)
        logger.info("*** Indexing new index '%s' [DONE]" % name)


def setup_form_controller_actions(portal):
    """Setup custom CMF Form actions
    """
    logger.info("*** Setup Form Controller custom actions ***")
    fc_tool = api.get_tool("portal_form_controller")

    # Redirect the user to Worksheets listing view after the "remove" action
    # from inside Worksheet context is pressed
    # https://github.com/senaite/senaite.core/pull/1480
    fc_tool.addFormAction(
        object_id="content_status_modify",
        status="success",
        context_type="Worksheet",
        button=None,
        action_type="redirect_to",
        action_arg="python:object.aq_inner.aq_parent.absolute_url()")


def add_dexterity_portal_items(portal):
    """Adds the Dexterity Container in the Site folder

    N.B.: We do this in code, because adding this as Generic Setup Profile in
          `profiles/default/structure` flushes the contents on every import.
    """
    # Tuples of ID, Title, FTI
    items = [
        ("samples",  # ID
         "Samples",  # Title
         "Samples"),  # FTI
    ]
    add_dexterity_items(portal, items)

    # Move Samples after Clients nav item
    position = portal.getObjectPosition("clients")
    portal.moveObjectToPosition("samples", position + 1)
    portal.plone_utils.reindexOnReorder(portal)


def add_dexterity_setup_items(portal):
    """Adds the Dexterity Container in the Setup Folder

    N.B.: We do this in code, because adding this as Generic Setup Profile in
          `profiles/default/structure` flushes the contents on every import.
    """
    # Tuples of ID, Title, FTI
    items = [
        ("dynamic_analysisspecs",  # ID
         "Dynamic Analysis Specifications",  # Title
         "DynamicAnalysisSpecs"),  # FTI

        ("interpretation_templates",
         "Interpretation Templates",
         "InterpretationTemplates")
    ]
    setup = api.get_setup()
    add_dexterity_items(setup, items)


def add_dexterity_items(container, items):
    """Adds a dexterity item, usually a folder in the container
    :param container: container of the items to add
    :param items: tuple of Id, Title, FTI
    """
    for id, title, fti in items:
        obj = container.get(id)
        if obj is None:
            with temporary_allow_type(container, fti) as ct:
                obj = api.create(ct, fti, id=id, title=title)
        else:
            obj.setTitle(title)
        obj.reindexObject()


def setup_html_filter(portal):
    """Setup HTML filtering for resultsinterpretations
    """
    logger.info("*** Setup HTML Filter ***")
    # XXX P5: Fix ImportError: No module named controlpanel.filter
    from plone.app.controlpanel.filter import IFilterSchema
    # bypass the broken API from portal_transforms
    adapter = IFilterSchema(portal)
    style_whitelist = adapter.style_whitelist
    for style in ALLOWED_STYLES:
        logger.info("Allow style '{}'".format(style))
        if style not in style_whitelist:
            style_whitelist.append(style)
    adapter.style_whitelist = style_whitelist
