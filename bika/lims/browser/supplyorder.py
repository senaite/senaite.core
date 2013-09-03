
from zope import event

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Archetypes.event import ObjectInitializedEvent

from bika.lims.browser import BrowserView
from bika.lims.utils import tmpID


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
            context = portal_factory.doCreate(context, context.id)
            # Process the order item data
            for k, v in request.form.items():
                if k.startswith('product_') and int(v) > 0:
                    k = k.replace('product_', '')
                    product = setup.bika_labproducts[k]
                    context.invokeFactory('SupplyOrderItem', k)
                    obj = context[k]
                    obj.edit(
                        Product=product,
                        Quantity=int(v),
                        Price='0.00',
                        VAT='0.00',
                    )
            # Redirect to the list of orders
            parent_url = context.aq_parent.absolute_url_path()
            request.response.redirect(parent_url + '/orders')
            return
        else:
            self.orderDate = context.Schema()['OrderDate']
            self.contact = context.Schema()['Contact']
            # Prepare the products
            self.products = ({
                'id': o.getId(),
                'title': o.Title(),
                'description': o.Description(),
                'volume': o.getVolume(),
                'unit': o.getUnit(),
                'price': o.getPrice(),
                'vat': "%s%%" % o.getVAT(),
            } for o in products)
            # Render the template
            return self.template()
