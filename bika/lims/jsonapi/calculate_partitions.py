from plone.jsonapi.core import router
from plone.jsonapi.core.interfaces import IRouteProvider
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest
from zope import interface
import magnitude


def mg(value):
    tokens = value.split(" ") if value else [0, '']
    val = float(tokens[0]) if isinstance(tokens[0], (int, long)) else 0
    unit = tokens[1] if len(tokens) > 1 else ''
    # Magnitude doesn't support mL units.
    # Since mL is commonly used instead of ml to avoid confusion with the
    # number one, add "L" (for liter) as a 'recognizable' unit.
    # L unit as liter is also recommended by the NIST Guide
    # http://physics.nist.gov/Pubs/SP811/sec05.html#table6
    # Further info: https://jira.bikalabs.com/browse/LIMS-1441
    unit = unit[:-1]+'l' if unit.endswith('L') else unit
    return magnitude.mg(val, unit)


class calculate_partitions(object):
    interface.implements(IRouteProvider)

    def initialize(self, context, request):
        pass

    @property
    def routes(self):
        return (
            ("/calculate_partitions",
             "calculate_partitions",
             self.calculate_partitions,
             dict(methods=['GET', 'POST'])
            ),
        )

    def calculate_partitions(self, context, request):
        """Calculate the size and type of sample partitions required to perform
        analysis services on a certain sample type.

        Required fields

            - services: A list of Analysis Services
            - sampletype: The sample type in use for this sample

        Example usage:

            @@API/calculate_partitions
                ?sampletype=portal_type:SampleType,title=Cattle Feed
                &services:list=portal_type:AnalysisService,title:Ash
                &services:list=portal_type:AnalysisService,title:Moisture
        """

        ret = {
            "url": router.url_for("calculate_partitions", force_external=True),
            "success": False,
            "error": True,
        }
        parts = []

        uc = getToolByName(context, 'uid_catalog')

        services = []
        _services = request.get('services', '').split(",")
        if not _services:
            raise BadRequest("services are not present in request")
        for uid in _services:
            try:
                services.append(uc(UID=uid)[0].getObject())
            except:
                raise BadRequest("analysis service uid %s is invalid" % uid)

        _sampletype = request.get('sampletype', '')
        if not _sampletype:
            raise BadRequest("sampletype is not present in the request")
        try:
            sampletype = uc(UID=_sampletype)[0].getObject()
        except:
            raise BadRequest("sample type %s is invalid" % _sampletype)

        for service in services:
            partsetup = [ps for ps in service.getPartitionSetup()
                         if ps['sampletype'] == sampletype.UID()]
            if partsetup:
                # User values set for each SampleType on each service
                separate = bool(partsetup[0]['separate'])
                containers = [uc(UID=uid)[0].getObject() for uid in partsetup[0]['container']]
                preservations = [uc(UID=uid)[0].getObject() for uid in partsetup[0]['preservation']]
                minvol = mg(partsetup[0]['vol'])
            else:
                # read default values from service
                separate = service.getSeparate()
                containers = service.getContainer()
                if not containers:
                    containers = []
                if containers and not type(containers) in (list, tuple):
                    containers = [containers, ]
                preservations = service.getPreservation()
                if not preservations:
                    preservations = []
                if preservations and not type(preservations) in (list, tuple):
                    preservations = [preservations, ]
                minvol = mg(sampletype.getMinimumVolume())

            # ContainerTypes may also be selected in the UI.
            # we want a list of actual containers which this analysis can use
            _containers = []
            for c in containers:
                if c.portal_type == 'Container':
                    _containers.append(c)
                else:
                    _containers.extend(c.getContainers())
            containers = _containers

            containers.sort(lambda a, b: cmp(mg(a.getCapacity()),
                                             mg(b.getCapacity())))

            if separate:
                parts.append({
                    'services': [service, ],
                    'separate': True,
                    'container': containers,
                    'preservation': preservations,
                    'minvol': minvol,
                })
            else:
                # find partition this analysis can use or create new entry.
                for x, part in enumerate(parts):
                    if part['separate']:
                        continue

                    # our container must match this part.
                    _containers = []
                    if part['container']:
                        _containers = [c for c in part['container']
                                       if c in containers]
                        if not _containers:
                            continue

                    # our preservation must match this part
                    _preservations = []
                    if part['preservation']:
                        _preservations = [p for p in part['preservation']
                                          if p in preservations]
                        if not _preservations:
                            continue

                    # filter containers on capacoty
                    _required_vol = part['minvol'] + minvol
                    if _containers:
                        _containers = [c for c in _containers
                                       if mg(c.getCapacity()) > _required_vol]
                        if not _containers:
                            continue

                    # all the conditions passed:
                    # this partition can host our analysis
                    part['minvol'] = _required_vol
                    part['services'].append(service)
                    part['container'] = _containers
                    part['preservation'] = _preservations
                    parts[x] = part
                    break
                # no partition found to share this analysis: create new.
                else:
                    parts.append({
                        'services': [service, ],
                        'separate': False,
                        'container': containers,
                        'preservation': preservations,
                        'minvol': minvol
                    })

        # Convert objects to UIDs
        for x, part in enumerate(parts):
            parts[x]['service_titles'] = [s.Title() for s in part['services']]
            parts[x]['services'] = [s.UID() for s in part['services']]
            parts[x]['container_titles'] = [c.Title() for c in part['container']]
            parts[x]['container'] = [c.UID() for c in part['container']]
            parts[x]['preservation_titles'] = [p.Title() for p in part['preservation']]
            parts[x]['preservation'] = [p.UID() for p in part['preservation']]
            parts[x]['minvol'] = str(part['minvol'])

        ret['success'] = True
        ret['error'] = False
        ret['parts'] = parts

        return ret
