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
from bika.lims.databasesanitize.ar_deps import set_ar_departments


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
        tasks = []
        if self.request.form.get('sanitize_analyses_creation_date', '0')\
                == '1':
            # Fix the creation date of analyses
            task = {"class": AnalysesCreationDateRecover(),
                    "uri": "analyses_creation_date_recover"
                    }
            tasks.append(task)

        if self.request.form.get('sanitize_ar_departments', '0')\
                == '1':
            # Fix AR Departments
            task = {"class": ARDepartmentAssignment(),
                    "uri": "st_ar_dep_assignment"
                    }
            tasks.append(task)

        for t in tasks:
            self.sanitize(t["class"], t["uri"])

        return self.template()

    def sanitize(self, klass, uri):
            logger.info("Starting sanitation process {0} ".format(uri))
            # Only load asynchronously if queue sanitation-tasks is available
            task_queue = queryUtility(ITaskQueue, name='sanitation-tasks')
            if task_queue is None:
                # sanitation-tasks queue not registered. Proceed synchronously
                logger.info("SYNC sanitation process started...")
                klass()
            else:
                # sanitation-tasks queue registered, create asynchronously
                logger.info("[A]SYNC sanitation process started...")
                path = self.request.PATH_INFO
                path = path.replace(
                    'sanitize_action', uri)
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


class ARDepartmentAssignment():
    """
    This class manages the creation of async tasks.
    """

    def __call__(self):
        set_ar_departments()
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
