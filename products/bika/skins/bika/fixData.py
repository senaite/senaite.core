## Script (Python) "fixData"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=fix data changed in fixIS
##
for proxy in context.portal_catalog(portal_type="StandardSample"):
    ss = proxy.getObject()
    old_id = ss.getId()
    ss_id = context.generateUniqueId('StandardSample')
    ss.setStandardID(ss_id)
    ss.setStandardDesription(ss.Title())
    parent = ss.aq_parent
    parent.manage_renameObject(old_id, ss_id)
    ss.reindexObject()

return 'ok'
