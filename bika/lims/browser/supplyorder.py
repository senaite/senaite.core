from Products.CMFPlone.utils import _createObjectByType
from zope import event

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.utils import t


class View(BrowserView):

    template = ViewPageTemplateFile('templates/supplyorder_view.pt')
    content = ViewPageTemplateFile('templates/supplyorder_content.pt')
    currency_td = ViewPageTemplateFile('templates/currency_td.pt')
    title = _('Supply Order')

    def __call__(self):
        context = self.context
        # Disable the add new menu item
        context.setConstrainTypesMode(1)
        context.setLocallyAllowedTypes(())
        # Collect general data
        self.orderDate = self.ulocalized_time(context.getOrderDate())
        self.contact = context.getContact()
        self.contact = self.contact.getFullname() if self.contact else ''
        self.subtotal = '%.2f' % context.getSubtotal()
        self.vat = '%.2f' % context.getVATAmount()
        self.total = '%.2f' % context.getTotal()
        # Set the title
        self.title = context.Title()
        # Collect order item data
        items = context.objectValues('SupplyOrderItem')
        self.items = []
        for item in items:
            product = item.getProduct()
            self.items.append({
                'title': product.Title(),
                'description': product.Description(),
                'volume': product.getVolume(),
                'unit': product.getUnit(),
                'price': product.getPrice(),
                'vat': '%s%%' % product.getVATAmount(),
                'quantity': item.getQuantity(),
                'totalprice': '%.2f' % item.getTotal(),
            })
        # Render the template
        return self.template()


class EditView(BrowserView):

    template = ViewPageTemplateFile('templates/supplyorder_edit.pt')
    field = ViewPageTemplateFile('templates/row_field.pt')
    currency_td = ViewPageTemplateFile('templates/currency_td.pt')

    def __call__(self):
        portal = self.portal
        request = self.request
        context = self.context
        setup = portal.bika_setup
        # Allow adding items to this context
        context.setConstrainTypesMode(0)
        # Collect the products
        products = setup.bika_labproducts.objectValues('LabProduct')
        # Handle for submission and regular request
    	if 'submit' in request:
            portal_factory = getToolByName(context, 'portal_factory')
            context = portal_factory.doCreate(context, context.id)
            context.processForm()
            # Process the order item data
            for k, v in request.form.items():
                if k.startswith('product_') and int(v) > -1:
                    k = k.replace('product_', '')
                    product = setup.bika_labproducts[k]
                    # Create a item if it doesn't yet exist
                    if k not in context:
                        _createObjectByType("SupplyOrderItem", context, k)
                    # Fetch and edit the item
                    obj = context[k]
                    obj.edit(
                        Product=product,
                        Quantity=int(v),
                        Price=product.getPrice(),
                        VAT=product.getVAT(),
                    )
            # Redirect to the list of orders
            obj_url = context.absolute_url_path()
            request.response.redirect(obj_url)
            return
        else:
            self.orderDate = context.Schema()['OrderDate']
            self.contact = context.Schema()['Contact']
            self.subtotal = '%.2f' % context.getSubtotal()
            self.vat = '%.2f' % context.getVATAmount()
            self.total = '%.2f' % context.getTotal()
            # Prepare the products
            items = context.objectValues('SupplyOrderItem')
            self.products = []
            for product in products:
                item = [o for o in items if o.getProduct() == product]
                quantity = item[0].getQuantity() if len(item) > 0 else 0
                total = item[0].getTotal() if len(item) > 0 else '0.00'
                self.products.append({
                    'id': product.getId(),
                    'title': product.Title(),
                    'description': product.Description(),
                    'volume': product.getVolume(),
                    'unit': product.getUnit(),
                    'price': product.getPrice(),
                    'vat': '%s%%' % product.getVAT(),
                    'quantity': quantity,
                    'total': total,
                })
            # Render the template
            return self.template()


class PrintView(View):

    template = ViewPageTemplateFile('templates/supplyorder_print.pt')

    def __call__(self):
        return View.__call__(self)
