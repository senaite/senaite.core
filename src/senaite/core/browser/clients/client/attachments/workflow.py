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

        # Get the parent container (Client)
        parent = api.get_parent(self.context)

        # Use the remover adapter to delete the files
        # This will also cleanup references in the parent
        remover = queryAdapter(parent, IMultiUploadFileRemover)
        if not remover:
            logger.error(
                "No IMultiUploadFileRemover adapter found for context"
            )
            return self.redirect(
                message="Delete operation not available",
                level="error"
            )

        try:
            # Remove the files - this also cleans up parent references
            remover.remove(uids)

            message = "{} file(s) deleted successfully".format(len(uids))
            return self.redirect(message=message, level="info")

        except Exception as e:
            logger.error("Error deleting files: {}".format(str(e)))
            return self.redirect(
                message="Error deleting files: {}".format(str(e)),
                level="error"
            )
