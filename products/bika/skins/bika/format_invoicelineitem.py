## Script (Python) "format_invoicelineitem"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=description
##title=
##
if not description:
    return description

parts = str(description).split(' ')
if not parts:
    return description

id = parts[0]
rs = context.portal_catalog(id=id)

if not rs:
    return description
else:
    url = rs[0].getURL()
    description = ' '.join(parts[1:])
    return '<a href="%s">%s</a> %s' % (url, id, description)
