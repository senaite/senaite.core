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

from bika.lims import api
from bika.lims.browser.fields.uidreferencefield import get_backreferences


def get_calculation_dependants_for(service):
    """Collect all services which depend on this service

    :param service: Analysis Service Object/ZCatalog Brain
    :returns: List of services that depend on this service
    """

    def calc_dependants_gen(service, collector=None):
        """Generator for recursive resolution of dependant sevices.
        """

        # The UID of the service
        service_uid = api.get_uid(service)

        # maintain an internal dependency mapping
        if collector is None:
            collector = {}

        # Stop iteration if we processed this service already
        if service_uid in collector:
            raise StopIteration

        # Get the dependant calculations of the service
        # (calculations that use the service in their formula).
        calc_uids = get_backreferences(
            service, relationship="CalculationDependentServices")

        for calc_uid in calc_uids:
            # Get the calculation object
            calc = api.get_object_by_uid(calc_uid)

            # Get the Analysis Services which have this calculation assigned
            dep_service_uids = get_backreferences(
                calc, relationship='AnalysisServiceCalculation')

            for dep_service_uid in dep_service_uids:
                dep_service = api.get_object_by_uid(dep_service_uid)

                # remember the dependent service
                collector[dep_service_uid] = dep_service

                # yield the dependent service
                yield dep_service

                # check the dependants of the dependant services
                for ddep_service in calc_dependants_gen(
                        dep_service, collector=collector):
                    yield ddep_service

    dependants = {}
    service = api.get_object(service)

    for dep_service in calc_dependants_gen(service):
        # Skip the initial (requested) service
        if dep_service == service:
            continue
        uid = api.get_uid(dep_service)
        dependants[uid] = dep_service

    return dependants


def get_calculation_dependencies_for(service):
    """Calculation dependencies of this service and the calculation of each
    dependent service (recursively).
    """

    def calc_dependencies_gen(service, collector=None):
        """Generator for recursive dependency resolution.
        """

        # The UID of the service
        service_uid = api.get_uid(service)

        # maintain an internal dependency mapping
        if collector is None:
            collector = {}

        # Stop iteration if we processed this service already
        if service_uid in collector:
            raise StopIteration

        # Get the calculation of the service.
        # The calculation comes either from an assigned method or the user
        # has set a calculation manually (see content/analysisservice.py).
        calculation = service.getCalculation()

        # Stop iteration if there is no calculation
        if not calculation:
            raise StopIteration

        # The services used in this calculation.
        # These are the actual dependencies of the used formula.
        dep_services = calculation.getDependentServices()
        for dep_service in dep_services:
            # get the UID of the dependent service
            dep_service_uid = api.get_uid(dep_service)

            # remember the dependent service
            collector[dep_service_uid] = dep_service

            # yield the dependent service
            yield dep_service

            # check the dependencies of the dependent services
            for ddep_service in calc_dependencies_gen(dep_service,
                                                      collector=collector):
                yield ddep_service

    dependencies = {}
    for dep_service in calc_dependencies_gen(service):
        # Skip the initial (requested) service
        if dep_service == service:
            continue
        uid = api.get_uid(dep_service)
        dependencies[uid] = dep_service

    return dependencies


def get_service_dependencies_for(service):
    """Calculate the dependencies for the given service.
    """

    dependants = get_calculation_dependants_for(service)
    dependencies = get_calculation_dependencies_for(service)

    return {
        "dependencies": dependencies.values(),
        "dependants": dependants.values(),
    }
