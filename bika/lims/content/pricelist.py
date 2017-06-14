# -*- coding: utf-8 -*-
# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFCore import permissions
from bika.lims.config import PROJECTNAME
from bika.lims.content.schema.pricelist import schema
from bika.lims.interfaces import IPricelist
from persistent.mapping import PersistentMapping
from plone.app.folder import folder
from zope.interface import implements


def apply_discount(price=None, discount=None):
    return float(price) - (float(price) * float(discount)) / 100


def get_vat_amount(price, vat_perc):
    return float(price) * float(vat_perc) / 100


class PricelistLineItem(PersistentMapping):
    pass


class Pricelist(folder.ATFolder):
    implements(IPricelist)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    security.declarePublic('current_date')

    def current_date(self):
        """ return current date """
        return DateTime()

    security.declareProtected(permissions.ModifyPortalContent,
                              'processForm')


registerType(Pricelist, PROJECTNAME)


# noinspection PyUnusedLocal
def ObjectModifiedEventHandler(instance, event):
    """ Various types need automation on edit.
    """
    if not hasattr(instance, 'portal_type'):
        return

    if instance.portal_type == 'Pricelist':
        """ Create price list line items
        """
        # Remove existing line items
        instance.pricelist_lineitems = []
        for p in instance.portal_catalog(portal_type=instance.getType(),
                                         inactive_state="active"):
            obj = p.getObject()
            itemDescription = None
            itemAccredited = False
            itemTitle = ''
            cat = None
            price = 0
            vat = 0
            totalprice = 0
            if instance.getType() == "LabProduct":
                print_detail = ""
                if obj.getVolume():
                    print_detail = print_detail + str(obj.getVolume())
                if obj.getUnit():
                    print_detail = print_detail + str(obj.getUnit())
                if obj.getVolume() or obj.getUnit():
                    print_detail = " (" + print_detail + ")"
                    itemTitle = obj.Title() + print_detail
                else:
                    itemTitle = obj.Title()
                if obj.getPrice():
                    price = float(obj.getPrice())
                    totalprice = float(obj.getTotalPrice())
                    vat = totalprice - price
            elif instance.getType() == "AnalysisService":
                #
                if str(obj.getUnit()):
                    print_detail = " (" + str(obj.getUnit()) + ")"
                    itemTitle = obj.Title() + print_detail
                else:
                    itemTitle = obj.Title()
                itemAccredited = obj.getAccredited()
                #
                cat = obj.getCategoryTitle()
                if instance.getBulkDiscount():
                    price = float(obj.getBulkPrice())
                    vat = get_vat_amount(price, obj.getVAT())
                    totalprice = price + vat
                else:
                    if instance.getBulkPrice():
                        discount = instance.getBulkPrice()
                        price = float(obj.getPrice())
                        price = apply_discount(price, discount)
                        vat = get_vat_amount(price, obj.getVAT())
                        totalprice = price + vat
                    elif obj.getPrice():
                        price = float(obj.getPrice())
                        vat = get_vat_amount(price, obj.getVAT())
                        totalprice = price + vat

            if instance.getDescriptions():
                itemDescription = obj.Description()

            li = PricelistLineItem()
            li['title'] = itemTitle
            li['ItemDescription'] = itemDescription
            li['CategoryTitle'] = cat
            li['Accredited'] = itemAccredited
            li['Subtotal'] = "%0.2f" % price
            li['VATAmount'] = "%0.2f" % vat
            li['Total'] = "%0.2f" % totalprice
            instance.pricelist_lineitems.append(li)
