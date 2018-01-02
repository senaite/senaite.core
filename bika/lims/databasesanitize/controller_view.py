# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import json
import traceback

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.taskqueue.interfaces import ITaskQueue
from plone.protect import CheckAuthenticator
from plone.protect import PostOnly
from zope.component import queryUtility

from bika.lims import logger
from bika.lims.browser import BrowserView
from bika.lims.databasesanitize.analyses import analyses_creation_date_recover


class ControllerView(BrowserView):
    """
    This class is the controller for the sanitize view. Sanitize view
    """
    template = ViewPageTemplateFile("templates/main_template.pt")

    def __call__(self):
        if not self.request.form.get('submit', None):
            # The form hasn't been submitted, no tasks required
            return self.template()
        # Need to sanitize creation date from analyses
        if self.request.form.get('sanitize_analyses_creation_date', '0')\
                == '1':
            # Fix the creation date of analyses
            self.sanitize_analyses_creation_date()
        return self.template()

    def sanitize_analyses_creation_date(self):
            logger.info("Starting sanitation process 'Analyses creation "
                        "date recover'...")
            # Only load asynchronously if queue sanitation-tasks is available
            task_queue = queryUtility(ITaskQueue, name='sanitation-tasks')
            if task_queue is None:
                # sanitation-tasks queue not registered. Proceed synchronously
                logger.info("SYNC sanitation process started...")
                task_manager = AnalysesCreationDateRecover()
                task_manager()
            else:
                # sanitation-tasks queue registered, create asynchronously
                logger.info("[A]SYNC sanitation process started...")
                path = self.request.PATH_INFO
                path = path.replace(
                    'sanitize_action', 'analyses_creation_date_recover')
                task_queue.add(path, method='POST')
                msg = 'One job added to the sanitation process queue'
                self.context.plone_utils.addPortalMessage(msg, 'info')


class AnalysesCreationDateRecover():
    """
    This class manages the creation of async tasks.
    """

    def __call__(self):
        analyses_creation_date_recover()
        return json.dumps({'success': 'With taskqueue'})


class QueuedSanitationTasksCount(BrowserView):

    def __call__(self):
        """
        Returns the number of tasks in the sanitation-tasks queue
        """
        try:
            PostOnly(self.context.REQUEST)
        except:
            logger.error(traceback.format_exc())
            return json.dumps({'count': 0})
        try:
            CheckAuthenticator(self.request.form)
        except:
            logger.error(traceback.format_exc())
            return json.dumps({'count': 0})
        task_queue = queryUtility(ITaskQueue, name='sanitation-tasks')
        count = len(task_queue) if task_queue is not None else 0
        return json.dumps({'count': count})
