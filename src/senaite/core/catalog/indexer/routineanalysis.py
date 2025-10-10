# -*- coding: utf-8 -*-

from bika.lims.interfaces import IRoutineAnalysis
from plone.indexer import indexer


@indexer(IRoutineAnalysis)
def has_calculation(instance):
    calculation_uid = instance.getRawCalculation()
    if not calculation_uid:
        return False
    return True
