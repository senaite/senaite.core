## Script (Python) "result_in_range"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=analysis, sampletype_uid, specification
##title=Check if result in range
##
result_class = ''
result = analysis.getResult()
try:
    result = float(result)
except:
    # if it is not an integer result we assume it is in range
    return ''

service = analysis.getService()
aservice = service.UID()

if analysis.portal_type in ['Analysis', 'RejectAnalysis']:
    if analysis.portal_type == 'RejectAnalysis':
        client_uid = analysis.getRequest().getClientUID()
    else:
        client_uid = analysis.getClientUID()

    if specification == 'lab':
        as = context.portal_catalog(portal_type='LabAnalysisSpec', 
                                    getSampleTypeUID=sampletype_uid) 
    else:
        as = context.portal_catalog(portal_type='AnalysisSpec', 
                                    getSampleTypeUID=sampletype_uid,
                                    getClientUID=client_uid) 

    if as:
        spec_obj = as[0].getObject()
        spec = spec_obj.getResultsRangeDict()
    else:
        return ''

    result_class = 'out_of_range'
    if spec.has_key(aservice):
        spec_min = float(spec[aservice]['min'])
        spec_max = float(spec[aservice]['max'])
        if spec_min <= result <= spec_max:
            result_class = ''
        #else:
        #    """ check if in error range """
        #    error_amount = result * float(spec[aservice]['error']) / 100
        #    error_min = result - error_amount
        #    error_max = result + error_amount
        #    if ((result < spec_min) and (error_max >= spec_min)) or \
        #       ((result > spec_max) and (error_min <= spec_max)):
        #        result_class = 'in_error_range'
    else:
        result_class = ''
            

elif analysis.portal_type == 'StandardAnalysis':
    result_class = ''
    specs = analysis.aq_parent.getResultsRangeDict()
    if specs.has_key(aservice):
        spec = specs[aservice]
        if (result < float(spec['min'])) or (result > float(spec['max'])):
            result_class = 'out_of_range'
    return specs

elif analysis.portal_type == 'DuplicateAnalysis':
    service = analysis.getService()
    service_id = service.getId()
    service_uid = service.UID()
    wf_tool = context.portal_workflow
    if wf_tool.getInfoFor(analysis, 'review_state', '') == 'rejected':
        ws_uid = context.UID()
        for orig in context.portal_catalog(portal_type='RejectAnalysis', 
                                      getWorksheetUID=ws_uid,
                                      getServiceUID=service_uid):
            orig_analysis = orig.getObject()
            if orig_analysis.getRequest().getRequestID() == analysis.getRequest().getRequestID():
                break
    else:
        ar = analysis.getRequest()
        orig_analysis = ar[service_id]
    orig_result = orig_analysis.getResult()
    try:
        orig_result = float(orig_result)
    except ValueError:
        return ''
    dup_variation = service.getDuplicateVariation()
    dup_variation = dup_variation and dup_variation or 0
    range_min = result - (result * dup_variation / 100)
    range_max = result + (result * dup_variation / 100)
    if range_min <= orig_result <= range_max:
        result_class = ''
    else:
        result_class = 'out_of_range'


return result_class

