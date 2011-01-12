## Script (Python) "get_arprofiles"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Get client and lab analysis profiles
##
profiles = []

for proxy in context.portal_catalog(portal_type='ARProfile',
                                    getClientUID = context.UID()):
    profile = proxy.getObject()
    services = ""
    active = False

    for service in profile.getService():
        if (active):
            services += ";"
        else:
            active = True
        services += service.UID()
    
    profiles.append({'uid' : profile.UID(),
                     'title' : profile.getProfileTitle(),
                     'services' : services})

for proxy in context.portal_catalog(portal_type='LabARProfile'):
    profile = proxy.getObject()
    services = ""
    active = False
    for service in profile.getService():
        if (active):
            services += ";"
        else:
            active = True
        services += service.UID()
    
    profiles.append({'uid' : profile.UID(),
                     'title' : 'Lab:' + profile.getProfileTitle(),
                     'services' : services})

return profiles
