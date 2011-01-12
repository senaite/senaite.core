## Script (Python) "group_analyses_by_service"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=analyses
##title=
##
d = {}
for analysis in analyses:
    d[analysis.getId()] = analysis
return d
