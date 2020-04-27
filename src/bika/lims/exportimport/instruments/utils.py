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

def get_instrument_import_override(override):
    over = [False, False]
    if override == 'nooverride':
        over = [False, False]
    elif override == 'override':
        over = [True, False]
    elif override == 'overrideempty':
        over = [True, True]
    return over


def get_instrument_import_ar_allowed_states(artoapply):
    status = ['sample_received', 'attachment_due', 'to_be_verified']
    if artoapply == 'received':
        status = ['sample_received']
    elif artoapply == 'received_tobeverified':
        status = ['sample_received', 'attachment_due', 'to_be_verified']
    return status
