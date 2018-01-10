# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import transaction
from DateTime import DateTime
from plone.api.portal import get_tool

from bika.lims import logger
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING


def analyses_creation_date_recover():
    """
    This function walks over all Analysis Request objects, obtains their
    associate analyses and checks if their creation date is older than the
    Analysis Request one. If this condition is met, the system sets the
    analyses creation date with the Analysis Request one.
    :return: Boolean. True if the process succeed, and False otherwise.
    """

    ar_catalog = get_tool(CATALOG_ANALYSIS_REQUEST_LISTING)
    ans_catalog = get_tool(CATALOG_ANALYSIS_LISTING)
    # Getting all analysis requests to walk through
    ar_brains = ar_catalog()
    total_ars = len(ar_brains)
    total_iterated = 0
    logger.info("Analysis Requests to walk over: {}".format(total_ars))
    total_modified = 0
    for ar_brain in ar_brains:
        ans_brains = ans_catalog({"getRequestUID": ar_brain.UID})
        analyses_modified = set_correct_created_date(
            ar_brain.created, ans_brains)
        total_modified += analyses_modified
        total_iterated = commit_action(
            total_ars, total_iterated, total_modified)
    transaction.commit()
    logger.info("Analyses creation date sanitized.")
    return True


def set_correct_created_date(ar_creation_date, ans_brains):
    """
    Checks if the Analysis Request's creation date is older than their
    analyses ones. If not, sets the Analyses creation that with the Analysis
    Request one and reindex the object.
    :param ar_creation_date: A DateTime objects with an Analysis Request
    creation date.
    :param ans_brains: An Analysis Service brain.
    :return: The number of analyses modified this time
    """
    counter = 0
    for an_brain in ans_brains:
        if ar_creation_date > an_brain.created:
            # update analysis date with request's one
            analysis = an_brain.getObject()
            analysis.creation_date = ar_creation_date
            analysis.reindexObject(idxs=['created', ])
            counter += 1
    return counter


def commit_action(total_ars, total_iterated, total_modified):
    """
    Does a tranaction commit in order to save the changes. It also logs some
    info about the process.
    :param total_ars: An integer as the total amount of Analysis Requests
    to walk over.
    :param total_iterated: An integer as the total amount of Analysis Requests
    checked.
    :param total_modified: An integer as the total amount of analyses modified
    :return: The total of analyses iterated.
    """
    total_iterated += 1
    if total_iterated % 20 == 0:
        transaction.commit()
        logger.info(
            "Sanitize progress of analyses creation date: {} out of {}. "
            "Number of modified analyses: {}"
            .format(total_iterated, total_ars, total_modified))
    return total_iterated
