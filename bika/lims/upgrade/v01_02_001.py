# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.Expression import Expression
from bika.lims import api
from bika.lims import logger
from bika.lims.config import PROJECTNAME as product
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from bika.lims.workflow import changeWorkflowState
from bika.lims.workflow import isActive
from DateTime import DateTime

version = '1.2.1'  # Remember version number in metadata.xml and setup.py
profile = 'profile-{0}:default'.format(product)


@upgradestep(product, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(product)

    if ut.isOlderVersion(product, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            product, ver_from, version))
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(product, ver_from, version))

    # -------- ADD YOUR STUFF HERE --------
    set_guards_to_inactive_workflow()
    fix_service_status_inconsistences()
    fix_service_profile_template_inconsistences()

    logger.info("{0} upgraded to version {1}".format(product, version))

    return True


def set_guards_to_inactive_workflow():
    wtool = api.get_tool('portal_workflow')
    workflow = wtool.getWorkflowById('bika_inactive_workflow')

    deactivate = workflow.transitions['deactivate']
    deactivate_guard = deactivate.getGuard()
    deactivate_guard.expr = Expression('python:here.guard_deactivate_transition()')
    deactivate.guard = deactivate_guard

    activate = workflow.transitions['activate']
    activate_guard = activate.getGuard()
    activate_guard.expr = Expression('python:here.guard_activate_transition()')
    activate.guard = activate_guard


def fix_service_status_inconsistences():
    catalog = api.get_tool('bika_setup_catalog')
    brains = catalog(portal_type='AnalysisService')
    for brain in brains:
        obj = api.get_object(brain)
        if not isActive(obj):
            continue

        # If this service is active, then all the services this service
        # depends on must be active too, as well as the calculation
        calculation = obj.getCalculation()
        if not calculation:
            continue

        dependencies = calculation.getDependentServices()
        for dependency in dependencies:
            dependency = api.get_object(dependency)
            if not isActive(dependency):
                _change_inactive_state(dependency, 'active')


def fix_service_profile_template_inconsistences():
    catalog = api.get_tool('bika_setup_catalog')
    brains = catalog(portal_type='AnalysisService')
    for brain in brains:
        obj = api.get_object(brain)
        if isActive(obj):
            continue

        # If this service is inactive, be sure is not used neither in Profiles
        # nor in AR Templates
        obj.after_deactivate_transition_event()


def _change_inactive_state(service, new_state):
    msg = "Upgrade v1.2.1: Updating status of {} to '{}'".\
        format(service.getKeyword(), new_state)
    logger.info(msg)
    wtool = api.get_tool('portal_workflow')
    workflow = wtool.getWorkflowById('bika_inactive_workflow')
    wf_state = {
        'action': None,
        'actor': None,
        'comments': msg,
        'inactive_state': new_state,
        'time': DateTime(),
    }
    wtool.setStatusOf('bika_inactive_workflow', service, wf_state)
    workflow.updateRoleMappingsFor(service)
    service.reindexObject(idxs=['allowedRolesAndUsers', 'inactive_state'])
