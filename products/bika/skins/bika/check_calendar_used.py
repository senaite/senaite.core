## Script (Python) "check_calendar_used"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Check whether the bika calendar is in use
##
portal = context.portal_url.getPortalObject()
if 'calendars' in portal.objectIds():
    days = context.portal_catalog(portal_type='BCDefaultDay')
    if days:
        return True
    else:
        return False
else:
    return False


