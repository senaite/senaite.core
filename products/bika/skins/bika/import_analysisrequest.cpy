## Script (Python) "import_analysisrequest"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=
##
arit = context.ar_import_tool
client = context.REQUEST.ClientID
infile = context.REQUEST.csvfile
option = context.REQUEST.ImportOption
if option == 'c':
    result = arit.import_file(infile.readlines(), infile.filename, client, state)
elif option == 'p':
    pass
elif option == 's':
    result = arit.import_file_s(infile.readlines(), client, state)
return state
