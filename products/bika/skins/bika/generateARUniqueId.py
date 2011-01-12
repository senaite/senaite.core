## Script (Python) "generateARUniqueId"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=type_name=None,sample_id,ar_number
##title=
##
''' overriding plone_scripts/generateUniqueId so that we can dish out
our own ids for transactions and accounts.
Analysisrequests are numbered as subnumbers of the associated sample,
'''
# get prefix
prefixes = context.bika_settings.settings.getPrefixes()
type_name = type_name.replace(' ', '')
for d in prefixes:
    if type_name == d['portal_type']:
        padding = int(d['padding'])
        prefix  = d['prefix']
        break
sample_id_bits = sample_id.split('-')
sample_number = sample_id_bits[1]

ar_id = prefix + sample_number + '-' + str(ar_number).zfill(padding)

""" if there have been more than 99 requests on this sample - error  
"""
    
return ar_id

