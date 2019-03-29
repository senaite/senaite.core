# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018-2019 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

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
