## Script (Python) "get_toggle_title"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=state, states
##title=Get toggle title
##
for item in states:
    if state == item['id']:
        return item['title'].lower()
return 'unknown'
