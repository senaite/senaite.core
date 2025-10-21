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

import re
from collections import OrderedDict

import transaction
from bika.lims import PMF
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.api import security
from bika.lims.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.content.labcontact import LabContact
from senaite.core.interfaces import IContacts
from bika.lims.utils import get_email_link
from bika.lims.utils import get_link
from bika.lims.vocabularies import CatalogVocabulary
from plone.memoize import view
from plone.protect import CheckAuthenticator
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.controlpanel.browser.usergroups_usersoverview import \
    UsersOverviewControlPanel
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.catalog import CLIENT_CATALOG
from senaite.core.catalog import CONTACT_CATALOG
from senaite.core.config.groups import HIDDEN_GROUPS
from senaite.core.p3compat import cmp
from zope.interface import implements


class ClientContactsView(BikaListingView):
    """Client Contacts listing view
    """
    implements(IContacts)

    def __init__(self, context, request):
        super(ClientContactsView, self).__init__(context, request)
        self.catalog = CONTACT_CATALOG
        self.contentFilter = {
            "portal_type": "Contact",
            "sort_on": "sortable_title",
            "path": {
                "query": "/".join(context.getPhysicalPath()),
                "level": 0
            }
        }
        self.context_actions = {
            _("Add"):
                {"url": "++add++Contact",
                 "permission": "Add portal content",
                 "icon": "++resource++bika.lims.images/add.png"}}

        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50
        self.form_id = "contacts"

        self.icon = self.portal_url + \
                    "/++resource++bika.lims.images/client_contact_big.png"
        self.title = self.context.translate(_("Contacts"))
        self.description = ""

        self.columns = OrderedDict((
            ("getFullname", {
                "title": _("Full Name"),
                "index": "getFullname",
                "sortable": True, }),
            ("Username", {
                "title": _("User Name"), }),
            ("getEmailAddress", {
                "title": _("Email Address"), }),
            ("getBusinessPhone", {
                "title": _("Business Phone"), }),
            ("getMobilePhone", {
                "title": _("MobilePhone"), }),
        ))

        self.review_states = [
            {"id": "default",
             "title": _("Active"),
             "contentFilter": {"is_active": True},
             "transitions": [{"id": "deactivate"}, ],
             "columns": self.columns.keys()},
            {"id": "inactive",
             "title": _("Inactive"),
             "contentFilter": {"is_active": False},
             "transitions": [{"id": "activate"}, ],
             "columns": self.columns.keys()},
            {"id": "all",
             "title": _("All"),
             "contentFilter": {},
             "columns": self.columns.keys()},
        ]

    def folderitem(self, obj, item, index):
        obj = api.get_object(obj)
        url = item.get("url")
        email = obj.getEmailAddress()
        fullname = obj.getFullname()
        item["getFullname"] = fullname
        item["getEmailAddress"] = email
        item["getBusinessPhone"] = obj.getBusinessPhone()
        item["getMobilePhone"] = obj.getMobilePhone()
        item["Username"] = obj.getUsername() or ""
        item["replace"]["getFullname"] = get_link(url, fullname)
        if email:
            item["replace"]["getEmailAddress"] = get_email_link(email)
        return item


class ClientContactVocabularyFactory(CatalogVocabulary):
    """Vocabulary factory for client contacts
    """
    def __call__(self):
        return super(ClientContactVocabularyFactory, self).__call__(
            portal_type="Contact",
            path={"query": "/".join(self.context.getPhysicalPath()),
                  "level": 0}
        )


class ContactLoginDetailsView(BrowserView):
    """Contact Login View
    """
    template = ViewPageTemplateFile("templates/login_details.pt")

    def __call__(self):
        request = self.request
        form = request.form
        CheckAuthenticator(form)

        self.newSearch = False
        self.searchstring = form.get("searchstring", "")

        if form.get("submitted"):
            logger.debug("Form Submitted: {}".format(form))
            if form.get("unlink_button", False):
                self._unlink_user()
            elif form.get("search_button", False):
                logger.debug("Search User")
                self.newSearch = True
            elif form.get("link_button", False):
                logger.debug("Link User")
                self._link_user(form.get("userid"))
            elif form.get("save_button", False):
                logger.debug("Create User")
                self._create_user()

        return self.template()

    @view.memoize
    def get_users(self):
        """Get all users of the portal
        """
        # We make use of the existing controlpanel `@@usergroup-userprefs`
        # view logic to make sure we get all users from all plugins (e.g. LDAP)
        users_view = UsersOverviewControlPanel(self.context, self.request)
        return users_view.doSearch("")

    @view.memoize
    def get_clients_groups(self):
        """Returns the client-specific groups
        """
        groups = []
        cat = api.get_tool(CLIENT_CATALOG)
        for brain in cat(portal_type="Client"):
            if brain.getGroupId:
                groups.append(brain.getGroupId)
        return groups

    def get_laboratory_groups(self):
        """Return the groups available for laboratory users
        """
        gtool = api.get_tool("portal_groups")
        groups = gtool.listGroupIds()

        # exclude hidden (Administrators, etc.) and client-specific groups
        to_skip = HIDDEN_GROUPS + self.get_clients_groups()
        groups = filter(lambda group: group not in to_skip, groups)

        # sort them
        return sorted(groups)

    def get_user_properties(self):
        """Return the properties of the User
        """

        user = self.context.getUser()

        # No User linked, nothing to do
        if user is None:
            return {}

        out = {}
        plone_user = user.getUser()
        userid = plone_user.getId()
        for sheet in plone_user.listPropertysheets():
            ps = plone_user.getPropertysheet(sheet)
            out.update(dict(ps.propertyItems()))

        portal = api.get_portal()
        mtool = getToolByName(self.context, "portal_membership")

        out["id"] = userid
        out["portrait"] = mtool.getPersonalPortrait(id=userid)
        out["edit_url"] = "{}/@@user-information?userid={}".format(
            portal.absolute_url(), userid)

        return out

    def get_contact_properties(self):
        """Return the properties of the Contact
        """
        contact = self.context

        return {
            "fullname": contact.getFullname(),
            "username": contact.getUsername(),
        }

    def linkable_users(self):
        """Search Plone users which are not linked to a contact or lab contact
        """

        # Only users with at most these roles are displayed
        linkable_roles = {"Authenticated", "Member", "Client"}

        out = []
        for user in self.get_users():
            userid = user.get("id", None)

            if userid is None:
                continue

            # Skip users which are already linked to a Contact
            # Use classmethod to find contacts by username
            from senaite.core.content.contact import Contact
            contact = Contact.getContactByUsername(userid)
            labcontact = LabContact.getContactByUsername(userid)

            if contact or labcontact:
                continue
            if self.is_contact():
                # Checking Plone user belongs to Client group only. Otherwise,
                # weird things could happen (a client contact assigned to a
                # user with labman privileges, different contacts from
                # different clients assigned to the same user, etc.)
                user_roles = security.get_roles(user=userid)
                if not linkable_roles.issuperset(set(user_roles)):
                    continue
            userdata = {
                "userid": userid,
                "email": user.get("email"),
                "fullname": user.get("title"),
            }

            # filter out users which do not match the searchstring
            if self.searchstring:
                s = self.searchstring.lower()
                if not any(
                        map(lambda v: re.search(s, str(v).lower()),
                            userdata.values())):
                    continue

            # update data (maybe for later use)
            userdata.update(user)

            # Append the userdata for the results
            out.append(userdata)

        out.sort(lambda x, y: cmp(x["fullname"], y["fullname"]))
        return out

    def is_contact(self):
        """Check if the current context is a Contact
        """
        if self.context.portal_type == "Contact":
            return True
        return False

    def is_labcontact(self):
        """Check if the current context is a LabContact
        """
        if self.context.portal_type == "LabContact":
            return True
        return False

    def _link_user(self, userid):
        """Link an existing user to the current Contact
        """
        # check if we have a selected user from the search-list
        if userid:
            try:
                self.context.setUser(userid)
                self.add_status_message(
                    _("User linked to this Contact"), "info")
            except ValueError as e:
                self.add_status_message(e, "error")
        else:
            self.add_status_message(
                _("Please select a User from the list"), "info")

    def _unlink_user(self):
        """Unlink and delete the User from the current Contact
        """
        self.context.unlinkUser()
        self.add_status_message(_("Unlinked User"), "info")

    def add_status_message(self, message, severity="info"):
        """Set a portal message
        """
        self.context.plone_utils.addPortalMessage(message, severity)

    def _create_user(self):
        """Create a new user
        """

        def error(field, message):
            if field:
                message = "%s: %s" % (field, message)
            self.context.plone_utils.addPortalMessage(message, "error")
            return self.request.response.redirect(
                self.context.absolute_url() + "/login_details")

        form = self.request.form
        contact = self.context

        password = safe_unicode(form.get("password", "")).encode("utf-8")
        username = safe_unicode(form.get("username", "")).encode("utf-8")
        confirm = form.get("confirm", "")
        email = safe_unicode(form.get("email", "")).encode("utf-8")

        if not username:
            return error("username", PMF("Input is required but not given."))

        if not email:
            return error("email", PMF("Input is required but not given."))

        reg_tool = self.context.portal_registration
        # properties = self.context.portal_properties.site_properties
        # if properties.validate_email:
        #     password = reg_tool.generatePassword()
        # else:
        if password != confirm:
            return error("password", PMF("Passwords do not match."))

        if not password:
            return error("password", PMF("Input is required but not given."))

        if not confirm:
            return error("password", PMF("Passwords do not match."))

        if len(password) < 5:
            return error("password", PMF("Passwords must contain at least 5 "
                                         "characters."))
        for user in self.get_users():
            userid = user.get("id", None)
            if userid is None:
                continue
            user_obj = api.get_user(userid)
            if user_obj.getUserName() == username:
                msg = "Username {} already exists, please, choose " \
                      "another one.".format(username)
                return error(None, msg)

        try:
            reg_tool.addMember(username,
                               password,
                               properties={
                                   "username": username,
                                   "email": email,
                                   "fullname": username})
        except ValueError as msg:
            return error(None, msg)

        # set the user to the contact
        contact.setUser(username)

        # Additional groups for LabContact users only!
        # -> This is not visible in the Client Contact Form
        if "groups" in self.request and self.request["groups"]:
            groups = self.request["groups"]
            if not type(groups) in (list, tuple):
                groups = [groups, ]
            for group in groups:
                group = self.portal_groups.getGroupById(group)
                group.addMember(username)

        if self.request.get("mail_me", 0):
            try:
                reg_tool.registeredNotify(username)
            except Exception:
                transaction.abort()
                message = _("SMTP server disconnected. User creation aborted.")
                return error(None, message)

        message = _("Member registered and linked to the current Contact.")
        self.context.plone_utils.addPortalMessage(message, "info")
        return self.request.response.redirect(
            self.context.absolute_url() + "/login_details")

    def tabindex(self):
        i = 0
        while True:
            i += 1
            yield i
