## Script (Python) "get_analysisrequest_dependancies"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=Requirement
##title=Get analysis request dependancies 
##
required_keys = []
required_uids = []
if Requirement == 'DryMatter':
    drymatter = context.bika_settings.getDryMatterService()
    if drymatter:
        required_keys.append(drymatter.getAnalysisKey())
        required_uids.append(drymatter.UID())
    moisture = context.bika_settings.getMoistureService()
    if moisture:
        required_keys.append(moisture.getAnalysisKey())
        required_uids.append(moisture.UID())

required = {}
required['uids'] = required_uids
required['keys'] = required_keys
return required
