# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

"""ReferenceSample represents a reference sample used for quality control 
testing
"""

from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from bika.lims import bikaMessageFactory as _
from bika.lims.config import PROJECTNAME
from bika.lims.content.schema.referencesample import schema
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import IReferenceSample
from bika.lims.utils import t
from bika.lims.utils import tmpID
from bika.lims.utils import to_unicode as _u
from zope.interface import implements


class ReferenceSample(BaseFolder):
    implements(IReferenceSample)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    security.declarePublic('current_date')

    def current_date(self):
        return DateTime()

    def getReferenceDefinitions(self):

        def make_title(s):
            # the javascript uses these strings to decide if it should
            # check the blank or hazardous checkboxes when a reference
            # definition is selected (./js/referencesample.js)
            if not s:
                return ''
            title = _u(s.Title())
            if s.getBlank():
                title += " %s" % t(_('(Blank)'))
            if s.getHazardous():
                title += " %s" % t(_('(Hazardous)'))

            return title

        bsc = getToolByName(self, 'bika_setup_catalog')
        brains = bsc(portal_type='ReferenceDefinition', inactive_state='active')
        defs = [b.getObject() for b in brains]
        items = [('', '')] + [(d.UID(), make_title(d)) for d in defs]
        definition = self.getReferenceDefinition()
        it = make_title(definition)
        if definition and (definition.UID(), it) not in items:
            items.append((definition.UID(), it))
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    def getManufacturers(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        mans = bsc(portal_type='Manufacturer', inactive_state='active')
        items = [('', '')] + [(m.UID, m.Title) for m in mans]
        definition = self.getReferenceDefinition()
        if definition and definition.UID() not in [i[0] for i in items]:
            items.append((definition.UID(), definition.Title()))
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    security.declarePublic('getSpecCategories')

    def getSpecCategories(self):
        tool = getToolByName(self, REFERENCE_CATALOG)
        categories = []
        for spec in self.getReferenceResults():
            service = tool.lookupObject(spec['uid'])
            if service.getCategoryUID() not in categories:
                categories.append(service.getCategoryUID())
        return categories

    security.declarePublic('getResultsRangeDict')

    def getResultsRangeDict(self):
        specs = {}
        for spec in self.getReferenceResults():
            uid = spec['uid']
            specs[uid] = {}
            specs[uid]['result'] = spec['result']
            specs[uid]['min'] = spec.get('min', '')
            specs[uid]['max'] = spec.get('max', '')
            specs[uid]['error'] = 'error' in spec and spec['error'] or 0
        return specs

    security.declarePublic('getResultsRangeSorted')

    def getResultsRangeSorted(self):
        tool = getToolByName(self, REFERENCE_CATALOG)

        cats = {}
        for spec in self.getReferenceResults():
            service = tool.lookupObject(spec['uid'])
            service_title = service.Title()
            category = service.getCategoryTitle()
            if category not in cats:
                cats[category] = {}

            cat = cats[category]
            cat[service_title] = {
                'category': category,
                'service': service_title,
                'id': service.getId(),
                'unit': service.getUnit(),
                'result': spec['result'],
                'min': spec.get('min', ''),
                'max': spec.get('max', ''),
                'error': spec['error']}

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

    security.declarePublic('getReferenceAnalyses')

    def getReferenceAnalyses(self):
        """ return all analyses linked to this reference sample """
        return self.objectValues('ReferenceAnalysis')

    security.declarePublic('getReferenceAnalysesService')

    def getReferenceAnalysesService(self, service_uid):
        """ return all analyses linked to this reference sample for a service 
        """
        analyses = []
        for analysis in self.objectValues('ReferenceAnalysis'):
            if analysis.getServiceUID() == service_uid:
                analyses.append(analysis)
        return analyses

    security.declarePublic('getReferenceResult')

    def getReferenceResult(self, service_uid):
        """ Return an array [result, min, max, error] with the desired result
            for a specific service.
            If any reference result found, returns None.
            If no value found for result, min, max, error found returns None
            If floatable value, sets the value in array as floatable, otherwise
            sets the raw value for that spec key
            in its array position
        """
        for spec in self.getReferenceResults():
            if spec['uid'] == service_uid:
                found = False
                outrefs = []
                specitems = ['result', 'min', 'max', 'error']
                for item in specitems:
                    if item in spec:
                        outrefs.append(spec[item])
                        found = True
                    else:
                        outrefs.append(None)
                return found and outrefs or None
        return None

    security.declarePublic('addReferenceAnalysis')

    def addReferenceAnalysis(self, service_uid, reference_type):
        """
        Creates a new Reference Analysis object based on this Sample
        Reference, with the type passed in and associates the newly
        created object to the Analysis Service passed in.

        :param service_uid: The UID of the Analysis Service to be associated 
        to the newly created Reference Analysis
        :type service_uid: A string
        :param reference_type: type of ReferenceAnalysis, where 'b' is is  
        Blank and 'c' is Control
        :type reference_type: A String
        :returns: the UID of the newly created Reference Analysis
        :rtype: string
        """
        rc = getToolByName(self, REFERENCE_CATALOG)
        service = rc.lookupObject(service_uid)
        calc = service.getCalculation()
        interim_fields = calc.getInterimFields() if calc else None
        interim_fields = interim_fields if interim_fields else []
        analysis = _createObjectByType("ReferenceAnalysis", self, id=tmpID())
        analysis.setAnalysisService(service_uid)
        analysis.setReferenceType(reference_type)
        analysis.setInterimFields(interim_fields)
        analysis.unmarkCreationFlag()
        renameAfterCreation(analysis)
        return analysis.UID()

    security.declarePublic('getServices')

    def getServices(self):
        """ get all services for this Sample """
        tool = getToolByName(self, REFERENCE_CATALOG)
        services = []
        for spec in self.getReferenceResults():
            service = tool.lookupObject(spec['uid'])
            services.append(service)
        return services

    security.declarePublic('getReferenceResultStr')

    def getReferenceResultStr(self, service_uid):
        specstr = ''
        specs = self.getReferenceResult(service_uid)
        if specs:
            # [result, min, max, error]
            if not specs[0]:
                if specs[1] and specs[2]:
                    specstr = '%s - %s' % (specs[1], specs[2])
                elif specs[1]:
                    specstr = '> %s' % (specs[1])
                elif specs[2]:
                    specstr = '< %s' % (specs[2])
            elif specs[0]:
                if specs[3] and specs[3] != 0:
                    specstr = '%s (%s%%)' % (specs[0], specs[3])
                else:
                    specstr = specs[0]
        return specstr

    # XXX workflow methods
    def workflow_script_expire(self):
        """ expire sample """
        self.setDateExpired(DateTime())
        self.reindexObject()

    def workflow_script_dispose(self):
        """ dispose sample """
        self.setDateDisposed(DateTime())
        self.reindexObject()


registerType(ReferenceSample, PROJECTNAME)
