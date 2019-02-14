import collections

from Products.Archetypes import PloneMessageFactory as _p
from Products.Archetypes.config import UID_CATALOG
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.interfaces import IWorkflowActionAdapter, \
    IWorkflowActionUIDsAdapter
from bika.lims.workflow import ActionHandlerPool
from bika.lims.workflow import doActionFor as do_action_for
from zope.component import queryMultiAdapter
from zope.component.interfaces import implements


class RequestContextAware(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.back_url = self.context.absolute_url()

    def redirect(self, redirect_url=None, message=None, level="info"):
        """Redirect with a message
        """
        if redirect_url is None:
            redirect_url = self.back_url
        if message is not None:
            self.add_status_message(message, level)
        return self.request.response.redirect(redirect_url)

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)


class WorkflowActionHandler(RequestContextAware):
    """Handler in charge of processing workflow action requests from views and
    if necessary, delegates actions to third-party subscribers/adapters.
    """
    def __init__(self, context, request):
        super(WorkflowActionHandler, self).__init__(context, request)

        # TODO This "context_uid" dance is probably no longer necessary
        self.request["context_uid"] = ""
        if api.is_object(self.context):
            self.request["context_uid"] = api.get_uid(self.context)

    def __call__(self):
        # Get the id of the action to be performed
        action = self.get_action()
        if not action:
            return self.redirect(message=_("No action defined."), level="error")

        # Get the UIDs of the objects the action needs to be done against
        uids = self.get_uids()
        if not uids:
            return self.redirect(message=_("No items selected."),
                                 level="warning")

        # Find out if there is an adapter registered for the current context
        # able to handle the requested action
        adapter_name = "workflow_action_{}".format(action)
        adapter = queryMultiAdapter((self.context, self.request),
                                    interface=IWorkflowActionAdapter,
                                    name=adapter_name)
        if not adapter:
            # No adapter found, use the generic one
            adapter = WorkflowActionGenericAdapter(self.context, self.request)
        else:
            adapter_module = adapter.__module__
            adapter_class = adapter.__class__.__name__
            logger.info("Action '{}' managed by {}.{}"
                        .format(action, adapter_module, adapter_class))

        # Handle the action
        if IWorkflowActionUIDsAdapter.providedBy(adapter):
            return adapter(action, uids)

        objects = api.search(dict(UID=uids), UID_CATALOG)
        objects = map(api.get_object, objects)
        return adapter(action, objects)

    def get_uids(self):
        """Returns a uids list of the objects this action must be performed
        against to. If no values for uids param found in the request, returns
        the uid of the current context
        """
        uids = self.get_uids_from_request()
        if not uids and api.is_object(self.context):
            uids = [api.get_uid(self.context)]
        return uids

    def get_uids_from_request(self):
        """Returns a list of uids from the request
        """
        uids = self.request.get("uids", "")
        if isinstance(uids, basestring):
            uids = uids.split(",")
        unique_uids = collections.OrderedDict().fromkeys(uids).keys()
        return filter(api.is_uid, unique_uids)

    def get_action(self):
        """Returns the action to be taken from the request. Returns None if no
        action is found

        While "workflow_action_button" is typically used by buttons in listings,
        "workflow_action" is used in edit content action menus in content type
        views (top-right selection list), with the following form:
        <content_type>/content_status_modify?workflow_action=receive
        """
        action = self.request.get("workflow_action_id", None)
        action = self.request.get("workflow_action", action)
        if not action:
            return None

        # A condition in the form causes Plone to sometimes send two actions
        # This usually happens when the previous action was not managed properly
        # and the request was not able to complete, so the previous form value
        # is kept, together with the new one.
        if type(action) in (list, tuple):
            actions = list(set(action))
            if len(actions) > 0:
                logger.warn("Multiple actions in request: {}. Fallback to '{}'"
                            .format(repr(actions), actions[-1]))
            action = actions[-1]
        return action


class WorkflowActionGenericAdapter(RequestContextAware):
    """General purpose adapter for processing workflow action requests
    """
    implements(IWorkflowActionAdapter)

    def __call__(self, action, objects):
        """Performs the given action to the objects passed in
        """
        transitioned = self.do_action(action, objects)
        if not transitioned:
            return self.redirect(message=_("No changes made."), level="warning")

        # TODO Here we could handle subscriber adapters here?

        # Redirect the user to success page
        return self.success(transitioned)

    def do_action(self, action, objects):
        """Performs the workflow transition passed in and returns the list of
        objects that have been successfully transitioned
        """
        transitioned = []
        ActionHandlerPool.get_instance().queue_pool()
        for obj in objects:
            obj = api.get_object(obj)
            success, message = do_action_for(obj, action)
            if success:
                transitioned.append(obj)
        ActionHandlerPool.get_instance().resume()
        return transitioned

    def is_context_only(self, objects):
        """Returns whether the action applies to the current context only
        """
        if len(objects) > 1:
            return False
        return api.get_object(objects[0]) == self.context

    def success(self, objects):
        """Redirects the user to success page with informative message
        """
        if self.is_context_only(objects):
            return self.redirect(message=_p("Changes saved."))

        ids = map(api.get_id, objects)
        message = _("Saved items: {}").format(", ".join(ids))
        return self.redirect(message=message)

    def get_form_value(self, form_key, object_brain_uid, default=None):
        """Returns a value from the request's form, if any
        """
        uid = object_brain_uid
        if not api.is_uid(uid):
            uid = api.get_uid(object_brain_uid)
        val = self.request.form.get(form_key, None) or [{}]
        val = val[0] or {}
        return val.get(uid, default)
