## Script (Python) "generateUniqueId"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=type_name=None, batch_size=None
##title=
##
''' overriding plone_scripts/generateUniqueId so that we can dish out
our own ids for transactions and accounts.
'''
# get prefix
prefixes = context.bika_settings.settings.getPrefixes()
type_name.replace(' ', '')
for d in prefixes:
    if type_name != d['portal_type']: continue
    prefix, padding = d['prefix'], d['padding']
    if batch_size:
        next_id = str(context.portal_ids.generate_id(prefix, batch_size=batch_size))
    else:
        next_id = str(context.portal_ids.generate_id(prefix))
    if padding:
        next_id = next_id.zfill(int(padding))
    return '%s%s' % ( prefix, next_id )

if batch_size:
    next_id = str(context.portal_ids.generate_id(type_name,batch_size=batch_size))
else:
    next_id = str(context.portal_ids.generate_id(type_name))
return '%s_%s'% ( type_name.lower(), next_id )

