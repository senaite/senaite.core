## Controller Python Script "duplicate_service"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Duplicates analysis services
##

status='failure'
message='Please select one or more services to duplicate.'
state.setNextAction('redirect_to:string:analysisservices')

if context.REQUEST.form.has_key('ids'):
    # for items to duplicate...
    ids=context.REQUEST.get('ids', [])
    titles=[]

    navId=''
    for id in ids:
        obj=context.restrictedTraverse(id)
        titles.append(obj.title_or_id())
        dupId=obj.duplicateService(context=context)
        if navId=='':
            navId=dupId

    if ids:
        status='success'
        message=', '.join(titles)+' have been duplicated.'
        state.setNextAction('traverse_to:string:analysisservices/%s' % navId)

return state.set(status=status, portal_status_message=message)


