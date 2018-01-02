# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from .ajax import ajaxGetSampleTypeInfo
from .analyses import SampleAnalysesView
from .partitions import SamplePartitionsView
from .edit import SampleEdit
from .partitions import createSamplePartition
from .printform import SamplesPrint
from .view import SampleView
from .view import SamplesView

import json
import plone
from bika.lims.workflow import doActionFor


class doActionForSample(object):
    """It should be called using the following format: .../doActionForSample?workflow_action=reject
        The function will change the object state to the asked one
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        action = self.request.get('workflow_action', '')
        if action == 'reject' and not self.context.bika_setup.isRejectionWorkflowEnabled():
            return json.dumps({"error": "true"})
        if action:
            doActionFor(self.context, action)
            return json.dumps({"success": "true"})
        else:
            return json.dumps({"error": "true"})
