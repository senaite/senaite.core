## Script (Python) "guard_submit_worksheet"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
if (context.getAnalyser() is None) or (context.getAnalyser() == ''):
    return False
analyses = context.getAllAnalyses()
if analyses:
    for a in analyses:
        if (a.getResult() is None) or (a.getResult() == ''):
            return False
    return True
else:
    return False
