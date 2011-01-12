## Script (Python) "query_analysis_requests"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST=None
##title=
##
if REQUEST is None:
    REQUEST = context.REQUEST


request_ids = []
# Do we need to query analyses?
service_uids = []
if REQUEST.has_key('ServiceUID'):
    service_uids.append(REQUEST.get('ServiceUID'))
elif REQUEST.has_key('CategoryUID'):
    category_uid = REQUEST.get('CategoryUID')
    for s in context.portal_catalog(portal_type='AnalysisService',
                    getCategoryUID=category_uid):
        service_uids.append(s.UID)
if service_uids:
    if REQUEST.has_key('getRequestID'):
        request_ids = [REQUEST.get('getRequestID')]

    query = {
        'portal_type': 'Analysis',
        'getServiceUID': service_uids,
    }

    
    a_proxies = context.portal_catalog(query)
    if a_proxies:
        for b in a_proxies:
            request_ids.append(b.getRequestID)
    else:
        # if no analyses found, then no ARs can be found
        REQUEST.set('getId', 'dummy')


    REQUEST.set('getRequestID', request_ids)


sampletype = False
sample_uids = []
samplequery = {
    'portal_type': 'Sample',
}
if REQUEST.has_key('SampleTypeUID'):
    samplequery['getSampleTypeUID'] = REQUEST.get('SampleTypeUID')
    sampletype = True
if REQUEST.has_key('ClientReference'):
    samplequery['getClientReference'] = REQUEST.get('ClientReference')
    sampletype = True
if REQUEST.has_key('ClientSampleID'):
    samplequery['getClientSampleID'] = REQUEST.get('ClientSampleID')
    sampletype = True
if REQUEST.has_key('SamplePointUID'):
    samplequery['getSamplePointUID'] = REQUEST.get('SamplePointUID')
    sampletype = True
if REQUEST.has_key('DateSampled'):
    samplequery['getDateSampled'] = REQUEST.get('DateSampled')
    sampletype = True
if REQUEST.has_key('SubmittedByUser'):
    samplequery['getSubmittedByUser'] = REQUEST.get('SubmittedByUser')
    sampletype = True
if sampletype:
    for b in context.portal_catalog(samplequery):
        sample_uids.append(b.UID)
    if sample_uids:
        REQUEST.set('getSampleUID', sample_uids)
    else:
        # if no sample found, then no ARs can be found
        REQUEST.set('getSampleUID', 'dummy')
    


REQUEST.set('portal_type', 'AnalysisRequest')
REQUEST.set('sort_on', 'getRequestID');
REQUEST.set('sort_order', 'reverse');

return context.queryCatalog()


