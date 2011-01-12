## Script (Python) "format_date_query"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=field_id
##title=
##

from_date = context.REQUEST.get('%s_fromdate' % field_id, None)
to_date = context.REQUEST.get('%s_todate' % field_id, None)
# if date was selected and then deselected in form, the following invalid
# date value is submitted - remove this 
if from_date:
    if from_date[5:] == '00-00':
        from_date = None
    if from_date:
        from_date = from_date[:10] + ' 00:00'
if to_date:
    if to_date[5:] == '00-00':
        to_date = None
    if to_date:
        to_date = to_date[:10] + ' 23:59'
if from_date and to_date:
    query = {'query': [from_date, to_date],
             'range': 'min:max'}
    context.REQUEST.set(field_id, query)
elif from_date or to_date:
    query = {'query': from_date or to_date,
             'range': from_date and 'min' or 'max'}
    context.REQUEST.set(field_id, query)
