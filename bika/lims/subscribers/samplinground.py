from bika.lims.idserver import renameAfterCreation

def SamplingRoundAddedEventHandler(instance, event):
    """ Event fired when BikaSetup object gets modified.
        Since Sampling Round is a dexterity object we have to change the ID by "hand"
        Then we have to redirect the user to the ar add form
    """
    if instance.portal_type != "SamplingRound":
        print("How does this happen: type is %s should be SamplingRound" % instance.portal_type)
        return
    renameAfterCreation(instance)
    num_art = len(instance.ar_templates)
    destination_url = instance.aq_parent.absolute_url() + \
                    "/portal_factory/" + \
                    "AnalysisRequest/Request new analyses/ar_add?samplinground=" + \
                    instance.UID() + "&ar_count=" + str(num_art)
    request = getattr(instance, 'REQUEST', None)
    request.response.redirect(destination_url)
