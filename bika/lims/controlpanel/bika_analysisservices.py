from Products.CMFPlone.utils import _createObjectByType, safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import IAnalysisServices
from bika.lims.utils import tmpID
from bika.lims.validators import ServiceKeywordValidator
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from plone.app.layout.globals.interfaces import IViewView
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from transaction import savepoint
from zope.interface.declarations import implements


class AnalysisServiceCopy(BrowserView):
    template = ViewPageTemplateFile('templates/analysisservice_copy.pt')
    # should never be copied between services
    skip_fieldnames = [
        'UID',
        'id',
        'title',
        'ShortTitle',
        'Keyword',
    ]
    created = []

    def create_service(self, src_uid, dst_title, dst_keyword):
        folder = self.context.bika_setup.bika_analysisservices
        dst_service = _createObjectByType("AnalysisService", folder, tmpID())
        # manually set keyword and title
        dst_service.setKeyword(dst_keyword)
        dst_service.setTitle(dst_title)
        dst_service.unmarkCreationFlag()
        _id = renameAfterCreation(dst_service)
        dst_service = folder[_id]
        return dst_service

    def validate_service(self, dst_service):
        # validate entries
        validator = ServiceKeywordValidator()
        # baseschema uses uniquefieldvalidator on title, this is sufficient.
        res = validator(dst_service.getKeyword(), instance=dst_service)
        if res is not True:
            self.savepoint.rollback()
            self.created = []
            self.context.plone_utils.addPortalMessage(res, 'info')
            return False
        return True

    def copy_service(self, src_uid, dst_title, dst_keyword):
        uc = getToolByName(self.context, 'uid_catalog')
        src_service = uc(UID=src_uid)[0].getObject()
        dst_service = self.create_service(src_uid, dst_title, dst_keyword)
        if self.validate_service(dst_service):
            # copy field values
            for field in src_service.Schema().fields():
                fieldname = field.getName()
                if field.getType() == "Products.Archetypes.Field.ComputedField" \
                        or fieldname in self.skip_fieldnames:
                    continue
                getter = field.getAccessor(src_service)
                setter = dst_service.Schema()[fieldname].getMutator(dst_service)
                setter(getter())
            dst_service.reindexObject()
            return dst_title
        else:
            return False

    def __call__(self):
        uc = getToolByName(self.context, 'uid_catalog')
        if 'copy_form_submitted' not in self.request:
            uids = self.request.form.get('uids', [])
            self.services = []
            for uid in uids:
                proxies = uc(UID=uid)
                if proxies:
                    self.services.append(proxies[0].getObject())
            return self.template()
        else:
            self.savepoint = savepoint()
            sources = self.request.form.get('uids', [])
            titles = self.request.form.get('dst_title', [])
            keywords = self.request.form.get('dst_keyword', [])
            self.created = []
            for i, s in enumerate(sources):
                if not titles[i]:
                    message = _('Validation failed: title is required')
                    self.context.plone_utils.addPortalMessage(message, 'info')
                    self.savepoint.rollback()
                    self.created = []
                    break
                if not keywords[i]:
                    message = _('Validation failed: keyword is required')
                    self.context.plone_utils.addPortalMessage(message, 'info')
                    self.savepoint.rollback()
                    self.created = []
                    break
                title = self.copy_service(s, titles[i], keywords[i])
                if title:
                    self.created.append(title)
            if len(self.created) > 1:
                message = t(_(
                    '${items} were successfully created.',
                    mapping={'items': safe_unicode(', '.join(self.created))}))
            elif len(self.created) == 1:
                message = t(_(
                    '${item} was successfully created.',
                    mapping={'item': safe_unicode(self.created[0])}))
            else:
                message = _('No new items were created.')
            self.context.plone_utils.addPortalMessage(message, 'info')
            self.request.response.redirect(self.context.absolute_url())


class AnalysisServicesView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        """
        """

        super(AnalysisServicesView, self).__init__(context, request)
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'portal_type': 'AnalysisService',
                              'sort_on': 'sortable_title'}
        self.context_actions = {
            _('Add'):
                {'url': 'createObject?type_name=AnalysisService',
                 'icon': '++resource++bika.lims.images/add.png'}}
        self.icon = self.portal_url + \
            "/++resource++bika.lims.images/analysisservice_big.png"
        self.title = self.context.translate(_("Analysis Services"))
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.show_select_all_checkbox = False
        self.pagesize = 25

        self.categories = []
        self.do_cats = self.context.bika_setup.getCategoriseAnalysisServices()
        if self.do_cats:
            self.pagesize = 999999  # hide batching controls
            self.show_categories = True
            self.expand_all_categories = False
            self.ajax_categories = True
            self.category_index = 'getCategoryTitle'

        self.columns = {
            'Title': {'title': _('Service'),
                      'index': 'sortable_title'},
            'Keyword': {'title': _('Keyword'),
                        'index': 'getKeyword'},
            'Category': {'title': _('Category')},
            'Method': {'title': _('Method'),
                       'toggle': False},
            'Department': {'title': _('Department'),
                           'toggle': False},
            'Instrument': {'title': _('Instrument')},
            'Unit': {'title': _('Unit')},
            'Price': {'title': _('Price')},
            'MaxTimeAllowed': {'title': _('Max Time'),
                               'toggle': False},
            'DuplicateVariation': {'title': _('Dup Var'),
                                   'toggle': False},
            'Calculation': {'title': _('Calculation')},
            'CommercialID': {'title': _('Commercial ID'),
                             'toggle': True},
            'ProtocolID': {'title': _('Protocol ID'),
                           'toggle': True},
        }

        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id': 'deactivate'}, ],
             'columns': ['Title',
                         'Category',
                         'Keyword',
                         'Method',
                         'Department',
                         'CommercialID',
                         'ProtocolID',
                         'Instrument',
                         'Unit',
                         'Price',
                         'MaxTimeAllowed',
                         'DuplicateVariation',
                         'Calculation',
                         ],
             'custom_actions': [{'id': 'duplicate',
                                 'title': _('Duplicate'),
                                 'url': 'copy'}, ]
             },
            {'id': 'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id': 'activate'}, ],
             'columns': ['Title',
                         'Category',
                         'Keyword',
                         'Method',
                         'Department',
                         'CommercialID',
                         'ProtocolID',
                         'Instrument',
                         'Unit',
                         'Price',
                         'MaxTimeAllowed',
                         'DuplicateVariation',
                         'Calculation',
                         ],
             'custom_actions': [{'id': 'duplicate',
                                 'title': _('Duplicate'),
                                 'url': 'copy'}, ]
             },
            {'id': 'all',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['Title',
                         'Keyword',
                         'Category',
                         'Method',
                         'Department',
                         'CommercialID',
                         'ProtocolID',
                         'Instrument',
                         'Unit',
                         'Price',
                         'MaxTimeAllowed',
                         'DuplicateVariation',
                         'Calculation',
                         ],
             'custom_actions': [{'id': 'duplicate',
                                 'title': _('Duplicate'),
                                 'url': 'copy'}, ]
             },
        ]

        if not self.context.bika_setup.getShowPrices():
            for i in range(len(self.review_states)):
                self.review_states[i]['columns'].remove('Price')

    def folderitems(self):

        items = BikaListingView.folderitems(self)

        for x in range(len(items)):
            if 'obj' not in items[x]:
                continue
            obj = items[x]['obj']

            # Although these should be automatically inserted when bika_listing
            # searches the schema for fields that match columns, it is still
            # not harmful to be explicit:
            items[x]['Keyword'] = obj.getKeyword()
            items[x]['CommercialID'] = obj.getCommercialID()
            items[x]['ProtocolID'] = obj.getProtocolID()

            cat = obj.getCategoryTitle()
            # Category (upper C) is for display column value
            items[x]['Category'] = cat
            if self.do_cats:
                # category is for bika_listing to groups entries
                items[x]['category'] = cat
                if cat not in self.categories:
                    self.categories.append(cat)

            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % (
                items[x]['url'], items[x]['Title'])

            instrument = obj.getInstrument()
            items[x]['Instrument'] = instrument and instrument.Title() or ''
            if instrument:
                items[x]['replace']['Instrument'] = "<a href='%s'>%s</a>" % (
                    instrument.absolute_url() + "/edit", instrument.Title())

            items[x]['Department'] = obj.getDepartment().Title() \
                if obj.getDepartment() else ''

            calculation = obj.getCalculation()
            items[x]['Calculation'] = calculation and calculation.Title()
            if calculation:
                items[x]['replace']['Calculation'] = "<a href='%s'>%s</a>" % (
                    calculation.absolute_url() + "/edit", calculation.Title())

            items[x]['Unit'] = obj.getUnit() and obj.getUnit() or ''
            items[x]['Price'] = "%s.%02d" % obj.Price

            method = obj.getMethod()
            items[x]['Method'] = method and method.Title() or ''
            if method:
                items[x]['replace']['Method'] = "<a href='%s'>%s</a>" % (
                    method.absolute_url(), method.Title())

            maxtime = obj.MaxTimeAllowed
            maxtime_string = ""
            for field in ('days', 'hours', 'minutes'):
                if field in maxtime:
                    try:
                        val = int(maxtime[field])
                        if val > 0:
                            maxtime_string += "%s%s " % (val, _(field[0]))
                    except:
                        pass
            items[x]['MaxTimeAllowed'] = maxtime_string

            if obj.DuplicateVariation is not None:
                items[x]['DuplicateVariation'] = "%s.%02d" % (
                    obj.DuplicateVariation)
            else:
                items[x]['DuplicateVariation'] = ""

            after_icons = ''
            ipath = "++resource++bika.lims.images"
            if obj.getAccredited():
                after_icons += "<img src='%s/accredited.png' title='%s'>" % (
                    ipath, _("Accredited"))
            if obj.getReportDryMatter():
                after_icons += "<img src='%s/dry.png' title='%s'>" % (
                    ipath, _("Can be reported as dry matter"))
            if obj.getAttachmentOption() == 'r':
                after_icons += "<img src='%s/attach_reqd.png' title='%s'>" % (
                    ipath, _("Attachment required"))
            if obj.getAttachmentOption() == 'n':
                after_icons += "<img src='%s/attach_no.png' title='%s'>" % (
                    ipath, _('Attachment not permitted'))
            if after_icons:
                items[x]['after']['Title'] = after_icons

        self.categories.sort()
        return items


schema = ATFolderSchema.copy()


class AnalysisServices(ATFolder):
    implements(IAnalysisServices)
    displayContentsTab = False
    schema = schema


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(AnalysisServices, PROJECTNAME)
