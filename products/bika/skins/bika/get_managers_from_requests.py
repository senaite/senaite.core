## Script (Python) "get_managers_from_requests"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=batch
##title=Get services from requests
##
managers = {'ids': [],
            'dict': {}}
departments = {}
for ar in batch:
    ar_mngrs = ar.getResponsible()
    for id in ar_mngrs['ids']:
        new_depts = ar_mngrs['dict'][id]['dept'].split(',')
        if id in managers['ids']:
            for dept in new_depts:
                if dept not in departments[id]:
                    departments[id].append(dept)
        else:
            departments[id] = new_depts
            managers['ids'].append(id)
            managers['dict'][id] = ar_mngrs['dict'][id]

mngrs = departments.keys()
for mngr in mngrs:
    final_depts = ''
    for dept in departments[mngr]:
        if final_depts:
            final_depts += ', '
        final_depts += dept
    managers['dict'][mngr]['dept'] = final_depts

return managers 
