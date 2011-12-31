""" RejectAnalysis """
from Products.Archetypes.public import registerType
from bika.lims.content.analysis import Analysis
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _

class RejectAnalysis(Analysis):
    archetype_name = 'RejectAnalysis'

registerType(RejectAnalysis, PROJECTNAME)
