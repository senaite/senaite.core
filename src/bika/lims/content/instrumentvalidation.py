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

from DateTime import DateTime
from AccessControl import ClassSecurityInfo

from Products.Archetypes.atapi import BaseFolder
from Products.Archetypes.atapi import DisplayList
from Products.Archetypes.atapi import registerType
from Products.CMFCore.utils import getToolByName

from zope.interface import implements


# Schema and Fields
from Products.Archetypes.atapi import Schema
from bika.lims.content.bikaschema import BikaSchema
from Products.Archetypes.atapi import ReferenceField
from Products.Archetypes.atapi import DateTimeField
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import TextField

# Widgets
from Products.Archetypes.atapi import StringWidget
from Products.Archetypes.atapi import TextAreaWidget
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.browser.widgets import ReferenceWidget

from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.interfaces import IInstrumentValidation


schema = BikaSchema.copy() + Schema((

    DateTimeField(
        'DateIssued',
        with_time=1,
        with_date=1,
        widget=DateTimeWidget(
            label=_("Report Date"),
            description=_("Validation report date"),
        ),
    ),

    DateTimeField(
        'DownFrom',
        with_time=1,
        with_date=1,
        widget=DateTimeWidget(
            label=_("From"),
            description=_("Date from which the instrument is under validation"),
        ),
    ),

    DateTimeField(
        'DownTo',
        with_time=1,
        with_date=1,
        widget=DateTimeWidget(
            label=_("To"),
            description=_("Date until the instrument will not be available"),
        ),
    ),

    StringField(
        'Validator',
        widget=StringWidget(
            label=_("Validator"),
            description=_("The analyst responsible of the validation"),
        )
    ),

    TextField(
        'Considerations',
        default_content_type='text/plain',
        allowed_content_types=('text/plain', ),
        default_output_type="text/plain",
        widget=TextAreaWidget(
            label=_("Considerations"),
            description=_("Remarks to take into account before validation"),
        ),
    ),

    TextField(
        'WorkPerformed',
        default_content_type='text/plain',
        allowed_content_types=('text/plain', ),
        default_output_type="text/plain",
        widget=TextAreaWidget(
            label=_("Work Performed"),
            description=_("Description of the actions made during the validation"),
        ),
    ),

    ReferenceField(
        'Worker',
        vocabulary='getLabContacts',
        allowed_types=('LabContact',),
        relationship='LabContactInstrumentValidation',
        widget=ReferenceWidget(
            checkbox_bound=0,
            label=_("Performed by"),
            description=_("The person at the supplier who performed the task"),
            size=30,
            base_query={'is_active': True},
            showOn=True,
            colModel=[
                {'columnName': 'UID', 'hidden': True},
                {'columnName': 'JobTitle', 'width': '20',
                 'label': _('Job Title')},
                {'columnName': 'Title', 'width': '80', 'label': _('Name')}
            ],
        ),
    ),

    StringField(
        'ReportID',
        widget=StringWidget(
            label=_("Report ID"),
            description=_("Report identification number"),
        )
    ),

    TextField(
        'Remarks',
        default_content_type='text/plain',
        allowed_content_types=('text/plain', ),
        default_output_type="text/plain",
        widget=TextAreaWidget(
            label=_("Remarks"),
        ),
    ),
))

schema['title'].widget.label = 'Task ID'


class InstrumentValidation(BaseFolder):
    """Instrument validation task
    """
    implements(IInstrumentValidation)
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getLabContacts(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        # fallback - all Lab Contacts
        pairs = []
        for contact in bsc(portal_type='LabContact',
                           is_active=True,
                           sort_on='sortable_title'):
            pairs.append((contact.UID, contact.Title))
        return DisplayList(pairs)

    def isValidationInProgress(self):
        """Checks if the date is beteween a validation period
        """
        today = DateTime()
        down_from = self.getDownFrom()
        down_to = self.getDownTo()

        return down_from <= today <= down_to

    def isFutureValidation(self):
        """
        Check is the current validation has been scheduled for a future time
        :return: Bool
        """
        today = DateTime()
        down_from = self.getDownFrom()
        return down_from >= today

    def getRemainingDaysInValidation(self):
        """Returns the days until the instrument returns from validation
        """
        delta = 0
        today = DateTime()
        down_from = self.getDownFrom() or today
        down_to = self.getDownTo()

        # one of the fields is not set, return 0 days
        if not down_from or not down_to:
            return 0
        # down_from comes after down_to?
        if down_from > down_to:
            return 0
        # calculate the time between today and down_to, even if down_from
        # is in the future.
        else:
            delta = down_to - today

        return int(math.ceil(delta))


registerType(InstrumentValidation, PROJECTNAME)
