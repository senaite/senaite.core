plone_view = context.restrictedTraverse('@@plone')
request = context.REQUEST
from_date = None
to_date = None
client_uid = None
tats = {}

if request.has_key('FromDate'):
    from_date = request.FromDate
    tats['FromDate'] = plone_view.toLocalizedTime(from_date, long_format=0)
else:
    tats['FromDate'] = None
if request.has_key('ToDate'):
    to_date = request.ToDate
    tats['ToDate'] = plone_view.toLocalizedTime(to_date, long_format=0)
else:
    tats['ToDate'] = None

if from_date and to_date:
    query = {'query': [from_date, to_date],
             'range': 'min:max'}
elif from_date or to_date:
    query = {'query': from_date or to_date,
             'range': from_date and 'min' or 'max'}

if request.has_key('ClientUID'):
    client_uid = request.ClientUID
    client = context.reference_catalog.lookupObject(client_uid) 
    tats['client'] = client.Title()
else:
    tats['client'] = 'All clients'

""" find all analysis requests in the selected date range """
""" must be a better way to do this """
if from_date or to_date:
    """ first need to read the analysis requests """
    if client_uid:
        results = context.portal_catalog.searchResults(
                        portal_type='AnalysisRequest',
                        getDateReceived=query,
                        getClientUID=client_uid)
    else:
        results = context.portal_catalog.searchResults(
                        portal_type='AnalysisRequest',
                        getDateReceived=query)
    """ read the analyses for these requests """
    ar_ids = []
    for result in results:
        ar_ids.append(result.getRequestID)
    results = context.portal_catalog.searchResults(
                        portal_type='Analysis',
                        review_state='published',
                        getRequestID=ar_ids)

    client_proxy = context.portal_catalog.searchResults(
                        portal_type='Client',
                        getClientUID=client_uid)
    for c in client_proxy:
        c.getObject()
        client = c.Title()
        tats['client'] = c.Title()
else:
    if client_uid:
        results = context.portal_catalog.searchResults(
                        portal_type='Analysis',
                        review_state='published',
                        getClientUID=client_uid)
    else:
        results = context.portal_catalog.searchResults(
                        portal_type='Analysis',
                        review_state='published')

""" group analyses by service """
total_count_early = 0
count_early = 0
total_mins_early = 0
mins_early = 0
total_count_late = 0
count_late = 0
total_mins_late = 0
mins_late = 0
total_count_undefined = 0
count_undefined = 0
serv = {}
for result in results:
    analysis = result.getObject()
    service = analysis.getId()
    if not serv.has_key(service):
        serv[service] = {'count_early': 0,
                         'count_late': 0,
                         'mins_early': 0,
                         'mins_late': 0,
                         'count_undefined': 0,
                         }
    earliness = analysis.getEarliness()
    if earliness < 0:
        count_late = serv[service]['count_late']
        mins_late = serv[service]['mins_late']
        count_late += 1
        mins_late -= earliness
        total_count_late += 1
        total_mins_late -= earliness
        serv[service]['count_late'] = count_late
        serv[service]['mins_late'] = mins_late
    if earliness > 0:
        count_early = serv[service]['count_early']
        mins_early = serv[service]['mins_early']
        count_early += 1
        mins_early += earliness
        total_count_early += 1
        total_mins_early += earliness
        serv[service]['count_early'] = count_early
        serv[service]['mins_early'] = mins_early
    if earliness == 0:
        count_undefined = serv[service]['count_undefined']
        count_undefined += 1
        total_count_undefined += 1
        serv[service]['count_undefined'] = count_undefined

l = serv.keys()
l.sort()
for service in l:
    count_early = serv[service]['count_early']
    mins_early = serv[service]['mins_early']
    if count_early == 0:
        serv[service]['ave_early'] = ''
    else:
        totmins = (mins_early) / count_early
        serv[service]['ave_early'] = context.format_duration(totmins)

    count_late = serv[service]['count_late']
    mins_late = serv[service]['mins_late']
    if count_late == 0:
        serv[service]['ave_late'] = ''
    else:
        totmins = mins_late / count_late
        serv[service]['ave_late'] = context.format_duration(totmins)

""" sort into categories """
cats = {}
for cat in context.portal_catalog(portal_type="AnalysisCategory",
                              sort_on="sortable_title"):
    for service in context.portal_catalog(portal_type="AnalysisService",
                              getCategoryUID=cat.UID,
                              sort_on="sortable_title"):
        s_id = service.getId
        if serv.has_key(s_id):
            if not cats.has_key(cat.Title):
                cats[cat.Title] = []
            services = cats[cat.Title]
            s_dict = {'title':service.Title,
                      'id':service.getId,
                      'c_e':serv[s_id]['count_early'],
                      'c_l':serv[s_id]['count_late'],
                      'c_u':serv[s_id]['count_undefined'],
                      'a_e':serv[s_id]['ave_early'],
                      'a_l':serv[s_id]['ave_late']}
            services.append(s_dict)
            cats[cat.Title] = services

tats['count_late'] = total_count_late
tats['count_early'] = total_count_early
tats['count_undefined'] = total_count_undefined
if total_count_late == 0:
    tats['ave_late'] = ''
else:
    totmins = total_mins_late / total_count_late
    tats['ave_late'] = context.format_duration(totmins)
    
if total_count_early == 0:
    tats['ave_early'] = ''
else:
    totmins = total_mins_early / total_count_early
    tats['ave_early'] = context.format_duration(totmins) 
tats['cats'] = cats
    
return tats

