# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from senaite.core.browser.views import PublishTraverseView
from zExceptions import Unauthorized


class ATDownloadView(PublishTraverseView):
    """Download an Archetypes field, keeping the original uploaded filename

    Replaces the `at_download` skin script from `Products.Archetypes`. That
    script is acquired, so it can be traversed to on any object in the site,
    including Dexterity content and folders that never carried Archetypes
    fields. There it calls `getPrimaryField` resp. `getWrappedField`
    unguarded and raises an `AttributeError`, which surfaces as a 500 and,
    for users holding `Manage portal`, as a rendered traceback.

    A view wins over an acquired attribute during traversal (see
    `ZPublisher.BaseRequest.DefaultPublishTraverse`), so registering this
    view shadows the skin script without having to override it.

    `<context>/at_download` downloads the primary field,
    `<context>/at_download/<fieldname>` the named one. Anything that does
    not resolve to a downloadable field is a 404.
    """

    def get_field(self):
        """Return the requested field, or None when the context carries no
        Archetypes schema or the field does not exist
        """
        if self.traverse_subpath:
            accessor = getattr(self.context, "getWrappedField", None)
            return accessor(self.traverse_subpath[0]) if accessor else None
        accessor = getattr(self.context, "getPrimaryField", None)
        return accessor() if accessor else None

    def __call__(self):
        """Download the field, instead of dispatching to an `ajax_` method
        """
        field = self.get_field()
        if field is None:
            return self.handle_not_found()

        if not field.checkPermission("r", self.context):
            raise Unauthorized("Field %s requires %s permission" % (
                field, field.read_permission))

        download = getattr(field, "download", None)
        if download is None:
            return self.handle_not_found()

        return download(self.context)
