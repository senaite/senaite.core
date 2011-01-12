## Script (Python) "get_worksheet_services"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Get worksheet services
##
analyses = context.getAnalyses()
standards = context.getStandardAnalyses()   # includes blanks
duplicates = context.objectValues('DuplicateAnalysis')
rejects = context.objectValues('RejectAnalysis')
services = {}
for analysis in analyses:
    service = analysis.getService()
    services[service.UID()] = service
for analysis in duplicates:
    service = analysis.getService()
    services[service.UID()] = service
for analysis in standards:
    service = analysis.getService()
    services[service.UID()] = service
for analysis in rejects:
    service = analysis.getService()
    services[service.UID()] = service

return services.values()
