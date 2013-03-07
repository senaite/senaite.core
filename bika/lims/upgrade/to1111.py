from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName


def upgrade(tool):
    """
    """
    portal = aq_parent(aq_inner(tool))
    portal_catalog = getToolByName(portal, 'portal_catalog')
    typestool = getToolByName(portal, 'portal_types')
    setup = portal.portal_setup

    # Reimport Types Tool to add SampleCondition
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')

    # Changes to the catalogs
    at = getToolByName(portal, 'archetype_tool')
    at.setCatalogsByType('SampleCondition', ['bika_setup_catalog'])

    # Add SampleConditions folder at bika_setup/bika_sampleconditions
    bikasetup = portal['bika_setup']
    typestool.constructContent(type_name="SampleConditions",
                               container=bikasetup,
                               id='bika_sampleconditions',
                               title='Sample Conditions')
    obj = bikasetup['bika_sampleconditions']
    obj.unmarkCreationFlag()
    obj.reindexObject()

    # Add SampleCondition to all Sample objects
    proxies = portal_catalog(portal_type="Sample")
    samples = (proxy.getObject() for proxy in proxies)
    for sample in samples:
        sample.setSampleCondition(None)

    return True
