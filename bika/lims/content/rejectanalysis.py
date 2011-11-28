""" RejectAnalysis """
from Products.Archetypes.public import registerType
from bika.lims.content.analysis import Analysis
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
from bika.lims import bikaMessageFactory as _

class RejectAnalysis(Analysis):
    archetype_name = 'RejectAnalysis'
    displayContentsTab = False

registerType(RejectAnalysis, PROJECTNAME)
