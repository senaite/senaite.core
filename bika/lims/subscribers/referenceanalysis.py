from AccessControl import getSecurityManager
from Acquisition import aq_inner
from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
import transaction

def ObjectInitializedEventHandler(analysis, event):

    # set the MaxHoursAllowed
    service = analysis.getService()
    maxtime = service.getMaxTimeAllowed()
    if not maxtime:
        maxtime = {'days':0, 'hours':0, 'minutes':0}
    analysis.setMaxTimeAllowed(maxtime)

    # set Due Date
    starttime = analysis.getDateReceived()
    max_days = float(maxtime.get('days', 0)) + \
             (
                 (float(maxtime.get('hours', 0)) * 3600 + \
                  float(maxtime.get('minutes', 0)) * 60)
                 / 86400
             )
    duetime = starttime + max_days
    analysis.setDueDate(duetime)
    analysis.reindexObject()

def ActionSucceededEventHandler(analysis, event):

    if event.action == "verify":
        analysis.setDateVerified(DateTime())
