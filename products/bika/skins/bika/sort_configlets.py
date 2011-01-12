## Script (Python) "sort_configlets"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=configlets
##title=
##

def sortfunc(a, b):
    if a['name'] > b['name']:
        return 1
    elif a['name'] < b['name']:
        return -1
    elif a['name'] == b['name']:
        return 0

configlets.sort(sortfunc)
return configlets
