## Script (Python) "get_valid_analyses"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=analyses
##title=
##
valid_analyses = []
for analysis in analyses:
    if analysis.getResult():
        try:
            result = float(analysis.getResult())
            valid_analyses.append(analysis)
        except ValueError:
            continue
return valid_analyses
