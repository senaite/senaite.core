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

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.Archetypes.public import DateTimeField as BaseField
from Products.Archetypes.Registry import registerField
from Products.Archetypes.Registry import registerPropertyType
from senaite.core.api import dtime
from senaite.core.browser.widgets.datetimewidget import DateTimeWidget
from zope.i18n import translate
from zope.i18nmessageid import Message

from bika.lims import _
from bika.lims import api

WIDGET_SHOWTIME = "show_time"


class DateTimeField(BaseField):
    """An improved DateTime Field. It allows to specify
    whether only dates or only times are interesting.

    This field is ported from Products.ATExtensions
    """

    _properties = BaseField._properties.copy()
    _properties.update({
        "type": "datetime_ng",
        "widget": DateTimeWidget,
        "min": dtime.datetime.min,
        "max": dtime.datetime.max,
        "with_time": 1,  # set to False if you want date only objects
        "with_date": 1,  # set to False if you want time only objects
        })
    security = ClassSecurityInfo()

    def validate(self, value, instance, errors=None, **kwargs):
        """Validate passed-in value using all field validators plus the
        validators for minimum and maximum date values
        Return None if all validations pass; otherwise, return the message of
        of the validation failure translated to current language
        """
        # Rely on the super-class first
        error = super(DateTimeField, self).validate(
            value, instance, errors=errors, **kwargs)
        if error:
            return error

        # Return immediately if we have no value and the field is not required
        if not value and not self.required:
            return

        # Validate value is after min date
        error = self.validate_min_date(value, instance, errors=errors)
        if error:
            return error

        # Validate value is before max date
        error = self.validate_max_date(value, instance, errors=errors)
        if error:
            return error

    def validate_min_date(self, value, instance, errors=None):
        """Validates the passed-in value against the field's minimum date
        """
        if errors is None:
            errors = {}

        # self.get_min always returns an offset-naive datetime, but the value
        # is offset-aware. We need to add the TZ, otherwise we get a:
        #   TypeError: can't compare offset-naive and offset-aware datetimes
        min_date = self.get_min(instance)
        if dtime.to_ansi(value) >= dtime.to_ansi(min_date):
            return None

        error = _(
            u"error_datetime_before_min",
            default=u"${name} is before ${min_date}, please correct.",
            mapping={
                "name": self.get_label(instance),
                "min_date": self.localize(min_date, instance)
            }
        )

        field_name = self.getName()
        errors[field_name] = translate(error, context=api.get_request())
        return errors[field_name]

    def validate_max_date(self, value, instance, errors=None):
        """Validates the passed-in value against the field's maximum date
        """
        if errors is None:
            errors = {}

        # self.get_max always returns an offset-naive datetime, but the value
        # is offset-aware. We need to add the TZ, otherwise we get a:
        #   TypeError: can't compare offset-naive and offset-aware datetimes
        max_date = self.get_max(instance)
        if dtime.to_ansi(value) <= dtime.to_ansi(max_date):
            return None

        error = _(
            u"error_datetime_after_max",
            default=u"${name} is after ${max_date}, please correct.",
            mapping={
                "name": self.get_label(instance),
                "max_date": self.localize(max_date, instance)
            }
        )

        field_name = self.getName()
        errors[field_name] = translate(error, context=api.get_request())
        return errors[field_name]

    def is_true(self, val):
        """Returns whether val evaluates to True
        """
        val = str(val).strip().lower()
        return val in ["y", "yes", "1", "true", "on"]

    def get_label(self, instance):
        """Returns the translated label of this field for the given instance
        """
        request = api.get_request()
        label = self.widget.Label(instance)
        if isinstance(label, Message):
            return translate(label, context=request)
        return label

    def localize(self, dt, instance):
        """Returns the dt to localized time
        """
        request = api.get_request()
        return dtime.to_localized_time(dt, long_format=self.show_time,
                                       context=instance, request=request)

    def get_min(self, instance):
        """Returns the minimum datetime supported by this field and instance
        """
        min_date = self.resolve_date(self.min, instance)
        return min_date or dtime.datetime.min

    def get_max(self, instance):
        """Returns the maximum datetime supported for this field and instance
        """
        max_date = self.resolve_date(self.max, instance)
        return max_date or dtime.datetime.max

    def resolve_date(self, thing, instance):
        """Resolves the thing passed in to a DateTime object or None
        """
        if not thing:
            return None

        date = dtime.to_DT(thing)
        if api.is_date(date):
            return date

        if thing in ["current", "now"]:
            return dtime.datetime.now()

        # maybe a callable
        if callable(thing):
            value = thing()
            return dtime.to_DT(value)

        # maybe an instance attribute
        if hasattr(instance, thing):
            value = getattr(instance, thing)
            if callable(value):
                value = value()
            return dtime.to_DT(value)

        # maybe an instance fieldname
        if api.is_string(thing):
            fields = api.get_fields(instance)
            field = fields.get(thing)
            if field:
                value = field.get(instance)
                return dtime.to_DT(value)

        return None

    @property
    def show_time(self):
        """Returns whether the time is displayed by the widget
        """
        show_time = getattr(self.widget, WIDGET_SHOWTIME, False)
        return self.is_true(show_time)


InitializeClass(DateTimeField)


registerField(
    DateTimeField,
    title="DateTime Field",
    description="An improved DateTimeField, which also allows time "
                "or date only specifications.")


registerPropertyType("with_time", "boolean", DateTimeField)
registerPropertyType("with_date", "boolean", DateTimeField)
registerPropertyType("min", "string", DateTimeField)
registerPropertyType("max", "string", DateTimeField)
