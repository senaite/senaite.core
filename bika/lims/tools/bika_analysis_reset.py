from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem
from Products.CMFCore import permissions
from Products.CMFCore.utils import UniqueObject, getToolByName
from bika.lims.config import ManageAnalysisRequests
from bika.lims.interfaces.tools import Ibika_analysis_reset
from bika.lims.tools import ToolFolder
from zope.interface import implements
import csv

class bika_analysis_reset(UniqueObject, SimpleItem):
    """ AnalysisResetTool """

    implements(Ibika_analysis_reset)

    security = ClassSecurityInfo()
    id = 'bika_analysis_reset'
    title = 'Analysis ResetTool'
    description = 'Resets Analysis Data.'
    meta_type = 'Analysis Reset Tool'

    security.declareProtected(ManageAnalysisRequests, 'import_file')
    def import_file(self, csvfile):
        msgs = []
        sfolder = self.bika_analysisservices

        reader = csv.reader(csvfile, delimiter = ',')
        analyses = []
        batch_headers = None
        counter = 0
        updated_price_counter = 0
        updated_cprice_counter = 0
        updated_both_counter = 0
        not_found_counter = 0
        dup_counter = 0
        invalid_counter = 0
        no_kw_counter = 0
        for row in reader:
            counter += 1
            if counter == 1:
                continue


            if len(row) > 2:
                keyword = row[2].strip()
            else:
                keyword = None

            if len(row) > 1:
                service = row[1]
            else:
                service = None
            if len(row) > 0:
                cat = row[0]
            else:
                cat = None

            if not keyword:
                msgs.append('%s %s %s: KeyWord required for identification' % (counter, cat, service))
                no_kw_counter += 1
                continue

            if len(row) > 5:
                new_cprice = row[5].strip()
                new_cprice = new_cprice.strip('$')
                if new_cprice:
                    try:
                        price = float(new_cprice)
                    except:
                        invalid_counter += 1
                        msgs.append('%s %s %s: bulk discount %s is not numeric - not updated' % (counter, cat, service, new_cprice))
                        continue
            else:
                new_cprice = None


            if len(row) > 4:
                new_price = row[4].strip()
                new_price = new_price.strip('$')
                if new_price:
                    try:
                        price = float(new_price)
                    except:
                        invalid_counter += 1
                        msgs.append('%s %s %s: price %s is not numeric - not updated' % (counter, cat, service, new_price))
                        continue
            else:
                new_price = None

            if not (new_price or new_cprice):
                continue

            s_proxies = self.portal_catalog(portal_type = 'AnalysisService',
                                            getKeyword = keyword)

            if len(s_proxies) > 1:
                msgs.append('%s %s %s: duplicate key %s' % (counter, cat, service, keyword))
                dup_counter += 1
                continue

            if len(s_proxies) < 1:
                not_found_counter += 1
                msgs.append('%s %s %s: analysis %s not found ' % (counter, cat, service, keyword))

            if len(s_proxies) == 1:
                service_obj = s_proxies[0].getObject()
                old_price = service_obj.getPrice()
                old_cprice = service_obj.getBulkPrice()
                price_change = False
                cprice_change = False
                if new_price:
                    if old_price != new_price:
                        price_change = True
                        service_obj.edit(Price = new_price)
                        msgs.append('%s %s %s %s price updated from %s to %s' % (counter, cat, service, keyword, old_price, new_price))

                if new_cprice:
                    if old_cprice != new_cprice:
                        cprice_change = True
                        service_obj.edit(BulkPrice = new_cprice)
                        msgs.append('%s %s %s %s bulk discount updated from %s to %s' % (counter, cat, service, keyword, old_cprice, new_cprice))

                if price_change and cprice_change:
                    updated_both_counter += 1
                elif price_change:
                    updated_price_counter += 1
                elif cprice_change:
                    updated_cprice_counter += 1



        msgs.append('____________________________________________________')
        msgs.append('%s services in input file' % (counter - 1))
        msgs.append('%s services without keyword - not updated' % (no_kw_counter))
        msgs.append('%s duplicate services - not updated' % (dup_counter))
        msgs.append('%s services not found - not updated' % (not_found_counter))
        msgs.append('%s service price and bulk discounts updated' % (updated_both_counter))
        msgs.append('%s service prices updated' % (updated_price_counter))
        msgs.append('%s service bulk discounts updated' % (updated_cprice_counter))
        return msgs

InitializeClass(bika_analysis_reset)
