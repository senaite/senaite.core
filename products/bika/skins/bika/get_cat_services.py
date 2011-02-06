## Script (Python) "get_cat_services"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=cats
##title=Get service information for the specified categories for ar add and edit
##
old_services = []
if context.REQUEST.form.has_key('Services'):
    old_services = context.REQUEST.Services
old_prices = []
if context.REQUEST.form.has_key('Prices'):
    old_prices = context.REQUEST.Prices



if context.portal_type == 'AnalysisRequest':
    for analysis in context.getAnalyses():
        service = analysis.getService()
        if service.getCategoryUID() not in cats:
            cats.append(service.getCategoryUID())
if context.getMemberDiscountApplies():
    discount = True
else:
    discount = False
if context.getClientType() == 'corporate':
    corporate = True
else:
    corporate = False

discount_perc = context.bika_settings.getMemberDiscount()

service_dict = {}
service_list = []
cat_list = []
count = 0

s_proxies = []
if cats:
    c_proxies = context.portal_catalog(portal_type='AnalysisCategory',
             UID=cats,
             sort_on='sortable_title')
    s_proxies = []
    for c_proxy in c_proxies:
        cat_list.append(c_proxy.UID)
        for s_proxy in context.portal_catalog(portal_type='AnalysisService',
                getCategoryUID=c_proxy.UID,
                sort_on='sortable_title'):
            s_proxies.append(s_proxy)

for s_proxy in s_proxies:
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
    service_dict[count]['cat'] = service.getCategoryUID()
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
    categories = []
    
    active = False

    expand = ''
    for service in profile.getService():
        if (active):
            services += ";"
        else:
            active = True
        if service.UID() in service_list:
            service_count = service_list.index(service.UID())
            services += str(service_count)
        else:
            if service.getCategoryUID() not in categories:
                if len(expand) > 0:
                    expand += ', '
                expand += service.getCategoryName()
                categories.append(service.getCategoryUID())
    
    profiles.append({'uid' : profile.UID(),
                     'title' : profile.getProfileTitle(),
                     'expand' : expand,
                     'services' : services})

for proxy in context.portal_catalog(portal_type='LabARProfile',
                                    sort_on='sortable_title'):
    profile = proxy.getObject()
    services = ""
    categories = []
    active = False
    expand = ''
    for service in profile.getService():
        if (active):
            services += ";"
        else:
            active = True
        if service.UID() in service_list:
            service_count = service_list.index(service.UID())
            services += str(service_count)
        else:
            if service.getCategoryUID() not in categories:
                if len(expand) > 0:
                    expand += ', '
                expand += service.getCategoryName()
                categories.append(service.getCategoryUID())
    
    profiles.append({'uid' : profile.UID(),
                     'title' : 'Lab:' + profile.getProfileTitle(),
                     'expand' : expand,
                     'services' : services})

# repost all the form items
for key, value in context.REQUEST.form.items():
    if not key.startswith('ar'):
        continue

    # copy value so that we can manipulate it
    value = value.copy()

    # set total fields
    for k in ('Subtotal_submit', 'VAT_submit', 'Total_submit'):
        if not value.has_key(k):
            continue
        flat_key = '%s.%s' % (key, k)
        context.REQUEST.set(flat_key, value.get(k))
        del value[k]

    for k in ('Contact', 'CCEmails', 'ClientReference', 'ClientSampleID', 'SampleType', 'SamplePoint', 'ClientOrderNumber', 'Analysis', 'ReportDryMatter', 'InvoiceExclude', 'profileTitle', 'arprofiles', 'DateSampledYear', 'DateSampledMonth', 'DateSampledDay'):
        flat_key = '%s.%s' % (key, k)
        if value.has_key(k):
            if k == 'Analysis':
                analysis = []
                selectedServices = ''
                for as in value[k]:
                    uid = old_services[as]
                    new_count = service_list.index(uid)
                    analysis.append(str(new_count))
                    if selectedServices:
                        selectedServices += ','
                    selectedServices += str(new_count)
                context.REQUEST.set(flat_key, analysis)
                ss_key = '%s.%s' % (key, 'selectedservices')
                context.REQUEST.set(ss_key, selectedServices)
            else:
                context.REQUEST.set(flat_key, value.get(k))

results = {}
results['categories'] = cat_list
results['services'] = service_dict
results['profiles'] = profiles
return results

