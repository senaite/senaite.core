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
# Copyright 2018-2023 by it's authors.
# Some rights reserved, see README and LICENSE.

from zope.interface import classImplementsFirst

from .addressfield import AddressField
from .addressfield import IAddressField
from .datetimefield import DatetimeField
from .fields import IntField
from .interfaces import IDatetimeField
from .interfaces import IIntField
from .interfaces import IRichTextField
from .phonefield import IPhoneField
from .phonefield import PhoneField
from .richtextfield import RichTextField
from .uidreferencefield import IUIDReferenceField
from .uidreferencefield import UIDReferenceField

classImplementsFirst(AddressField, IAddressField)
classImplementsFirst(DatetimeField, IDatetimeField)
classImplementsFirst(IntField, IIntField)
classImplementsFirst(PhoneField, IPhoneField)
classImplementsFirst(RichTextField, IRichTextField)
classImplementsFirst(UIDReferenceField, IUIDReferenceField)
