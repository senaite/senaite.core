from Products.CMFPlone.utils import _createObjectByType
from zope import event

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from operator import itemgetter, methodcaller

from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.utils import t


class View(BrowserView):

    template = ViewPageTemplateFile('templates/supplyorder_view.pt')
    title = _('Supply Order')

    def __call__(self):
        context = self.context
        portal = self.portal
        setup = portal.bika_setup
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
        items = context.supplyorder_lineitems

        self.items = []
        for item in items:
            prodid = item['Product']
            product = setup.bika_labproducts[prodid]
            price = float(item['Price'])
            vat = float(item['VAT'])
            qty = float(item['Quantity'])
            self.items.append({
                'title': product.Title(),
                'description': product.Description(),
                'volume': product.getVolume(),
                'unit': product.getUnit(),
                'price': price,
                'vat': '%s%%' % vat,
                'quantity': qty,
                'totalprice': '%.2f' % (price * qty)
            })
        self.items = sorted(self.items, key = itemgetter('title')) 
        # Render the template
        return self.template()

    def getPreferredCurrencyAbreviation(self):
        return self.context.bika_setup.getCurrency()


class EditView(BrowserView):

    template = ViewPageTemplateFile('templates/supplyorder_edit.pt')
    field = ViewPageTemplateFile('templates/row_field.pt')

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
            # Clear the old line items
            context.supplyorder_lineitems = []
            # Process the order item data
            for prodid, qty in request.form.items():
                if prodid.startswith('product_') and float(qty) > 0:
                    prodid = prodid.replace('product_', '')
                    product = setup.bika_labproducts[prodid]
                    context.supplyorder_lineitems.append(
                            {'Product': prodid,
                             'Quantity': qty,
                             'Price': product.getPrice(),
                             'VAT': product.getVAT()})

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
            items = context.supplyorder_lineitems
            self.products = []
            products = sorted(products, key = methodcaller('Title'))
            for product in products:
                item = [o for o in items if o['Product'] == product.getId()]
                quantity = item[0]['Quantity'] if len(item) > 0 else 0
                self.products.append({
                    'id': product.getId(),
                    'title': product.Title(),
                    'description': product.Description(),
                    'volume': product.getVolume(),
                    'unit': product.getUnit(),
                    'price': product.getPrice(),
                    'vat': '%s%%' % product.getVAT(),
                    'quantity': quantity,
                    'total': (float(product.getPrice()) * float(quantity)),
                })
            # Render the template
            return self.template()

    def getPreferredCurrencyAbreviation(self):
        return self.context.bika_setup.getCurrency()


class PrintView(View):

    template = ViewPageTemplateFile('templates/supplyorder_print.pt')

    def __call__(self):
        return View.__call__(self)
