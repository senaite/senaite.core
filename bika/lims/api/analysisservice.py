from bika.lims.api import get_uid


def get_calculation_dependants_for(service):
    """Calculation dependants of this service
    """

    def calc_dependants_gen(service, collector=None):
        """Generator for recursive resolution of dependant sevices.
        """

        # The UID of the service
        service_uid = get_uid(service)

        # maintain an internal dependency mapping
        if collector is None:
            collector = {}

        # Stop iteration if we processed this service already
        if service_uid in collector:
            raise StopIteration

        # Get the dependant calculations of the service
        # (calculations that use the service in their formula).
        dep_calcs = service.getBackReferences('CalculationAnalysisService')
        for dep_calc in dep_calcs:
            # Get the methods linked to this calculation
            dep_methods = dep_calc.getBackReferences('MethodCalculation')
            for dep_method in dep_methods:
                # Get the services that have this method linked
                dep_services = dep_method.getBackReferences(
                    'AnalysisServiceMethod')
                for dep_service in dep_services:

                    # get the UID of the dependent service
                    dep_service_uid = get_uid(dep_service)

                    # skip services with a different calculation, e.g. when
                    # the user selected a calculation manually.
                    if dep_service.getCalculation() != dep_calc:
                        continue

                    # remember the dependent service
                    collector[dep_service_uid] = dep_service

                    # yield the dependent service
                    yield dep_service

                    # check the dependants of the dependant services
                    for ddep_service in calc_dependants_gen(
                            dep_service, collector=collector):
                        yield ddep_service

    dependants = {}
    for dep_service in calc_dependants_gen(service):
        # Skip the initial (requested) service
        if dep_service == service:
            continue
        uid = get_uid(dep_service)
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
        service_uid = get_uid(service)

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
            dep_service_uid = get_uid(dep_service)

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
        uid = get_uid(dep_service)
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
