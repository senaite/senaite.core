from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.workflow import WorkflowActionGenericAdapter, \
    RequestContextAware
from bika.lims.interfaces import IAnalysisRequest, IWorkflowActionUIDsAdapter
from zope.component.interfaces import implements


class WorkflowActionCopyToNewAdapter(RequestContextAware):
    """Adapter in charge of Analysis Requests 'copy_to_new' action
    """
    implements(IWorkflowActionUIDsAdapter)

    def __call__(self, action, uids):
        url = "{}/ar_add?ar_count={}&copy_from={}".format(
            self.back_url, len(uids), ",".join(uids))
        return self.redirect(redirect_url=url)


class WorkflowActionPrintStickersAdapter(RequestContextAware):
    """Adapter in charge of Analysis Requests 'print_stickers' action
    """
    implements(IWorkflowActionUIDsAdapter)

    def __call__(self, action, uids):
        url = "{}/sticker?template={}&items={}".format(self.back_url,
            self.context.bika_setup.getAutoStickerTemplate(), ",".join(uids))
        return self.redirect(redirect_url=url)


class WorkflowActionCreatePartitionsAdapter(RequestContextAware):
    """Adapter in charge of Analysis Requests 'copy_to_new' action
    """
    implements(IWorkflowActionUIDsAdapter)

    def __call__(self, action, uids):
        url = "{}/partition_magic?uids={}".format(self.back_url, ",".join(uids))
        return self.redirect(redirect_url=url)


class WorkflowActionPublishAdapter(RequestContextAware):
    """Adapter in charge of Analysis Requests 'publish'-like actions
    """
    implements(IWorkflowActionUIDsAdapter)

    def __call__(self, action, uids):
        purl = self.context.portal_url()
        uids = ",".join(uids)
        url = "{}/analysisrequests/publish?items={}".format(purl, uids)
        return self.redirect(redirect_url=url)


class WorkflowActionReceiveAdapter(WorkflowActionGenericAdapter):
    """Adapter in charge of Analysis Request receive action
    """

    def __call__(self, action, objects):
        transitioned = self.do_action(action, objects)
        if not transitioned:
            return self.redirect(message=_("No changes made"), level="warning")

        auto_partitions = filter(self.is_auto_partition_required, objects)
        if auto_partitions:
            # Redirect to the partitioning view
            uids = ",".join(map(api.get_uid, auto_partitions))
            url = "{}/partition_magic?uids={}".format(self.back_url, uids)
            return self.redirect(redirect_url=url)

        elif self.is_auto_print_stickers_enabled():
            # Redirect to the auto-print stickers view
            uids = ",".join(map(api.get_uid, transitioned))
            sticker_template = self.context.bika_setup.getAutoStickerTemplate()
            url = "{}/sticker?autoprint=1&template={}&items={}".format(
                self.back_url, sticker_template, uids)
            return self.redirect(redirect_url=url)

        # Redirect the user to success page
        return self.success(transitioned)

    def is_auto_partition_required(self, brain_or_object):
        """Returns whether the passed in object needs to be partitioned
        """
        obj = api.get_object(brain_or_object)
        if not IAnalysisRequest.providedBy(obj):
            return False
        template = obj.getTemplate()
        return template and template.getAutoPartition()

    def is_auto_print_stickers_enabled(self):
        """Returns whether the auto print of stickers on reception is enabled
        """
        return "receive" in self.context.bika_setup.getAutoPrintStickers()
