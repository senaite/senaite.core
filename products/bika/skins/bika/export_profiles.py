## Script (Python) "export_profiles"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

pet = context.profiles_export_tool
results_file = pet.export_file()
return
