"""ARs and Samples use HeaderTable to display object fields in their custom
view and edit screens.
"""

from bika.lims.browser import BrowserView
from bika.lims.interfaces import IHeaderTableFieldRenderer
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _p
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
            return (num == 2 and list_len or (num + 1) * sublist_len)

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
                target = field.get(self.context)
                if target:
                    sm = getSecurityManager()
                    if sm.checkPermission(view, target):
                        a = "<a href='%s'>%s</a>" % (target.absolute_url(),
                                                     target.Title())
                        ret = {'fieldName': fieldname,
                               'mode': 'structure',
                               'html': a}
                    else:
                        ret = {'fieldName': fieldname,
                               'mode': 'structure',
                               'html': target.Title()}
                else:
                    ret = {'fieldName': fieldname,
                           'mode': 'structure',
                           'html': ''}
        return ret

    def sublists(self, mode):
        ret = []
        prominent = []
        adapter = getAdapter(self.context, name='getWidgetVisibility')
        wv = adapter()
        edit = wv.get('edit', {}).get('visible', [])
        view = wv.get('view', {}).get('visible', [])

        prominent_fieldnames = wv.get('header_table', {}).get('prominent', [])
        for fieldname in prominent_fieldnames:
            if fieldname in view:
                prominent.append(self.render_field_view(fieldname))
            elif fieldname in edit:
                prominent.append({'fieldName': fieldname, 'mode': 'edit'})

        visible_fieldnames = wv.get('header_table', {}).get('visible', [])
        for fieldname in visible_fieldnames:
            if fieldname in prominent_fieldnames:
                continue
            if fieldname in edit:
                ret.append({'fieldName': fieldname, 'mode': 'edit'})
            elif fieldname in view:
                ret.append(self.render_field_view(fieldname))

        return prominent, self.three_column_list(ret)
