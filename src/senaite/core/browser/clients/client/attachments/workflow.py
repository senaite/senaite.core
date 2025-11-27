# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims import logger
from bika.lims.browser.workflow import WorkflowActionGenericAdapter
from senaite.core.interfaces import IMultiUploadFileRemover
from zope.component import queryAdapter


class WorkflowActionDeleteAdapter(WorkflowActionGenericAdapter):
    """Adapter for deleting client attachments"""

    def __call__(self, action, objects):
        """Delete the selected attachments

        :param action: The workflow action ID
        :param objects: List of objects to delete
        """
        if not objects:
            return self.redirect(message="No files selected")

        # Get UIDs of objects to delete
        uids = [api.get_uid(obj) for obj in objects]

        # Use the remover adapter to delete the files
        # This will also cleanup references in the parent
        remover = queryAdapter(self.context, IMultiUploadFileRemover)
        if not remover:
            logger.error(
                "No IMultiUploadFileRemover adapter found for context"
            )
            return self.redirect(
                message="Delete operation not available",
                level="error"
            )

        try:
            # Remove the files
            remover.remove(uids)

            # update parent references -> now done in an event handler
            # XXX: How to better remove stale references of the parent object?
            # if hasattr(self.context, "getRawAttachments"):
            #     attachments = self.context.getRawAttachments()
            #     new_attachments = [uid for uid in attachments
            #                        if uid not in uids]
            #     self.context.setAttachments(new_attachments)

            message = "{} file(s) deleted successfully".format(len(uids))
            return self.redirect(message=message, level="info")

        except Exception as e:
            logger.error("Error deleting files: {}".format(str(e)))
            return self.redirect(
                message="Error deleting files: {}".format(str(e)),
                level="error"
            )
