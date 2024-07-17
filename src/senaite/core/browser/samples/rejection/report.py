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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.api import dtime
from senaite.impress.interfaces import IPublisher
from zope.component import getUtility

DIN_A4_PORTRAIT = """
/** DIN A4 portrait **/
@page {
  size: 210.0mm 297.0mm;
  margin: 20.0mm;
}
@media print {
  .report {
    width: 170.0mm;
    height: 257.0mm;
  }
}
@media screen {
  .report {
    width: 210.0mm;
    height: 297.0mm;
    padding: 20.0mm !important;
  }
}
"""


class RejectionReport(BrowserView):
    """
    View that renders the template to be used for the generation of the pdf
    representing the rejection report
    """
    template = ViewPageTemplateFile("templates/rejection_report.pt")

    def __call__(self):
        if not self.request.get("pdf"):
            return self.template()

        pdf = self.to_pdf()
        filename = "%s-rejected" % api.get_id(self.context)
        self.request.response.setHeader(
            "Content-Disposition", "attachment; filename=%s.pdf" % filename)
        self.request.response.setHeader("Content-Type", "application/pdf")
        self.request.response.setHeader("Content-Length", len(pdf))
        self.request.response.setHeader("Cache-Control", "no-store")
        self.request.response.setHeader("Pragma", "no-cache")
        self.request.response.write(pdf)

    def to_pdf(self):
        """Returns a pdf of this report
        """
        # generate the html from the template
        html = self.template()
        # convert to unicode
        html = api.safe_unicode(html)
        # get the impress publisher with default css
        publisher = getUtility(IPublisher)
        publisher.add_inline_css(self.layout_css)
        # generate the pdf
        return publisher.write_pdf(html)

    @property
    def layout_css(self):
        """Returns the CSS for the page and content layout
        """
        return DIN_A4_PORTRAIT

    def long_date(self, date):
        """Returns the date localized in long format
        """
        return dtime.to_localized_time(date, long_format=True)

    def get_contact_properties(self, contact):
        """Returns a dictionary with information about the contact
        """
        if not contact:
            return {}

        # fill properties with contact additional info
        contact_url = api.get_url(contact)
        signature = contact.getSignature()
        signature = "{}/Signature".format(contact_url) if signature else ""
        department = contact.getDefaultDepartment()
        department = api.get_title(department) if department else ""

        return {
            "fullname": api.to_utf8(contact.getFullname()),
            "salutation": api.to_utf8(contact.getSalutation()),
            "signature": signature,
            "job_title": api.to_utf8(contact.getJobTitle()),
            "phone": contact.getBusinessPhone(),
            "department": api.to_utf8(department),
            "email": contact.getEmailAddress(),
            "uid": api.get_uid(contact),
        }

    def get_rejected_by(self):
        """Returns a dict with information about the rejecter, giving priority
        to the contact over the user
        """
        user = api.get_current_user()
        properties = api.get_user_properties(user)

        # overwrite with contact info
        contact = api.get_user_contact(user)
        contact_properties = self.get_contact_properties(contact)
        properties.update(contact_properties)

        return properties

    def get_authorized_by(self):
        """Returns a list of dicts with the information about the laboratory
        contacts that are in charge of this samples as responsibles of the
        departments from its tests
        """
        rejecter = self.get_rejected_by()
        rejecter_uid = rejecter.get("uid")
        authorized_by = {}
        for department in self.context.getDepartments():
            manager = department.getManager()
            properties = self.get_contact_properties(manager)
            if not properties:
                continue

            # skip rejecter
            contact_uid = api.get_uid(manager)
            if rejecter_uid == contact_uid:
                continue

            # skip duplicates
            authorized_by[contact_uid] = properties

        return authorized_by.values()

    def get_rejection_reasons(self, keyword=None):
        """
        Returns a list with the rejection reasons as strings

        :param keyword: set of rejection reasons to be retrieved.
        Possible values are:
            - 'selected': Get, amongst the set of predefined reasons, the ones selected
            - 'other': Get the user free-typed reason for rejection
            - None: Get all rejection reasons
        :return: list of rejection reasons as strings or an empty list
        """
        keys = ["selected", "other"]
        if keyword is None:
            return sum(map(self.get_rejection_reasons, keys), [])
        if keyword not in keys:
            return []
        rejection_reasons = self.context.getRejectionReasons()
        rejection_reasons = rejection_reasons and rejection_reasons[0] or {}
        if keyword == 'other':
            return rejection_reasons.get(keyword, '') and [rejection_reasons.get(keyword, '')] or []
        return rejection_reasons.get(keyword, [])
