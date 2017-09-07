from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.browser import BrowserView
from bika.lims import logger
from bika.lims.databasesanitize.analyses import analyses_creation_date_recover


class ControllerView(BrowserView):
    """
    This class is the controller for the sanitize view. Sanitize view
    """
    template = ViewPageTemplateFile("templates/main_template.pt")

    def __call__(self):
        # Need to generate a PDF with the stickers?
        if self.request.form.get('analysis_date', '0') == '1':
            logger.info("Starting sanitation process 'Analyses creation "
                        "date recover'...")
            analyses_creation_date_recover()

        return self.template()


