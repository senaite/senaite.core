# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import ClassSecurityInfo

from Products.Archetypes.Registry import registerWidget

from bika.lims.browser.widgets import RecordsWidget


class SampleTypeStickersWidget(RecordsWidget):
    security = ClassSecurityInfo()
    _properties = RecordsWidget._properties.copy()
    _properties.update({
        'helper_js': (
            "bika_widgets/recordswidget.js",
            "bika_widgets/sampletypestickerswidget.js",),
    })


registerWidget(
    SampleTypeStickersWidget,
    title="Sample type stickers widget",
    description='Defines the available stickers for a sample type.',
    )
