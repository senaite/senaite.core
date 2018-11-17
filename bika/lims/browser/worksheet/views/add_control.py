# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from referencesamples import ReferenceSamplesView


class AddControlView(ReferenceSamplesView):
    """Displays reference control samples
    """

    def __init__(self, context, request):
        super(AddControlView, self).__init__(context, request)
        self.title = _("Add Control Reference")

    def make_reference_sample_choices_for(self, service):
        """Create a choices list of available reference samples
        """
        reference_samples = self.get_available_reference_samples_for(service)
        controls = filter(lambda r: not r.getBlank(), reference_samples)
        choices = []
        for control in controls:
            text = api.get_title(control)
            ref_def = control.getReferenceDefinition()
            if ref_def:
                text += " ({})".format(api.get_title(ref_def))
            choices.append({
                "ResultText": text,
                "ResultValue": api.get_uid(control),
            })
        return choices
