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

from bika.lims import senaiteMessageFactory as _
from plone.app.users.browser.account import AccountPanelSchemaAdapter
from plone.app.users.browser.personalpreferences import \
    PersonalPreferencesPanel as Base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form.form import BaseForm
from zope.interface import Interface
from zope.schema import Choice


class IPersonalPreferences(Interface):
    """Personal Preferences Schema

    NOTE: Fields need equivalents in user properties!
    """

    timezone = Choice(
        title=_(u"label_timezone", default=u"Time zone"),
        description=_(u"help_timezone", default=u"Your time zone"),
        vocabulary="plone.app.vocabularies.AvailableTimezones",
        # vocabulary='plone.app.vocabularies.Timezones',
        required=False,
    )


class PersonalPreferencesPanelAdapter(AccountPanelSchemaAdapter):
    """Data manager that gets and sets any property mentioned
       in the schema to the property sheet
    """
    schema = IPersonalPreferences


class PersonalPreferencesPanel(Base):
    template = ViewPageTemplateFile("templates/account-panel.pt")
    schema = IPersonalPreferences

    def updateWidgets(self):
        # bypass the method of the base class, because it modifies schema
        # widgets that we removed
        BaseForm.updateWidgets(self)
