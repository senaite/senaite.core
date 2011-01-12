## Script (Python) "extract_services"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Extract analysis services to csv file
##
aset = context.services_export_tool
results_file = aset.export_file()
return
