## Script (Python) "get_duplicate_results"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=duplicate_analyses
##title=
##
analyses = []
mean_results = []
rel_errors = []
for dup in duplicate_analyses:
    analysis = dup.getRealAnalysis()
    try:
        dup_result = float(dup.getResult())
        real_result = float(analysis.getResult())
    except ValueError:
        continue
    mean_result = (dup_result + real_result) / 2
    rel_error = (dup_result - real_result) / mean_result * 100
    mean_str = '%.2f' %mean_result
    error_str = '%.2f' %rel_error
    these_results = {
         'ar': analysis.getRequestID(),
         'real': real_result,
         'dup':  dup_result,
         'mean': mean_str,
         'error': error_str,
         'ws': dup.aq_parent.getNumber(),
         'ws_url': dup.aq_parent.absolute_url(),
         'ar_url': analysis.aq_parent.absolute_url(),
         'vdate': dup.getDateVerified(), 
        }
    analyses.append(these_results)
    
return analyses
