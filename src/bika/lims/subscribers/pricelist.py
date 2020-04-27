# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from persistent.mapping import PersistentMapping


class PricelistLineItem(PersistentMapping):
    pass


def apply_discount(price=None, discount=None):
    return float(price) - (float(price) * float(discount)) / 100


def get_vat_amount(price, vat_perc):
    return float(price) * float(vat_perc) / 100


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
                                         is_active=True):
            obj = p.getObject()
            itemDescription = None
            itemAccredited = False
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
                cat = None
                if obj.getPrice():
                    price = float(obj.getPrice())
                    totalprice = float(obj.getTotalPrice())
                    vat = totalprice - price
                else:
                    price = 0
                    totalprice = 0
                    vat = 0
            elif instance.getType() == "AnalysisService":

                if str(obj.getUnit()):
                    print_detail = " (" + str(obj.getUnit()) + ")"
                    itemTitle = obj.Title() + print_detail
                else:
                    itemTitle = obj.Title()
                itemAccredited = obj.getAccredited()

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
                    else:
                        totalprice = 0
                        price = 0
                        vat = 0

            if instance.getDescriptions():
                itemDescription = obj.Description()

            li = PricelistLineItem()
            li["title"] = itemTitle
            li["ItemDescription"] = itemDescription
            li["CategoryTitle"] = cat
            li["Accredited"] = itemAccredited
            li["Subtotal"] = "%0.2f" % price
            li["VATAmount"] = "%0.2f" % vat
            li["Total"] = "%0.2f" % totalprice
            instance.pricelist_lineitems.append(li)
