## Script (Python) "guard_unassign"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

if context.portal_type != 'AnalysisRequest':
    return True

if context.getAnalyses(worksheetanalysis_review_state = 'unassigned'):
    return True

return False
