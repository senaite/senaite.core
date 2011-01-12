## Script (Python) "export_analysisservices"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

aset = context.services_export_tool
results_file = aset.export_file(context.REQUEST, context.RESPONSE)
return
