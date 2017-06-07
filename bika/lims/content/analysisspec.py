# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

"""Analysis result range specifications for a client
"""
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.Archetypes import atapi
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims import deprecated
from bika.lims.config import PROJECTNAME
from bika.lims.content.schema.analysisspec import schema
from bika.lims.interfaces import IAnalysisSpec
from zope.i18n import translate
from zope.interface import implements


class AnalysisSpec(BaseFolder, HistoryAwareMixin):
    implements(IAnalysisSpec)
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        """ Return the title if possible, else return the Sample type.
        Fall back on the instance's ID if there's no sample type or title.
        """
        if self.title:
            title = self.title
        else:
            sampletype = self.getSampleType()
            if sampletype:
                title = sampletype.Title()
            else:
                title = self.id
        return safe_unicode(title).encode('utf-8')

    def contextual_title(self):
        parent = self.aq_parent
        if parent == self.bika_setup.bika_analysisspecs:
            return self.title + " (" + translate(_("Lab")) + ")"
        else:
            return self.title + " (" + translate(_("Client")) + ")"

    security.declarePublic('getSpecCategories')

    def getSpecCategories(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        categories = []
        for spec in self.getResultsRange():
            keyword = spec['keyword']
            service = bsc(portal_type="AnalysisService",
                          getKeyword=keyword)
            if service.getCategoryUID() not in categories:
                categories.append(service.getCategoryUID())
        return categories

    security.declarePublic('getResultsRangeDict')

    def getResultsRangeDict(self):
        """
            Return a dictionary with the specification fields for each
            service. The keys of the dictionary are the keywords of each
            analysis service. Each service contains a dictionary in which
            each key is the name of the spec field:
            specs['keyword'] = {'min': value,
                                'max': value,
                                'error': value,
                                ... }
        """
        specs = {}
        subfields = self.Schema()['ResultsRange'].subfields
        for spec in self.getResultsRange():
            keyword = spec['keyword']
            specs[keyword] = {}
            for key in subfields:
                if key not in ['uid', 'keyword']:
                    specs[keyword][key] = spec.get(key, '')
        return specs

    security.declarePublic('getResultsRangeSorted')

    def getResultsRangeSorted(self):
        """
            Return an array of dictionaries, sorted by AS title:
             [{'category': <title of AS category>
               'service': <title of AS>,
               'id': <ID of AS>
               'uid': <UID of AS>
               'min': <min range spec value>
               'max': <max range spec value>
               'error': <error spec value>
               ...}]
        """
        tool = getToolByName(self, REFERENCE_CATALOG)

        cats = {}
        subfields = self.Schema()['ResultsRange'].subfields
        for spec in self.getResultsRange():
            service = tool.lookupObject(spec['uid'])
            service_title = service.Title()
            category_title = service.getCategoryTitle()
            if category_title not in cats:
                cats[category_title] = {}
            cat = cats[category_title]
            cat[service_title] = {'category': category_title,
                                  'service': service_title,
                                  'id': service.getId(),
                                  'uid': spec['uid'],
                                  'min': spec['min'],
                                  'max': spec['max'],
                                  'error': spec['error']}
            for key in subfields:
                if key not in ['uid', 'keyword']:
                    cat[service_title][key] = spec.get(key, '')
        cat_keys = cats.keys()
        cat_keys.sort(lambda x, y: cmp(x.lower(), y.lower()))
        sorted_specs = []
        for cat in cat_keys:
            services = cats[cat]
            service_keys = services.keys()
            service_keys.sort(lambda x, y: cmp(x.lower(), y.lower()))
            for service_key in service_keys:
                sorted_specs.append(services[service_key])
        return sorted_specs

    security.declarePublic('getRemainingSampleTypes')

    def getSampleTypes(self):
        """ return all sampletypes """
        sampletypes = []
        bsc = getToolByName(self, 'bika_setup_catalog')
        for st in bsc(portal_type='SampleType',
                      sort_on='sortable_title'):
            sampletypes.append((st.UID, st.Title))

        return DisplayList(sampletypes)

    @deprecated('[1703] Orphan. No alternative')
    def getAnalysisSpecsStr(self, keyword):
        specstr = ''
        specs = self.getResultsRangeDict()
        if keyword in specs.keys():
            specs = specs[keyword]
            smin = specs.get('min', '')
            smax = specs.get('max', '')
            if smin and smax:
                specstr = '%s - %s' % (smin, smax)
            elif smin:
                specstr = '> %s' % specs['min']
            elif smax:
                specstr = '< %s' % specs['max']
        return specstr

    def getClientUID(self):
        return self.aq_parent.UID()


atapi.registerType(AnalysisSpec, PROJECTNAME)
