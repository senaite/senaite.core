## Script (Python) "getDisplayView"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=value, join=', '
##title=
##
if same_type(value, '') or same_type(value, u''):
    return value
try:
    return join.join(value)
except TypeError:
    return value
