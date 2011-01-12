## Script (Python) "fix_disposal_dates"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Fix disposal dates
##

# Sets the DisposalDate of all Samples according to the RetentionPeriod of their SampleTypes

for sample in context.portal_catalog(portal_type='Sample'):
    obj = sample.getObject()
    dis_date = obj.disposal_date()
    obj.setDisposalDate(dis_date)


return 'ok'

