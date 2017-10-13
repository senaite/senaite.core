# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

# Basic definitions to use in catalog definitions machinery
BASE_CATALOG_INDEXES = {
    # Returns the catalog id
    'id': 'FieldIndex',
    'title': 'FieldIndex',
    # Return the object id
    'getId': 'FieldIndex',
    'portal_type': 'FieldIndex',
    'UID': 'UUIDIndex',
    # created returns a DataTime object
    'created': 'DateIndex',
    # created returns a string object with date format
    'CreationDate': 'DateIndex',
    'Creator': 'FieldIndex',
    # allowedRolesAndUsers is compulsory if we are going to run
    # advancedqueries in this catalog.
    'allowedRolesAndUsers': 'KeywordIndex',
    'review_state': 'FieldIndex',
    # Necessary to avoid reindexing whole catalog when we need to
    # reindex only one object. ExtendedPathIndex also could be used.
    'path': 'PathIndex',
    # This index allows to use the Plone's searchbox. Define a mthod with this
    # name in the contect type to rears for. The method will construct a text
    # blob which contains all full-text searchable text for this content item.
    # https://docs.plone.org/develop/plone/searching_and_indexing/indexing.html#full-text-searching
    'SearchableText': 'ZCTextIndex',
}
BASE_CATALOG_COLUMNS = [
    'UID',
    'getId',
    'meta_type',
    'Title',
    'review_state',
    'state_title',
    # allowedRolesAndUsers is compulsory if we are going to run
    # advancedqueries in this catalog.
    'allowedRolesAndUsers',
    'created',
    'Creator',
    'getObjectWorkflowStates',
]
