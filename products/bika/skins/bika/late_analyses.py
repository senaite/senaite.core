## Script (Python) "late_analyses"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=startdate
##title=
##

#month = startdate.month()
#year = startdate.year()
#nextmonth = startdate + 32
#enddate = DateTime('%s-%02d-01' % (nextmonth.year(), nextmonth.month())) - 1

now = DateTime()

la_proxies = context.portal_catalog(portal_type='AnalysisRequest', 
            getDueDate={
                'query': [now,], 
                'range': 'min'
            },
            review_state='sample_due',
            )
las = []
for la in la_proxies:
    las.append(la.getObject())



return las       
