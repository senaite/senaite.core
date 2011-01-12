## Script (Python) "migrate_101_110"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Migrate Bika 101 to 110
##
portal = context.portal_url.getPortalObject()

qi_tool = portal.portal_quickinstaller
qi_tool.reinstallProducts( ['ATExtensions',])
qi_tool.installProducts( ['ATSchemaEditorNG',])
qi_tool.reinstallProducts( ['bika',])

#upgrade to Plone 2.1.x
upgrade_tool = portal.portal_migration
upgrade_tool.upgrade()

portal.portal_properties.site_properties.manage_changeProperties(
    disable_folder_sections=1)

# Do post plone install migrations
from Products.bika.Extensions.post_plone_install import run
run(portal)

portal.portal_catalog.refreshCatalog(clear=1)

right_slots = (
    'here/portlet_late_analyses/macros/portlet',
    'here/portlet_pending_orders/macros/portlet',
    'here/portlet_sample_due/macros/portlet',
    'here/portlet_verified/macros/portlet',
    'here/portlet_review/macros/portlet',
)
portal.manage_changeProperties(right_slots=right_slots)

del_ids = []
for obj_id in ['index_html', 'Members', 'front-page', 'news',
               'events']:
    if obj_id in portal.objectIds():
        del_ids.append(obj_id)

if del_ids:
    portal.manage_delObjects(ids=del_ids)

return 'Upgrade to Bika 1.1.0 completed successfully'
