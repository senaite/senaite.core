## Script (Python) "get_analysis_dependancies"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=analysis
##title=Get analysis dependancies 
##
required_uids = []
required_keys = []
uids_checked = []
as_to_check = []
uids_checked.append(analysis.UID())
as_to_check = analysis.getCalcDependancy()
for as in as_to_check:
    if as.UID() in uids_checked:
        continue
    uids_checked.append(as.UID())
    if as.UID() not in required_uids:
        required_uids.append(as.UID())
        required_keys.append(as.getAnalysisKey())
        for more in as.getCalcDependancy():
            as_to_check.append(more)

required = {}
required['uids'] = required_uids
required['keys'] = required_keys
return required
