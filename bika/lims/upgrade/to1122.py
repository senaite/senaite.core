from Acquisition import aq_inner
from Acquisition import aq_parent


def upgrade(tool):
    """ Move add_ar.js from ar_add.pt to to jsregistry.xml.
        To be sure that is loaded before other dependant js registered in
        jsregistry.xml from other projects
    """
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    setup.runImportStepFromProfile('profile-bika.lims:default', 'jsregistry')

    return True
