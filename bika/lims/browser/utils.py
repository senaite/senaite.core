""" View utilities.
"""
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from bika.lims.config import POINTS_OF_CAPTURE
from bika.lims.utils import isActive
import json

class bsc_counter(BrowserView):
    def __call__(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        return bsc.getCounter()

class bsc_browserdata(BrowserView):
    """Returns information about services from bika_setup_catalog.
    This view is called from ./js/bika.js and it's output is cached
    in browser localStorage.
    """
    def __call__(self):
        translate = self.context.translate
        bsc = getToolByName(self.context, 'bika_setup_catalog')

        data = {
            'categories':{},  # services keyed by "POC_category"
            'services':{},    # service info, keyed by UID
        }

        ## Loop ALL SERVICES
        services = dict([(b.UID, b.getObject()) for b
                         in bsc(portal_type = "AnalysisService",
                                inactive_state = "active")])

        for uid, service in services.items():

            ## Store categories
            ## data['categories'][poc_catUID]: [uid, uid]
            key = "%s_%s" % (service.getPointOfCapture(),
                             service.getCategoryUID())
            if key in data['categories']:
                data['categories'][key].append(uid)
            else:
                data['categories'][key] = [uid, ]

            ## Get dependants
            ## (this service's Calculation backrefs' dependencies)
            backrefs = []
            # this function follows all backreferences so we need skip to
            # avoid recursion. It should maybe be modified to be more smart...
            skip = []
            def walk(items):
                for item in items:
                    if item.portal_type == 'AnalysisService'\
                       and item.UID() != service.UID():
                        backrefs.append(item)
                    if item not in skip:
                        skip.append(item)
                        walk(item.getBackReferences())
            walk([service, ])

            ## Get dependencies
            ## (services we depend on)
            deps = {}
            calc = service.getCalculation()
            if calc:
                deps = calc.getCalculationDependencies()
                def walk(deps):
                    for depserv_uid, depserv_deps in deps.items():
                        if depserv_uid == uid:
                            continue
                        depserv = services[depserv_uid]
                        category = depserv.getCategory()
                        cat = '%s_%s' % (category.UID(), category.Title())
                        poc = '%s_%s' % \
                            (depserv.getPointOfCapture(),
                             POINTS_OF_CAPTURE.getValue(depserv.getPointOfCapture()))
                        srv = '%s_%s' % (depserv.UID(), depserv.Title())
                        if not deps.has_key(poc): deps[poc] = {}
                        if not deps[poc].has_key(cat): deps[poc][cat] = []
                        deps[poc][cat].append(srv)
                        if depserv_deps:
                            walk(depserv_deps)
                walk(deps)

            ## Get partition setup records for this service
            separate = service.getSeparate()
            containers = service.getContainer()
            preservations = service.getPreservation()
            partsetup = service.getPartitionSetup()

            # Single values become lists here
            for x in range(len(partsetup)):
                if partsetup[x].has_key('container') \
                   and type(partsetup[x]['container']) == str:
                    partsetup[x]['container'] = [partsetup[x]['container'],]
                if partsetup[x].has_key('preservation') \
                   and type(partsetup[x]['preservation']) == str:
                    partsetup[x]['preservation'] = [partsetup[x]['preservation'],]

            ## If no dependents, backrefs or partition setup exists
            ## nothing is stored for this service
            if not (backrefs or deps or separate or
                    containers or preservations or partsetup):
                continue

            # store info for this service
            data['services'][uid] = {
                'backrefs':[s.UID() for s in backrefs],
                'deps':deps,
            }

            data['services'][uid]['Separate'] = separate
            data['services'][uid]['Container'] = \
                [container.UID() for container in containers]
            data['services'][uid]['Preservation'] = \
                [pres.UID() for pres in preservations]
            data['services'][uid]['PartitionSetup'] = \
                partsetup

        ## List of selected services for each ARProfile
        for context in (self.context, self.context.bika_setup.bika_arprofiles):
            for profile in [p for p in context.objectValues("ARProfile")
                            if isActive(p)]:
                slist = {}
                profile_services = profile.getService()
                if type(profile_services) == str:
                    profile_services = [profile_services, ]
                for p_uid in profile_services:
                    p_service = services[p_uid]
                    key = "%s_%s" % (p_service.getPointOfCapture(),
                                     p_service.getCategoryUID())
                    if key in slist:
                        slist[key].append(p_service.UID())
                    else:
                        [key] = [service.UID, ]

                title = context == self.context.bika_setup.bika_arprofiles \
                    and translate(_('Lab')) + ": " + profile.Title() \
                    or profile.Title()

                p_dict = {
                    'UID':profile.UID(),
                    'Title':title,
                    'Services':slist,
                }
                formdata['profiles'][profile.UID()] = p_dict

        ## parameters for all ARTemplates
        for context in (self.context, self.context.bika_setup.bika_arprofiles):
            templates = [t for t in context.objectValues("ARTemplate")
                         if isActive(t)]
            for template in templates:
                title = context == self.context.bika_setup.bika_arprofiles \
                    and translate(_('Lab')) + ": " + template.Title() \
                    or template.Title()
                sp_title = template.getSamplePoint()
                st_title = template.getSampleType()
                profile = template.getARProfile()
                t_dict = {
                    'UID':template.UID(),
                    'Title':template.Title(),
                    'ARProfile':profile and profile.UID() or '',
                    'SamplePoint':sp_title,
                    'SampleType':st_title,
                    'ReportDryMatter':template.getReportDryMatter(),
                }
                formdata['templates'][template.UID()] = t_dict

        # Store the default CCs for each client contact in form data.
        for contact in self.context.objectValues("Contact"):
            cc_uids = []
            cc_titles = []
            for cc in contact.getCCContact():
                cc_uids.append(cc.UID())
                cc_titles.append(cc.Title())
            c_dict = {
                'UID':contact.UID(),
                'Title':contact.Title(),
                'cc_uids':','.join(cc_uids),
                'cc_titles':','.join(cc_titles),
            }
            formdata['contact_ccs'][contact.UID()] = c_dict

        uc = getToolByName(self.context, 'uid_catalog')

        ## SamplePoint and SampleType autocomplete lookups need a reference
        ## to resolve Title->UID
        formdata['st_uids'] = {}
        for s in bsc(portal_type = 'SampleType',
                        inactive_review_state = 'active'):
            s = s.getObject()
            formdata['st_uids'][s.Title()] = {
                'uid':s.UID(),
            }

        formdata['sp_uids'] = {}
        for s in bsc(portal_type = 'SamplePoint',
                        inactive_review_state = 'active'):
            s = s.getObject()
            formdata['sp_uids'][s.Title()] = {
                'uid':s.UID(),
                'composite':s.getComposite(),
            }

        return json.dumps(formdata)
