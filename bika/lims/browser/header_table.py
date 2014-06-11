"""ARs and Samples use HeaderTable to display object fields in their custom
view and edit screens.
"""

from bika.lims.browser import BrowserView
from bika.lims.interfaces import IHeaderTableFieldRenderer
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _p
from bika.lims.utils import getHiddenAttributesForClass
from zope.component import getAdapter
from AccessControl import getSecurityManager
from AccessControl.Permissions import view
from zope.component.interfaces import ComponentLookupError

class HeaderTableView(BrowserView):

    template = ViewPageTemplateFile('templates/header_table.pt')

    def __call__(self):
        self.errors = {}
        if 'header_table_submitted' in self.request:
            schema = self.context.Schema()
            fields = schema.fields()
            form = self.request.form
            for field in fields:
                fieldname = field.getName()
                if fieldname in form:
                    if fieldname + "_uid" in form:
                        # references (process_form would normally do *_uid trick)
                        field.getMutator(self.context)(form[fieldname + "_uid"])
                    else:
                        # other fields
                        field.getMutator(self.context)(form[fieldname])
            message = _p("Changes saved.")
            self.context.plone_utils.addPortalMessage(message, 'info')
        return self.template()

    def three_column_list(self, input_list):
        list_len = len(input_list)

        # Calculate the length of the sublists
        sublist_len = (list_len % 3 == 0 and list_len / 3 or list_len / 3 + 1)

        def _list_end(num):
            # Calculate the list end point given the list number
            return num == 2 and list_len or (num + 1) * sublist_len

        # Generate only filled columns
        final = []
        for i in range(3):
            column = input_list[i * sublist_len:_list_end(i)]
            if len(column) > 0:
                final.append(column)
        return final

    def render_field_view(self, fieldname):
        field = self.context.Schema()[fieldname]
        ret = {'fieldName': fieldname, 'mode': 'view'}
        try:
            adapter = getAdapter(self.context,
                                 interface=IHeaderTableFieldRenderer,
                                 name=fieldname)
        except ComponentLookupError:
            adapter = None
        if adapter:
            ret = {'fieldName': fieldname,
                   'mode': 'structure',
                   'html': adapter(field)}
        else:
            if field.getType().find("Reference") > -1:
                # Prioritize method retrieval over schema's field
                targets = None
                if hasattr(self.context, 'get%s' % fieldname):
                    fieldaccessor = getattr(self.context, 'get%s' % fieldname)
                    if callable(fieldaccessor):
                        targets = fieldaccessor()
                if not targets:
                    targets = field.get(self.context)

                if targets:
                    if not type(targets) == list:
                        targets = [targets,]
                    sm = getSecurityManager()
                    if all([sm.checkPermission(view, t) for t in targets]):
                        a = ["<a href='%s'>%s</a>" % (target.absolute_url(),
                                                      target.Title())
                             for target in targets]
                        ret = {'fieldName': fieldname,
                               'mode': 'structure',
                               'html': ", ".join(a)}
                    else:
                        ret = {'fieldName': fieldname,
                               'mode': 'structure',
                               'html': ", ".join([t.Title() for t in targets])}
                else:
                    ret = {'fieldName': fieldname,
                           'mode': 'structure',
                           'html': ''}
        return ret

    def sublists(self):
        ret = []
        prominent = []
        adapter = getAdapter(self.context, name='getWidgetVisibility')
        wv = adapter()
        new_wv = {}
        # respect schemaextender's re-ordering of fields, and
        # remove hidden attributes.
        hiddenattributes = getHiddenAttributesForClass(self.context.portal_type)
        schema_fields = [f.getName() for f in self.context.Schema().fields()]
        for mode, state_field_lists in wv.items():
            new_wv[mode] = {}
            for statename, state_fields in state_field_lists.items():
                new_wv[mode][statename] = \
                    [field for field in schema_fields
                     if field in state_fields
                     and field not in hiddenattributes]
        edit_fields = new_wv.get("edit", {}).get('visible', [])
        view_fields = new_wv.get("view", {}).get('visible', [])
        # Prominent fields get appended
        prominent_fieldnames = new_wv.get('header_table', {}).get('prominent', [])
        for fieldname in prominent_fieldnames:
            if fieldname in view_fields:
                prominent.append(self.render_field_view(fieldname))
            elif fieldname in edit_fields:
                prominent.append({'fieldName': fieldname, 'mode': "edit"})
        # Other visible fields get appended
        visible_fieldnames = new_wv.get('header_table', {}).get('visible', [])
        for fieldname in visible_fieldnames:
            if fieldname in prominent_fieldnames:
                continue
            if fieldname in edit_fields:
                ret.append({'fieldName': fieldname, 'mode': "edit"})
            elif fieldname in view_fields:
                ret.append(self.render_field_view(fieldname))
        return prominent, self.three_column_list(ret)
