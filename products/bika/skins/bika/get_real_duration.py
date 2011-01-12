## Script (Python) "get_real_duration"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=starttime, endtime
##title=Get real duration time
##

start = DateTime(starttime)
end = DateTime(endtime)
totminutes =  int((end - start) * 24 * 60)
mins = totminutes % 60
hours = (totminutes - mins) / 60

mins_str = '%sm' % mins

if hours:
    hours_str = '%sh' % hours
else:
    hours_str = ''

return '%s%s' % (hours_str, mins_str)

