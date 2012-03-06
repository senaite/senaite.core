from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem
from Products.CMFCore import permissions
from Products.CMFCore.utils import UniqueObject, getToolByName
from bika.lims.config import ManageAnalysisRequests
from bika.lims.tools import ToolFolder
import csv
from bika.lims.interfaces.tools import Ibika_instrument_import
from zope.interface import implements

class bika_instrument_import(UniqueObject, SimpleItem):
    """ InstrumentImportTool """

    implements(Ibika_instrument_import)

    security = ClassSecurityInfo()
    id = 'bika_instrument_import'
    title = 'Instrument Import Tool'
    description = 'Imports Instrument Data.'
    meta_type = 'Instrument Import Tool'

    security.declareProtected(ManageAnalysisRequests, 'import_file')
    def import_file(self, csvfile):
        workflow = getToolByName(self, 'portal_workflow')
        prefixes = self.bika_setup.getPrefixes()
        ws_prefix = 'WS-'
        for d in prefixes:
            if d['portal_type'] == 'Worksheet':
                ws_prefix = d['prefix']
                break

        updateable_states = ['sample_received', 'assigned', 'open']
        reader = csv.reader(csvfile)
        samples = []
        batch_headers = None
        for row in reader:
            if not row: continue
            # a new batch starts
            if row[0] == 'Sample Id':
                headers = ['SampleID'] + row[5:]
                batch_headers = [x.strip() for x in headers]
                continue

            if not batch_headers: continue

            r = dict(zip(batch_headers, [row[0].strip()] + row[5:]))
            samples.append(r)

        results = {}
        ids = []
        map = self.getInstrumentKeywordToServiceIdMap()
        for sample in samples:
            sample_id = sample['SampleID']
            ids.append(sample_id)
            results[sample_id] = {}
            results[sample_id]['analyses'] = []
            results[sample_id]['errors'] = []
            results[sample_id]['added'] = []
            worksheet = False
            if sample_id[0:3] == ws_prefix:
                worksheet = True
                ws_id = sample_id.split('/')[0]
                pos = sample_id.split('/')[1]
            if worksheet:   # this is a worksheet
                r = self.portal_catalog(portal_type = 'Worksheet',
                    id = ws_id)
                if len(r) == 0:
                    results[sample_id]['errors'].append('Not found')
                    continue
                ws = r[0].getObject()
                ws_state = workflow.getInfoFor(ws, 'review_state', '')
                if (ws_state not in updateable_states):
                    results[sample_id]['errors'].append('Worksheet in %s status '
                               '- not updated' % (ws_state))
                    continue
                these_analyses = ws.getPosAnalyses(pos)
                ws_analyses = {}
                for analysis in these_analyses:
                    ws_analyses[analysis.getService().getId()] = analysis
                these_service_ids = ws_analyses.keys()
            else:          # Analysis Request
                r = self.portal_catalog(portal_type = 'AnalysisRequest',
                    id = sample_id)
                if len(r) == 0:
                    results[sample_id]['errors'].append('Not found')
                    continue
                ar = r[0].getObject()
                ar_state = workflow.getInfoFor(ar, 'review_state', '')
                if (ar_state not in updateable_states):
                    results[sample_id]['errors'].append('Analysis request in %s status '
                               '- not updated' % (ar_state))
                    continue
                these_service_ids = ar.objectIds()

            for keyword, result in sample.items():
                if result == '':
                    continue
                if keyword == 'SampleID':
                    continue
                if map.has_key(keyword):
                    service_id = map[keyword]
                else:
                    results[sample_id]['errors'].append('Instrument keyword %s not found' % (keyword))
                    continue

                service = self.bika_analysisservices._getOb(service_id)
                service_title = service.Title()
                analysis = None
                if service_id in these_service_ids:
                    if worksheet:
                        analysis = ws_analyses[service_id]
                    else:
                        analysis = ar._getOb(service_id)
                    as_state = workflow.getInfoFor(analysis, 'review_state', '')
                    if (as_state in ['assigned']):
                        if (analysis.getResult() is None) or (analysis.getResult() == ''):
                            pass
                        else:
                            results[sample_id]['errors'].append('%s has a result - not updated' % (service_title))
                            continue


                    if (as_state not in updateable_states):
                        results[sample_id]['errors'].append('%s in %s status '
                                   '- not updated' % (service_title, as_state))
                        continue
                    results[sample_id]['analyses'].append(service_title)
                else:
                    if worksheet:
                        # this is an error
                        results[sample_id]['errors'].append('%s not found' % (service_title))

                    else:
                        # create the analysis and set its status to 'not
                        # requested'
                        ar.invokeFactory(
                            id = service.id, type_name = 'Analysis')
                        analysis = ar._getOb(service_id)
                        discount = ar.getMemberDiscount()
                        if ar.getMemberDiscountApplies():
                            price = service.getDiscountedPrice()
                            totalprice = service.getTotalDiscountedPrice()
                        else:
                            price = service.getPrice()
                            totalprice = service.getTotalPrice()

                        analysis.edit(
                            Service = service,
                            Price = price,
                            Discount = discount,
                            VAT = service.getVAT(),
                            TotalPrice = totalprice,
                            Unit = service.getUnit(),
                        )
                        self.REQUEST.set('suppress_escalation', 1)
                        workflow.doActionFor(analysis, 'import')
                        del self.REQUEST.other['suppress_escalation']
                        results[sample_id]['added'].append('%s' % (service_title))

                if analysis:
                    analysis.setUncertainty(self.get_uncertainty(result, service))
                    analysis.setResult(result)
                    # set dummy titration values if required
                    if analysis.getCalcType() == 't':
                        analysis.setTitrationVolume(result)
                        analysis.setTitrationFactor('1')
                    analysis.processForm()

        results_ids = {}
        results_ids['results'] = results
        results_ids['ids'] = ids
        return results_ids

    def getInstrumentKeywordToServiceIdMap(self):
        d = {}
        for p in self.portal_catalog(portal_type = 'AnalysisService'):
            obj = p.getObject()
            keyword = obj.getInstrumentKeyword()
            if keyword:
                d[keyword] = obj.getId()
        return d

InitializeClass(bika_instrument_import)
