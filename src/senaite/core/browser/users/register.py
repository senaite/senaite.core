# -*- coding: utf-8 -*-

from plone.app.users.browser.register import AddUserForm as BaseAddUserForm
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class AddUserForm(BaseAddUserForm):
    template = ViewPageTemplateFile("templates/newuser_form.pt")

    def updateFields(self):
        super(AddUserForm, self).updateFields()

        # remove groups field from registration
        if "groups" in self.fields:
            del self.fields["groups"]

    def updateWidgets(self):
        super(AddUserForm, self).updateWidgets()

    def updateActions(self):
        super(AddUserForm, self).updateActions()
        self.actions["register"].klass = "btn btn-sm btn-success"
