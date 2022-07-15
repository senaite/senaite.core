# -*- coding: utf-8 -*-

from bika.lims import api


def isTemporary(self):
    return api.is_temporary(self)
