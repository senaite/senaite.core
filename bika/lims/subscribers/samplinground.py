from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions
from bika.lims.permissions import ManageWorksheets
from bika.lims.permissions import AddClient, EditClient, ManageClients
from bika.lims.idserver import renameAfterCreation

def SamplingRoundModifiedEventHandler(instance, event):
    """ Event fired when BikaSetup object gets modified.
        Since Sampling Round is a dexterity object we have to change the ID by "hand"
    """
    if instance.portal_type != "SamplingRound":
        print("How does this happen: type is %s should be SamplingRound" % instance.portal_type)
        return

    renameAfterCreation(instance)
