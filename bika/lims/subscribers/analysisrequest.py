def ObjectInitializedEventHandler(instance, event):

    if instance.portal_type != "AnalysisRequest":
        return

    priority = instance.getPriority()
    if priority:
        return

    instance.setDefaultPriority()
    return
