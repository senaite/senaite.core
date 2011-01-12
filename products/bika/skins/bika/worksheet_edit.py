## Script (Python) "worksheet_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
""" There is nothing to edit -> redirect to analyses action
"""
# XXX: There must be a better way than this
context.REQUEST.RESPONSE.redirect(
    '%s/%s' % (context.absolute_url(), 'worksheet_analyses')
)
