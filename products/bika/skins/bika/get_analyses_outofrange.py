## Script (Python) "get_analyses_outofrange"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=specification, fromdate, todate
##title=report all analyses with results out of specification range
##
# if date was selected and then deselected in form, the following invalid
# date value is submitted - remove this 
if fromdate:
    if fromdate[5:] == '00-00':
        fromdate = None
    if fromdate:
        fromdate = fromdate[:10] + ' 00:00'
if todate:
    if todate[5:] == '00-00':
        todate = None
    if todate:
        todate = todate[:10] + ' 23:59'
if fromdate and todate:
    query = {'query': [fromdate, todate],
             'range': 'min:max'}
elif fromdate or todate:
    query = {'query': fromdate or todate,
             'range': fromdate and 'min' or 'max'}

if fromdate or todate:
    ar_proxies = context.portal_catalog(portal_type="AnalysisRequest",
                                     getDateReceived=query)
else:
    ar_proxies = context.portal_catalog(portal_type="AnalysisRequest")
#st_desc: {uid = 'meal'}
#client_desc: {client_id/'lab' = {'name': 'Client Name'
#                                 {'url': 'Client url'}
#st_spec: {client_id/'lab' = {st_id: {service_id: (min,max)}

cat_desc = {}     # category description
as_cats = {}     # categories per analysis service
st_desc = {}      # sample type description
sp_desc = {}      # sample point description
clients = {}      # client name and url
as_desc = {}      # analysis service description
st_spec = {}
analyses = []
item = {}

wf_tool = context.portal_workflow
spec = 'lab'
for ar_proxy in ar_proxies:
    ar = ar_proxy.getObject()
    sample = ar.getSample()
    st_uid = sample.getSampleTypeUID()
    st_id = sample.getSampleType().getId()
    client_uid = ar.getClientUID()
    client_id = ar.aq_parent.getId()
    if specification == 'client':
        spec = client_id
    if not st_spec.has_key(spec):
        st_spec[spec] = {}
    if st_spec[spec].has_key(st_id):
        if st_spec[spec][st_id] == None:
            continue
    else:
        if specification == 'client':
            spec_proxies = context.portal_catalog(portal_type="AnalysisSpec",
                                            getClientUID=client_uid,
                                            getSampleTypeUID=st_uid)
            
        else:
            spec_proxies = context.portal_catalog(portal_type="LabAnalysisSpec",
                                            getSampleTypeUID=st_uid)
        if len(spec_proxies) == 0:
            st_spec[spec][st_id] = None
            continue
        else:
            st_spec[spec][st_id] = {}
            new_services = {}
            for spec_proxy in spec_proxies:
                spec_rec = spec_proxy.getObject()
                for row in spec_rec.getResultsRange():
                    new_services[row['service']] = \
                         (float(row['min']), float(row['max']))
                st_spec[spec][st_id] = new_services
            
    ar_analyses = ar.getAnalyses()
    for analysis in ar_analyses:
        item = {}
        as_uid = analysis.getServiceUID()
        if not st_spec[spec][st_id].has_key(as_uid):
            continue
       
        if analysis.getResult():
            try:
                result = float(analysis.getResult())
            except:
                continue
        else:
            continue
        if result < st_spec[spec][st_id][as_uid][0] \
        or result > st_spec[spec][st_id][as_uid][1]:
            if not clients.has_key(client_id):
                clients[client_id] = {}
                clients[client_id]['name'] = ar.aq_parent.Title()
                clients[client_id]['url'] = ar.aq_parent.absolute_url()
            item['client'] = client_id
            item['ar'] = ar.getRequestID()
            item['result'] = result
            item['min'] = st_spec[spec][st_id][as_uid][0]
            item['max'] = st_spec[spec][st_id][as_uid][1]
            item['st'] = st_id
            if not st_desc.has_key(st_id):
                st_desc[st_id] = sample.getSampleType().Title()
            if sample.getSamplePoint():
                sp_id = sample.getSamplePoint().getId()
                if not sp_desc.has_key(sp_id):
                    sp_desc[sp_id] = sample.getSamplePoint().Title()
            else:
                sp_id = None
            item['sp'] = sp_id
            item['as'] = as_uid
            if not as_cats.has_key(as_uid):
                service = analysis.getService()
                as_cats[as_uid] = service.getCategoryUID()
                if not cat_desc.has_key(service.getCategoryUID()):
                    cat_desc[service.getCategoryUID()] = service.getCategoryName()
            item['cat'] = as_cats[as_uid]
            if not as_desc.has_key(as_uid):
                as_desc[as_uid] = analysis.Title()

            item['rs'] = wf_tool.getInfoFor(analysis, 'review_state', '')
            analyses.append(item)

results = {}
results['analyses'] = analyses
results['st'] = st_desc
results['sp'] = sp_desc
results['as'] = as_desc
results['cat'] = cat_desc
results['clients'] = clients
return results

