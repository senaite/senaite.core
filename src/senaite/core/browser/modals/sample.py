# -*- coding: utf-8 -*-

from six import string_types

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.browser.modals import Modal


class CreateWorksheetModal(Modal):
    """Modal form handler that allows to assign all analyses to a new worksheet
    """
    template = ViewPageTemplateFile("templates/create_worksheet.pt")

    def __init__(self, context, request):
        super(CreateWorksheetModal, self).__init__(context, request)

    def __call__(self):
        if self.request.form.get("submitted", False):
            return self.handle_submit(REQUEST=self.request)
        return self.template()

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)

    def get_selected_samples(self):
        """Return selected samples

        :returns: selected Samples
        """
        return map(api.get_object, self.uids)

    def handle_submit(self, REQUEST=None):
        """Extract categories from request and create worksheet
        """
        categories = self.request.form.get("categories")
        if isinstance(categories, string_types):
            categories = [categories]
        # filter out non-UIDs
        categories = filter(api.is_uid, categories)
        worksheet = self.create_worksheet_for(self.uids, categories)
        self.add_status_message(
            _("Created worksheet %s" % api.get_id(worksheet)), level="info")
        # redirect to the new worksheet
        return api.get_url(worksheet)

    def create_worksheet_for(self, samples, categories):
        """Create a new worksheet

        The new worksheet contains the analyses of all samples which match the
        are in the given categories

        :param samples: Sample obejects or UIDs
        :param categories: Category objects or UIDs
        :returns: new created Workshett
        """
        samples = map(api.get_object, samples)
        categories = map(api.get_object, categories)
        analyses = []
        for sample in samples:
            for analysis in sample.getAnalyses(full_objects=True):
                if analysis.getCategory() not in categories:
                    continue
                analyses.append(analysis)

        # create the new worksheet
        ws = api.create(self.worksheet_folder, "Worksheet")
        ws.setResultsLayout(self.worksheet_layout)
        ws.addAnalyses(analyses)
        return ws

    @property
    def worksheet_folder(self):
        """Return the worksheet root folder
        """
        portal = api.get_portal()
        return portal.restrictedTraverse("worksheets")

    @property
    def worksheet_layout(self):
        """Return the configured workheet layout
        """
        setup = api.get_setup()
        return setup.getWorksheetLayout()

    def get_analysis_categories(self):
        """Return analysis categories of the selected samples

        :returns: List available categories for the selected samples
        """
        categories = []
        for sample in self.get_selected_samples():
            for analysis in sample.getAnalyses(full_objects=True):
                # only consider unassigned analyses
                if api.get_workflow_status_of(analysis) != "unassigned":
                    continue
                # get the category of the analysis
                category = analysis.getCategory()
                if category in categories:
                    continue
                categories.append(category)

        categories = list(map(self.get_category_info,
                          sorted(categories, key=lambda c: c.getSortKey())))
        return categories

    def get_category_info(self, category):
        """Extract category information for template

        :returns: Dictionary of category information for the page template
        """
        return {
            "title": api.get_title(category),
            "uid": api.get_uid(category),
            "obj": category,
        }
