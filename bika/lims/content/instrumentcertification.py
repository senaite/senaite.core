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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

import math

from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes.atapi import BaseFolder
from Products.Archetypes.atapi import BooleanField
from Products.Archetypes.atapi import BooleanWidget
from Products.Archetypes.atapi import ComputedField
# Widgets
from Products.Archetypes.atapi import ComputedWidget
from Products.Archetypes.atapi import DateTimeField
from Products.Archetypes.atapi import DisplayList
from Products.Archetypes.atapi import FileWidget
from Products.Archetypes.atapi import ReferenceField
# Schema and Fields
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import StringWidget
from Products.Archetypes.atapi import TextAreaWidget
from Products.Archetypes.atapi import TextField
from Products.Archetypes.atapi import registerType
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
# bika.lims imports
from bika.lims.browser.fields.remarksfield import RemarksField
from bika.lims.browser.widgets import ComboBoxWidget
from bika.lims.browser.widgets import RemarksWidget
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.browser.widgets import ReferenceWidget
from bika.lims import logger
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IInstrumentCertification
from plone.app.blob.field import FileField as BlobFileField
from zope.interface import implements

schema = BikaSchema.copy() + Schema((

    StringField(
        'TaskID',
        widget=StringWidget(
            label=_("Task ID"),
            description=_("The instrument's ID in the lab's asset register"),
        )
    ),

    ReferenceField(
        'Instrument',
        allowed_types=('Instrument',),
        relationship='InstrumentCertificationInstrument',
        widget=StringWidget(
            visible=False,
        )
    ),

    ComputedField(
        'InstrumentUID',
        expression='context.getInstrument() and context.getInstrument().UID() or None',
        widget=ComputedWidget(
            visible=False,
        ),
    ),

    # Set the Certificate as Internal
    # When selected, the 'Agency' field is hidden
    BooleanField(
        'Internal',
        default=False,
        widget=BooleanWidget(
            label=_("Internal Certificate"),
            description=_("Select if is an in-house calibration certificate")
        )
    ),

    StringField(
        'Agency',
        widget=StringWidget(
            label=_("Agency"),
            description=_("Organization responsible of granting the calibration certificate")
        ),
    ),

    DateTimeField(
        'Date',
        widget=DateTimeWidget(
            label=_("Date"),
            description=_("Date when the calibration certificate was granted"),
        ),
    ),

    StringField(
        'ExpirationInterval',
        vocabulary="getInterval",
        widget=ComboBoxWidget(
            label=_("Interval"),
            description=_("The interval is calculated from the 'From' field "
                          "and defines when the certificate expires in days. "
                          "Setting this inverval overwrites the 'To' field "
                          "on save."),
            default="",
            # configures the HTML input attributes for the additional field
            field_config={"type": "number", "step": "1", "max": "99999"},
            field_regex="\d+"
        )
    ),

    DateTimeField(
        'ValidFrom',
        with_time=1,
        with_date=1,
        required=1,
        widget=DateTimeWidget(
            label=_("From"),
            description=_("Date from which the calibration certificate is valid"),
        ),
    ),

    DateTimeField(
        'ValidTo',
        with_time=1,
        with_date=1,
        required=1,
        widget=DateTimeWidget(
            label=_("To"),
            description=_("Date until the certificate is valid"),
        ),
    ),

    ReferenceField(
        'Preparator',
        vocabulary='getLabContacts',
        allowed_types=('LabContact',),
        relationship='LabContactInstrumentCertificatePreparator',
        widget=ReferenceWidget(
            checkbox_bound=0,
            label=_("Prepared by"),
            description=_("The person at the supplier who prepared the certificate"),
            size=30,
            base_query={'is_active': True},
            showOn=True,
            colModel=[
                {'columnName': 'UID', 'hidden': True},
                {'columnName': 'JobTitle', 'width': '20', 'label': _('Job Title')},
                {'columnName': 'Title', 'width': '80', 'label': _('Name')}
            ],
        ),
    ),

    ReferenceField(
        'Validator',
        vocabulary='getLabContacts',
        allowed_types=('LabContact',),
        relationship='LabContactInstrumentCertificateValidator',
        widget=ReferenceWidget(
            checkbox_bound=0,
            label=_("Approved by"),
            description=_("The person at the supplier who approved the certificate"),
            size=30,
            base_query={'is_active': True},
            showOn=True,
            colModel=[
                {'columnName': 'UID', 'hidden': True},
                {'columnName': 'JobTitle', 'width': '20', 'label': _('Job Title')},
                {'columnName': 'Title', 'width': '80', 'label': _('Name')}
            ],
        ),
    ),

    BlobFileField(
        'Document',
        widget=FileWidget(
            label=_("Report upload"),
            description=_("Load the certificate document here"),
        )
    ),

    TextField(
        "Remarks",
        allowable_content_types=("text/plain",),
        widget=TextAreaWidget(
            label=_("Remarks"),
        )
    ),

))

schema['title'].widget.label = _("Certificate Code")


class InstrumentCertification(BaseFolder):
    """Issued certification from an instrument calibration
    """
    implements(IInstrumentCertification)
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    security.declareProtected("Modify portal content", "setValidTo")
    def setValidTo(self, value):
        """Custom setter method to calculate a `ValidTo` date based on
        the `ValidFrom` and `ExpirationInterval` field values.
        """

        valid_from = self.getValidFrom()
        valid_to = DateTime(value)
        interval = self.getExpirationInterval()

        if valid_from and interval:
            valid_to = valid_from + int(interval)
            self.getField("ValidTo").set(self, valid_to)
            logger.debug("Set ValidTo Date to: %r" % valid_to)
        else:
            # just set the value
            self.getField("ValidTo").set(self, valid_to)

    def getLabContacts(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        # fallback - all Lab Contacts
        pairs = []
        for contact in bsc(portal_type='LabContact',
                           is_active=True,
                           sort_on='sortable_title'):
            pairs.append((contact.UID, contact.Title))
        return DisplayList(pairs)

    def getInterval(self):
        """Vocabulary of date intervals to calculate the "To" field date based
        from the "From" field date.
        """
        items = (
            ("", _(u"Not set")),
            ("1", _(u"daily")),
            ("7", _(u"weekly")),
            ("30", _(u"monthly")),
            ("90", _(u"quarterly")),
            ("180", _(u"biannually")),
            ("365", _(u"yearly")),
        )
        return DisplayList(items)

    def isValid(self):
        """Returns if the current certificate is in a valid date range
        """

        today = DateTime()
        valid_from = self.getValidFrom()
        valid_to = self.getValidTo()

        return valid_from <= today <= valid_to

    def getDaysToExpire(self):
        """Returns the days until this certificate expires

        :returns: Days until the certificate expires
        :rtype: int
        """

        delta = 0
        today = DateTime()
        valid_from = self.getValidFrom() or today
        valid_to = self.getValidTo()

        # one of the fields is not set, return 0 days
        if not valid_from or not valid_to:
            return 0
        # valid_from comes after valid_to?
        if valid_from > valid_to:
            return 0
        # calculate the time between today and valid_to, even if valid_from
        # is in the future.
        else:
            delta = valid_to - today

        return int(math.ceil(delta))

    def getWeeksAndDaysToExpire(self):
        """Returns the number weeks and days until this certificate expires

        :returns: Weeks and days until the certificate expires
        :rtype: tuple(weeks, days)
        """

        days = self.getDaysToExpire()
        return divmod(days, 7)


registerType(InstrumentCertification, PROJECTNAME)
