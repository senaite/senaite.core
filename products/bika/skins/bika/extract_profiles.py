## Script (Python) "extract_profiles"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Extract AR profiles to csv file
##
spec = context.REQUEST.get('getClientUID', 'lab')
arpet = context.profiles_export_tool
results_file = arpet.export_file(spec)
return
