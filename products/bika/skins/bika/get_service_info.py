## Script (Python) "get_service_info"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Get service information for ar add and edit
##
if context.getMemberDiscountApplies():
    discount = True
else:
    discount = False
if context.getClientType() == 'corporate':
    corporate = True
else:
    corporate = False

discount_perc = context.bika_settings.settings.getMemberDiscount()

service_dict = {}
service_list = []
count = 0
for s_proxy in context.portal_catalog(portal_type='AnalysisService',
                sort_on='sortable_title'):
    service = s_proxy.getObject()
    service_dict[count] = {}
    service_dict[count]['uid'] = service.UID()
    if corporate:
        if service.getCorporatePrice() is None:
            price = 0.0
        else:
            price = service.getCorporatePrice()
    else:
        if service.getPrice() is None:
            price = 0
        else:
            price = service.getPrice()
    if discount:
        price = price - (price * discount_perc)/100
    service_dict[count]['price'] = str(price)
    service_dict[count]['vat'] = str(service.getVAT())
    service_dict[count]['id'] = service.getId()
    service_dict[count]['title'] = service.Title()
    service_dict[count]['unit'] = service.getUnit()
    service_dict[count]['accr'] = service.getAccredited()
    service_dict[count]['dm'] = service.getReportDryMatter()
    service_list.append(s_proxy.UID)
    count += 1

profiles = []
if context.portal_type == 'Client':
    client_uid = context.UID()
else:
    client_uid = context.getClientUID()
for proxy in context.portal_catalog(portal_type='ARProfile',
                                    getClientUID = client_uid,
                                    sort_on='sortable_title'):
    profile = proxy.getObject()
    services = ""
    active = False

    for service in profile.getService():
        if (active):
            services += ";"
        else:
            active = True
        service_count = service_list.index(service.UID())
        services += str(service_count)
    
    profiles.append({'uid' : profile.UID(),
                     'title' : profile.getProfileTitle(),
                     'services' : services})

for proxy in context.portal_catalog(portal_type='LabARProfile',
                                    sort_on='sortable_title'):
    profile = proxy.getObject()
    services = ""
    active = False
    for service in profile.getService():
        if (active):
            services += ";"
        else:
            active = True
        service_count = service_list.index(service.UID())
        services += str(service_count)
    
    profiles.append({'uid' : profile.UID(),
                     'title' : 'Lab:' + profile.getProfileTitle(),
                     'services' : services})

results = {}
results['services'] = service_dict
results['profiles'] = profiles
return results
