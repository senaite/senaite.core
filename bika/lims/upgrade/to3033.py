from Acquisition import aq_parent, aq_inner


def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    setup.runImportStepFromProfile(
            'profile-bika.lims:default', 'propertiestool')

    return True
