# -*- coding: utf-8 -*-

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
