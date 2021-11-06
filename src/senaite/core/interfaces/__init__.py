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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

from plone.app.z3cform.interfaces import IPloneFormLayer
from senaite.core.interfaces.datamanager import IDataManager  # noqa (convenience import)
from zope.interface import Interface
from senaite.core.interfaces.catalog import *  # noqa


class ISenaiteCore(Interface):
    """Marker interface that defines a Zope 3 browser layer.
    """


class ISenaiteFormLayer(IPloneFormLayer):
    """Used to override plone.app.z3cform forms

    Inherits from `z3c.form.interfaces.IFormLayer`
    """


class IShowDisplayMenu(Interface):
    """Marker interface that can be applied for contents that should display
    the "Display" menu
    """


class IShowFactoriesMenu(Interface):
    """Marker interface that can be applied for contents that should display
    the "Add" menu
    """


class IHideActionsMenu(Interface):
    """Marker interface that can be applied for contents that should not
    display the content actions menu
    """


class IAjaxEditForm(Interface):
    """Ajax edit form adapter
    """

    def initialized(data):
        """Called once after the edit form was rendered

        :param data: JSON payload of the edit form.
                     Contains at least `form`, `name`, `value`
        :returns: A dictionary with update instructions for the frontend logic
        """

    def modified(data):
        """Called for each field modification

        :param data: JSON payload of the edit form.
                     Contains at least `form`, `name`, `value`
        :returns: A dictionary with update instructions for the frontend logic
        """


class ISamples(Interface):
    """Marker interface for samples main folder
    """


class ISamplesView(Interface):
    """Marker interface for samples listing view
    """


class IHaveUIDReferences(Interface):
    """Marker interface when the object contains UID references
    """
