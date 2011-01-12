## Script (Python) "get_billing_address"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=org, innerJoin=None, outerJoin=None
##title=
##
""" Compute the billing address for a statement or order
"""
# try billing address first then fall back physical address
for field_id in ('BillingAddress', 'PhysicalAddress'):
    if not org.Schema().has_key(field_id):
        continue
    field = org.Schema()[field_id]
    # join with blank string to check if subfields are filled in
    address = field.getSubfieldViews(org, '')
    if address:
        outerJoin = outerJoin or field.outerJoin
        innerJoin = innerJoin or field.innerJoin
        subfieldViews = field.getSubfieldViews(org, innerJoin)
        return outerJoin.join(subfieldViews)

return ''
