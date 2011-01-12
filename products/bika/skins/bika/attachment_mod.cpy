## Controller Python Script "attachment_mod"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Modify attachment
##
from DateTime import DateTime
req = context.REQUEST.form

came_from = req['came_from']

rc = context.reference_catalog
if came_from == 'edit':
    # check out just using context, not getting object AVS AVS 
    uid = req['AttachmentUID']
    attachment = rc.lookupObject(uid)
    attachment.edit(
        AttachmentType=context.REQUEST.AttachmentType,
        AttachmentKeys=context.REQUEST.AttachmentKeys,
        )

if context.REQUEST.Attachment_action == 'replace':
    attachment.setAttachmentFile(context.REQUEST.AttachmentFile_file)


attachment.reindexObject()


from Products.CMFPlone import transaction_note
transaction_note('Attachment modified successfully')
message=context.translate('message_attachment_edited', default='Attachment ${attachment_id} was successfully modified', mapping={'attachment_id': attachment.getTextTitle()}, domain='bika')

return state.set(portal_status_message=message)

