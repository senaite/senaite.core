## Script (Python) "guard_preserved_transition"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=type_name=None
##title=
##

workflow = context.portal_workflow

membership_tool = context.portal_membership
member = membership_tool.getAuthenticatedMember()

if context.portal_type == "AnalysisRequest":
    if workflow.getInfoFor(context.getSample(), 'review_state', '') not in ("to_be_sampled", "sampled"):
        return True

if context.portal_type == "Analysis":
    if workflow.getInfoFor(context.aq_parent, 'review_state', '') not in ("to_be_sampled", "sampled"):
        return True

if not member.has_role(('Preserver','Manager','LabManager',)): return False

if context.portal_type == 'Sample':
    review_state = workflow.getInfoFor(context, 'review_state', '')
    parts = context.values()
    preservable_parts = [p for p in parts if p.getPreservation()]
    preserved_parts = [p for p in parts if p.getDatePreserved()]
    preservers = [p for p in parts if p.getPreservedByUser()]
    if (len(preservable_parts) == len(preserved_parts)) and \
       (len(preservable_parts) == len(preservers)) and \
       review_state == "sampled":
           return True

return False


