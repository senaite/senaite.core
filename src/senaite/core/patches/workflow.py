# -*- coding: utf-8 -*-

from Acquisition import aq_base
from bika.lims import api
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware


def _reindexWorkflowVariables(self, ob):
    """This function is called by DCWorkflow immediately after the workflow
    action is invoked in WorkflowTool.doActionFor.

    The original function is only responsible of reindexing the variables that
    may have changed due to the transition (e.g review_state) along with
    security-related indexes. However, the original function does two calls
    to reindexObject, one for workflow variables and another one for the
    security-related indexes. Metadata is updated on both calls as well, cause
    those workflow-variables might also be stored as metadata.

    Since quite often the transition involves changes not only in
    workflow-related variables, but to other field values, it becomes almost
    a requirement to always reindex the object after a transition. Therefore,
    we simply do a full reindexObject here instead of taking only some indexes
    into account.
    """
    if api.is_temporary(ob):
        return

    # do a full reindex
    ob.reindexObject()
    return

    indexes = []

    # Get the variables (e.g. review_state) to be indexes
    if hasattr(aq_base(ob), 'reindexObject'):
        mapping = self.getCatalogVariablesFor(ob) or {}
        indexes = list(mapping)

    # Reindex security of sub-objects.
    if hasattr(aq_base(ob), 'reindexObjectSecurity'):
        indexes.extend(CMFCatalogAware._cmf_security_indexes)

    if not indexes:
        return

    # bail-out indexes that are not in the catalog
    catalogs = api.get_catalogs_for(ob)
    for cat in catalogs:
        cat_indexes = cat.indexes()
        cat_indexes = list(filter(lambda idx: idx in indexes, cat_indexes))
        if not cat_indexes:
            continue

        # Reindex only the desired indexes, w/o metadata update
        cat.catalog_object(ob, idxs=cat_indexes, update_metadata=0)

