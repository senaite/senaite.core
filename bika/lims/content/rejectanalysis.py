""" RejectAnalysis """
from Products.Archetypes.public import registerType
from bika.lims.content.analysis import Analysis
from bika.lims.config import I18N_DOMAIN, PROJECTNAME

class RejectAnalysis(Analysis):
    archetype_name = 'RejectAnalysis'

registerType(RejectAnalysis, PROJECTNAME)
