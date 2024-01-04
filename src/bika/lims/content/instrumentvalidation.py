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

import math

from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IInstrumentValidation
from DateTime import DateTime
from Products.Archetypes.atapi import BaseFolder
from Products.Archetypes.atapi import DateTimeField
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import StringWidget
from Products.Archetypes.atapi import TextAreaWidget
from Products.Archetypes.atapi import TextField
from Products.Archetypes.atapi import registerType
from senaite.core.browser.widgets.referencewidget import ReferenceWidget
from senaite.core.catalog import CONTACT_CATALOG
from zope.interface import implements

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

    UIDReferenceField(
        "Worker",
        allowed_types=("LabContact", "SupplierContact"),
        widget=ReferenceWidget(
            label=_(
                "label_instrumentvalidation_worker",
                default="Performed by"),
            description=_(
                "description_instrumentvalidation_worker",
                default="The person who performed the task"),
            catalog=CONTACT_CATALOG,
            query={
                "is_active": True,
                "sort_on": "sortable_title",
                "sort_order": "ascending"
            },
            columns=[
                {"name": "getFullname", "label": _("Name")},
                {"name": "getEmailAddress", "label": _("Email")},
                {"name": "getJobTitle", "label": _("Job Title")},
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
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from senaite.core.idserver import renameAfterCreation
        renameAfterCreation(self)

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
