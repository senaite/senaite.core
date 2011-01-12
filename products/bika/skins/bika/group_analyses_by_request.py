## Script (Python) "group_analyses_by_request"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=batch
##title=
##
plone_view = context.restrictedTraverse('@@plone')
any_titr_vol_reqd = False
any_weight_calc_reqd = False

r = {}
for analysis in batch:
    ar = analysis.aq_parent
    ar_id = ar.getId()
    sample = ar.getSample()
    sampletype = sample.getSampleType()
    samplepoint = sample.getSamplePoint() and sample.getSamplePoint().Title()
    if not r.has_key(ar_id):
        date_received = ar.getDateReceived()
        date_published = ar.getDatePublished()
        if date_published:
            date_published = plone_view.toLocalizedTime(date_published, long_format=1)
        r[ar_id] = { 'id': ar_id, 
                     'RequestID': ar.getRequestID(),
                     'absolute_url': ar.absolute_url(),
                     'Client': ar.aq_parent,
                     'SampleID': sample.getSampleID(),
                     'Hazardous': sampletype.getHazardous(),
                     'sample_absolute_url': sample.absolute_url(),
                     'SamplePoint': samplepoint,
                     'SampleType': sampletype.Title(),
                     'sampletype_obj': sampletype,
                     'ClientReference': sample.getClientReference(),
                     'ClientSampleID': sample.getClientSampleID(),
                     'DateRequested': plone_view.toLocalizedTime(
                         ar.getDateRequested(), long_format=1
                         ),
                     'DateReceived': plone_view.toLocalizedTime(
                         date_received, long_format=1
                         ),
                     'DatePublished': date_published,
                     'AnyTitrReqd': False,
                     'AnyWeightReqd': False,
                     'Analyses': {},
                     'AnalysisType':'A',
                   }

    d = r[ar_id]['Analyses']
    d[analysis.getId()] = analysis
    if analysis.getTitrationRequired():
        r[ar_id]['AnyTitrReqd'] = True
    if analysis.getWeightRequired():
        r[ar_id]['AnyWeightReqd'] = True

l = r.keys()
l.sort()
result_set = {}
result_set['results'] = [r[ar_id] for ar_id in l]
result_set['titr_reqd'] = any_titr_vol_reqd
result_set['weight_reqd'] = any_weight_calc_reqd
return result_set

