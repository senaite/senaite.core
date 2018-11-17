# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from referencesamples import ReferenceSamplesView


class AddBlankView(ReferenceSamplesView):
    """Displays reference control samples
    """

    def __init__(self, context, request):
        super(AddBlankView, self).__init__(context, request)
        self.title = _("Add Blank Reference")

    def make_reference_sample_choices_for(self, service):
        """Create a choices list of available reference samples
        """
        reference_samples = self.get_available_reference_samples_for(service)
        blanks = filter(lambda r: r.getBlank(), reference_samples)
        choices = []
        for blank in blanks:
            text = api.get_title(blank)
            ref_def = blank.getReferenceDefinition()
            if ref_def:
                text += " ({})".format(api.get_title(ref_def))
            choices.append({
                "ResultText": text,
                "ResultValue": api.get_uid(blank),
            })
        return choices
