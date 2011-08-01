## Script (Python) "guard_receive_sample"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=type_name=None
##title=
##
return 1

##if context.portal_type == 'Analysis':
##    return 1
##elif context.portal_type == 'AnalysisRequest':
##    return len(context.objectIds('Analysis')) > 0
