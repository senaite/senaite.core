# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.


def get_instrument_import_search_criteria(sample):
    sam = ['getRequestID', 'getSampleID', 'getClientSampleID']
    if sample == 'requestid':
        sam = ['getRequestID']
    if sample == 'sampleid':
        sam = ['getSampleID']
    elif sample == 'clientsid':
        sam = ['getClientSampleID']
    elif sample == 'sample_clientsid':
        sam = ['getSampleID', 'getClientSampleID']
    return sam


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
