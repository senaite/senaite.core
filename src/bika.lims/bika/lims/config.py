"""Common configuration constants
"""

PROJECTNAME = 'bika.lims'

# __init__.py uses these permissions for the Zope 2 object factories.
ADD_PERMISSIONS = {
    # -*- extra stuff goes here -*-
    'AnalysisService': 'bika.lims: Add Analysis Service',
    'Result': 'bika.lims: Add Result',
    'Sample': 'bika.lims: Add Sample',
    'AnalysisRequest': 'bika.lims: Add AnalysisRequest',
    'Analysis': 'bika.lims: Add Analysis',
    'Contact': 'bika.lims: Add Contact',
    'Client': 'bika.lims: Add Client',
    'ClientFolder': 'bika.lims: Add ClientFolder',
}
