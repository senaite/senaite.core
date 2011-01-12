## Script (Python) "get_analysespersampletype"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=fromdate, todate, clientuid
##title=report count of analyses per sample type
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

st_titles = {}      # sample types and counts
st_counts = {}      # sample types and counts

for st in context.portal_catalog(portal_type="SampleType",
                                 sort_on='sortable_title'):
    st_titles[st.Title] = st.UID
    st_counts[st.UID] = 0

if fromdate or todate:
    if clientuid:
        ar_proxies = context.portal_catalog(portal_type="AnalysisRequest",
                                            getClientUID=clientuid,
                                            getDateReceived=query)
    else:
        ar_proxies = context.portal_catalog(portal_type="AnalysisRequest",
                                            getDateReceived=query)
else:
    if clientuid:
        ar_proxies = context.portal_catalog(portal_type="AnalysisRequest",
                                            getClientUID=clientuid)
    else:
        ar_proxies = context.portal_catalog(portal_type="AnalysisRequest")

for proxy in ar_proxies:
    ar = proxy.getObject()
    count = len(context.portal_catalog(portal_type="Analysis",
                                       getRequestID=ar.getRequestID()))
    st_uid = ar.getSample().getSampleTypeUID()
    st_count = st_counts[st_uid] + count
    st_counts[st_uid] = st_count

titles = st_titles.keys()
titles.sort()
sampletypes = []
for title in titles:
    sampletypes.append((title, st_counts[st_titles[title]]))

return sampletypes
    
                


