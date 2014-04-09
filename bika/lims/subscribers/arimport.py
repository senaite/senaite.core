def ARImportModifiedEventHandler(instance, event):

    if instance.portal_type != "ARImport":
        print("How does this happen: type is %s should be ARImport" % instance.portal_type)
        return

    instance.validateIt()


def ARImportItemModifiedEventHandler(instance, event):

    if instance.portal_type != "ARImportItem":
        print("How does this happen: type is %s, should be ARImportItem" % instance.portal_type)
        return

    instance.aq_inner.aq_parent.validateIt()
