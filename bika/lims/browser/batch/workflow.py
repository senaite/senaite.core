# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims.workflow import doActionFor

class BatchWorkflowAction(WorkflowAction):
    """This function is called to do the worflow actions on objects
    acted on in bika-listing views in batch context
    """
    pass
