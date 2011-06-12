## Script (Python) "guard_publish_analysis"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
return True
if context.portal_type == "Analysis":
    if context.getReportDryMatter():
        return context.getResultDM() is not None
elif context.portal_type == 'AnalysisRequest':
    # Only transition to 'published' if all analyses which require
    # dry matter reporting have dry matter results
    if context.getReportDryMatter():
        for analysis in context.objectValues('Analysis'):
            if analysis.getReportDryMatter():
                if analysis.getResultDM() is None:
                    return False
    return True
