## Script (Python) "guard_handler"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=transition_id=None
##title=guard_handler Script
from bika.lims.workflow import guard_handler as wf_guard_handler
return wf_guard_handler(context, transition_id)
