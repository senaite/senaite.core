from Acquisition import aq_inner
from Acquisition import aq_parent

from bika.lims import logger
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
import transaction
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from Products.CMFCore.utils import getToolByName

product = 'bika.lims'
version = '3.2.0.1708'


@upgradestep(product, version)
def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    ut = UpgradeUtils(portal)
    logger.info("Anonimating database objects...")

    anonimate_clients(portal)

    logger.info("Objects anonimated.")
    return True


def anonimate_clients(portal):
    """
    It walks over all client objects and changes the sensible data
    """
    catalog = getToolByName(portal, "uid_catalog")
    brains = catalog(portal_type='Client')
    tot_counter = 0
    total = len(brains)
    prefix = "Client-"
    for brain in brains:
        obj = brain.getObject()
        title = prefix + str(tot_counter)
        obj.setCCEmails("person@email.com")
        obj.setEmailAddress("person@email.com")
        obj.setTitle(title)
        obj.setName(title)
        obj.setPhone("777777")
        obj.setFax("7777777")
        import pdb; pdb.set_trace()
        setPhysicalAddress(obj)
        setPostalAddress(obj)
        setBillingAddress(obj)
        obj.setAccountName("My Account")
        obj.setAccountNumber("45454545")
        obj.setBankName("My Bank")
        obj.setBranch("Bank branch")
        obj.reindexObject()

        tot_counter += 1
        if tot_counter % 500 == 0:
            logger.info(
                "Setting missing DateSampled values of "
                "ARs: %d of %d".format(tot_counter, total))
            transaction.commit()
    transaction.commit()


def anonimate_contact(portal):
    """
    It walks over all client objects and changes the sensible data
    """
    catalog = getToolByName(portal, "uid_catalog")
    brains = catalog(portal_type='Contact')
    tot_counter = 0
    total = len(brains)
    prefix = "Contact-"
    for brain in brains:
        obj = brain.getObject()
        title = prefix + str(tot_counter)
        obj.setFirstname()
        obj.setMiddleinitial(title)
        obj.setMiddlename(title)
        obj.setSurname(title)
        obj.setUsername(title)
        obj.setEmailAddress("person@email.com")
        obj.setBusinessPhone("99999")
        obj.setBusinessFax("999999")
        obj.setHomePhone("000000")
        obj.setMobilePhone("000000")

        setPhysicalAddress(obj)
        setPostalAddress(obj)
        setBillingAddress(obj)
        obj.reindexObject()

        tot_counter += 1
        if tot_counter % 500 == 0:
            logger.info(
                "Setting missing DateSampled values of "
                "ARs: %d of %d".format(tot_counter, total))
            transaction.commit()
    transaction.commit()


def setPhysicalAddress(obj):
    import pdb; pdb.set_trace()
    pass


def setPostalAddress(obj):
    pass


def setBillingAddress(obj):
    pass
