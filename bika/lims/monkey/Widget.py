from bika.lims.interfaces import IATWidgetVisibility
from types import DictType
from plone import api
from Acquisition import aq_base
from zope.component import getAdapters

_marker = []

# Products.Archetypes.Schema.Schemata#editableFields
def editableFields(self, instance, visible_only=False):
    """Returns a list of editable fields for the given instance
    """
    ret = []
    portal = api.portal.get_tool('portal_url').getPortalObject()
    for field in self.fields():
        if field.writeable(instance, debug=False) and    \
               (not visible_only or
                field.widget.isVisible(
                    instance, mode='edit', field=field) != 'invisible') and \
                field.widget.testCondition(instance.aq_parent, portal, instance):
            ret.append(field)
    return ret

# Products.Archetypes.Widget.TypesWidget#isVisible
def isVisible(self, instance, mode='view', default=None, field=None):
    """decide if a field is visible in a given mode -> 'state'.
    """

    # First get the original value, to use as our default
    vis_dic = getattr(aq_base(self), 'visible', _marker)
    state = default if default else 'visible'
    if vis_dic is _marker:
        return state
    if type(vis_dic) is DictType:
        state = vis_dic.get(mode, state)
    elif not vis_dic:
        state = 'invisible'
    elif vis_dic < 0:
        state = 'hidden'

    if not field:
        return state

    # call any IATWidgetVisibility adapters
    adapters = {}
    for adapter in getAdapters((instance, ), IATWidgetVisibility):
        sort_val = getattr(adapter[1], 'sort', 1000)
        if sort_val not in adapters:
            adapters[sort_val] = []
        adapters[sort_val].append(adapter)
    keys = sorted(adapters.keys())
    keys.reverse()
    for key in keys:
        for adapter in adapters[key]:
            oldstate = state
            state = adapter[1](instance, mode, field, state)
            # if state != oldstate:
            #     adapter_name = adapter[1].__repr__().split(" ")[0].split(".")[-1]
            #     print "%-25s %-25s adapter:%s"%(field.getName(), "%s->%s"%(oldstate, state), adapter_name)

    return state
