## Script (Python) "get_worksheet_query_results"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
if context.REQUEST.form.has_key('getCategoryUID'):
    category = context.REQUEST.form['getCategoryUID']
else:
    category = None

if context.REQUEST.form.has_key('getServiceUID'):
    service = context.REQUEST.form['getServiceUID']
else:
    service = None

if context.REQUEST.form.has_key('getClientUID'):
    client = context.REQUEST.form['getClientUID']
else:
    client = None

if category and not service:
    s_uids = []
    for s_proxy in context.portal_catalog(portal_type="AnalysisService",
                    getCategoryUID=category):
        s_uids.append(s_proxy.UID)
proxies = []
if service and client:
    proxies = context.portal_catalog(portal_type="Analysis",
                                     review_state="sample_received",
                                     getServiceUID=service,
                                     getClientUID=client,
                                     sort_on="getDueDate")
elif category and client:
    proxies = context.portal_catalog(portal_type="Analysis",
                                     review_state="sample_received",
                                     getServiceUID=s_uids,
                                     getClientUID=client,
                                     sort_on="getDueDate")
elif service:
    proxies = context.portal_catalog(portal_type="Analysis",
                                     review_state="sample_received",
                                     getServiceUID=service,
                                     sort_on="getDueDate")
elif category:
    proxies = context.portal_catalog(portal_type="Analysis",
                                     review_state="sample_received",
                                     getServiceUID=s_uids,
                                     sort_on="getDueDate")
elif client:
    proxies = context.portal_catalog(portal_type="Analysis",
                                     review_state="sample_received",
                                     getClientUID=client,
                                     sort_on="getDueDate")
else:
    proxies = context.portal_catalog(portal_type="Analysis",
                                     review_state="sample_received",
                                     sort_on="getDueDate")
results = []
analyses = []
duedate = None

for proxy in proxies:
    analysis = proxy.getObject()
    if analysis.getDueDate() != duedate:
        sort_on = (('getRequestID', 'nocase', 'asc'),('Title', 'nocase', 'asc'),)
        analyses = sequence.sort(analyses, sort_on)
        results.extend(analyses)
        analyses = []
        duedate = analysis.getDueDate()
    analyses.append(analysis)
if analyses:
    results.extend(analyses)

return results
