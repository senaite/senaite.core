## Script (Python) "guard_receive_sample"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=type_name=None
##title=
##
if context.portal_type == 'AnalysisRequest':
    return 0
return 1
