# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api
from bika.lims.browser.sample import SamplesView as _SV


class SamplesView(_SV):

    def __init__(self, context, request):
        super(SamplesView, self).__init__(context, request)
        self.view_url = self.context.absolute_url() + "/samples"
        self.contentFilter = {'portal_type': 'Sample',
                              'getBatchUIDs': api.get_uid(self.context),
                              'sort_on': 'created',
                              'sort_order': 'reverse',
                              'cancellation_state':'active'}
