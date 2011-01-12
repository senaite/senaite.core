## Script (Python) "get_services_from_requests"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=batch
##title=Get services from requests ordered by category
##
all_services = []
unsorted = []
cats = {}
any_accredited = False
any_drymatter = False
for ar in batch:
    if ar.getReportDryMatter():
        any_drymatter = True
    for analysis in ar.getPublishedAnalyses():
        service = analysis.getService()
        if service.UID() in unsorted:
            continue
        unsorted.append(service.UID())
        if cats.has_key(service.getCategoryName()):
            services = cats[service.getCategoryName()]
        else:
            services = []
        services.append(service)
        cats[service.getCategoryName()] = services
        if (service.getAccredited()):
            any_accredited = True
        
cat_keys = cats.keys()
cat_keys.sort(lambda x, y:cmp(x.lower(), y.lower()))
for cat_key in cat_keys:
    services = cats[cat_key]
    services.sort(lambda x, y:cmp(x.Title().lower(), y.Title().lower()))
    for service in services:
        all_services.append(service)

return {'Services': all_services, 'Accredited': any_accredited,
        'DryMatter': any_drymatter}
