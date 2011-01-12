## Controller Python Script "createObject"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=id=None,type_name=None,script_id=None
##title=
##

from DateTime import DateTime
from Products.CMFPlone.utils import transaction_note
from Products.CMFPlone import PloneMessageFactory as _
REQUEST=context.REQUEST

if id is None:
    id=context.generateUniqueId(type_name)

if type_name is None:
    raise Exception, 'Type name not specified'

if context.portal_factory.getFactoryTypes().has_key(type_name):
    o = context.restrictedTraverse('portal_factory/' + type_name + '/' + id)
    message = None
    transaction_note('Initiated creation of %s with id %s in %s' % (o.getTypeInfo().getId(), id, context.absolute_url()))
else:
    new_id = context.invokeFactory(id=id, type_name=type_name)
    if new_id is None or new_id == '':
       new_id = id
    o=getattr(context, new_id, None)
    tname = o.getTypeInfo().Title()
    # AVS temporary solution - unicode translation not being done in unix
    # message = _(u'${tname} has been created.', mapping={u'tname' : tname})
    message = context.translate('object_created', default='${tname} has been created.', mapping={'tname' : tname})
    transaction_note('Created %s with id %s in %s' % (o.getTypeInfo().getId(), new_id, context.absolute_url()))

if o is None:
    raise Exception

if o.getTypeInfo().getActionById('edit', None) is None:
    state.setStatus('success_no_edit')

if script_id:
    state.setId(script_id)

if message:
    context.plone_utils.addPortalMessage(message)
return state.set(context=o)
