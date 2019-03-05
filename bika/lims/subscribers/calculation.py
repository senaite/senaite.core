# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2019 by it's authors.
# Some rights reserved.

from bika.lims import api


def ObjectInitializedEventHandler(calculation, event):
    """Actions to be done after a Calculation is created. It sets the initial
    version id of the calculation object to 0
    """
    pr = api.get_tool("portal_repository")
    pr.save(obj=calculation, comment="First version")
