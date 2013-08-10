from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from bika.lims.browser import BrowserView


class EditView(BrowserView):

    template = ViewPageTemplateFile('templates/supplyorder_edit.pt')

    def __call__(self):
    	return self.template()
