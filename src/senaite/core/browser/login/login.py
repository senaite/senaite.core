# -*- coding: utf-8 -*-

from Products.CMFPlone.browser.login.login import LoginForm as BaseLoginForm


class LoginForm(BaseLoginForm):

    def get_icon_class_for(self, widget):
        if widget.name == "__ac_name":
            return "glyphicon glyphicon-user"
        if widget.name == "__ac_password":
            return "glyphicon glyphicon-lock"

    def updateWidgets(self):
        super(LoginForm, self).updateWidgets()
        self.widgets["__ac_name"].addClass("form-control")
        self.widgets["__ac_password"].addClass("form-control")

    def updateActions(self):
        super(LoginForm, self).updateActions()
        self.actions["login"].addClass("btn btn-primary")
