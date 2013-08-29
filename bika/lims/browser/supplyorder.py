
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from bika.lims.browser import BrowserView


class EditView(BrowserView):

    template = ViewPageTemplateFile('templates/supplyorder_edit.pt')
    field = ViewPageTemplateFile('templates/row_field.pt')

    def __call__(self):
        portal = self.portal
        request = self.request
        context = self.context
        setup = portal.bika_setup
        # Collect the products
        products = setup.bika_labproducts.objectValues('LabProduct')
        # Handle for submission and regular request
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
            # Prepare the products
            self.products = ({
                'title': o.Title(),
                'description': o.Description(),
                'volume': o.getVolume(),
                'unit': o.getUnit(),
                'price': o.getPrice(),
            } for o in products)
            # Render the template
            return self.template()
