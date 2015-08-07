from zope.interface import implements
from bika.lims.browser.bika_listing import BikaListingView
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from bika.lims import bikaMessageFactory as _


class MultifileView(BikaListingView):
    """
    This class implements a bika listing base view. This view is thought to be used inside other content types actions
    as a default way to upload and show documentation.
    This class should be modified for each different content type, for instance: if you want this class as a place to
    upload instrument documentation, you should rename the columns, description, and title
    """
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(MultifileView, self).__init__(context, request)
        self.catalog = "bika_setup_catalog"
        self.contentFilter = {
            'portal_type': 'Multifile',
        }
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=Multifile',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.show_table_only = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25
        self.form_id = "multifile"
        self.icon = self.portal_url + "/++resource++bika.lims.images/instrumentcertification_big.png"
        self.title = self.context.translate(_("Files"))
        self.description = ""

        self.columns = {
            'DocumentID': {'title': _('Document ID'),
                           'index': 'sortable_title'},
            'DocumentVersion': {'title': _('Document Version'), 'index': 'sortable_title'},
            'DocumentLocation': {'title': _('Document Location'), 'index': 'sortable_title'},
            'DocumentType': {'title': _('Document Type'), 'index': 'sortable_title'},
            'FileDownload': {'title': _('File')}
        }
        self.review_states = [
            {'id': 'default',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['DocumentID',
                         'DocumentVersion',
                         'DocumentLocation',
                         'DocumentType',
                         'FileDownload']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        outitems = []
        toshow = []
        for val in self.context.getDocuments():
            toshow.append(val.UID())
        for x in range (len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            if obj.UID() in toshow:
                items[x]['replace']['DocumentID'] = "<a href='%s'>%s</a>" % \
                    (items[x]['url'], items[x]['DocumentID'])
                items[x]['FileDownload'] = obj.getFile().filename
                filename = obj.getFile().filename if obj.getFile().filename != '' else 'File'
                items[x]['replace']['FileDownload'] = "<a href='%s'>%s</a>" % \
                    (obj.getFile().absolute_url_path(), filename)
                items[x]['DocumentVersion'] = obj.getDocumentVersion()
                items[x]['DocumentLocation'] = obj.getDocumentLocation()
                items[x]['DocumentType'] = obj.getDocumentType()
                outitems.append(items[x])
        return outitems
