
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from bika.lims.browser import BrowserView


class EditView(BrowserView):

    template = ViewPageTemplateFile('templates/supplyorder_edit.pt')
    field = ViewPageTemplateFile('templates/row_field.pt')

    def __call__(self):
        request = self.request
        context = self.context
    	if 'submit' in request:
            context.processForm()
            portal_factory = getToolByName(context, 'portal_factory')
            portal_factory.doCreate(context, context.id)
            parent_url = context.aq_parent.absolute_url_path()
            request.response.redirect(parent_url + '/orders')
            return
        else:
        	self.orderDate = context.Schema()['OrderDate']
        	self.contact = context.Schema()['Contact']
        	return self.template()
