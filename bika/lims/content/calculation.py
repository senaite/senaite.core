# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

import math
import re

import transaction
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.Archetypes.ArchetypeTool import registerType
from Products.Archetypes.BaseFolder import BaseFolder
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims.config import PROJECTNAME
from bika.lims.content.schema.calculation import schema
from bika.lims.interfaces import ICalculation
from zope.interface import implements


class Calculation(BaseFolder, HistoryAwareMixin):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema
    implements(ICalculation)

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def setInterimFields(self, value):
        new_value = []

        for x in range(len(value)):
            row = dict(value[x])
            keys = row.keys()
            if 'value' not in keys:
                row['value'] = 0
            new_value.append(row)

        self.getField('InterimFields').set(self, new_value)

    def setFormula(self, Formula=None):
        """Set the Dependent Services from the text of the calculation Formula
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        if Formula is None:
            self.setDependentServices(None)
            self.getField('Formula').set(self, Formula)
        else:
            DependentServices = []
            keywords = re.compile(r"\[([^\]]+)\]").findall(Formula)
            for keyword in keywords:
                service = bsc(portal_type="AnalysisService",
                              getKeyword=keyword)
                if service:
                    DependentServices.append(service[0].getObject())

            self.getField('DependentServices').set(self, DependentServices)
            self.getField('Formula').set(self, Formula)

    def getMinifiedFormula(self):
        """Return the current formula value as text.
        The result will have newlines and additional spaces stripped out.
        """
        value = " ".join(self.getFormula().splitlines())
        return value

    def getMappedFormula(self, analysis, mapping):
        formula = self.getMinifiedFormula()
        # XXX regex groups to replace only [x] where x in interim keys.
        keywords = re.compile(r"\[([^\]]+)\]").findall(formula)
        for keyword in keywords:
            if keyword in mapping:
                try:
                    formula = formula.replace('[%s]' % keyword,
                                              '%f' % mapping[keyword])
                except TypeError:
                    formula = formula.replace('[%s]' % keyword,
                                              '"%s"' % mapping[keyword])

        mapped = eval("'%s'%%mapping" % formula,
                      {"__builtins__": locals()['__builtins__'],
                       'math': math,
                       'context': analysis},
                      {'mapping': mapping})

        print analysis, mapped, mapping
        return mapped

    def getCalculationDependencies(self, flat=False, deps=None):
        """ Recursively calculates all dependencies of this calculation.
            The return value is dictionary of dictionaries (of dictionaries....)

            {service_UID1:
                {service_UID2:
                    {service_UID3: {},
                     service_UID4: {},
                    },
                },
            }

            set flat=True to get a simple list of AnalysisService objects
        """
        if deps is None:
            deps = [] if flat else {}

        for service in self.getDependentServices():
            calc = service.getCalculation()
            if calc:
                calc.getCalculationDependencies(flat, deps)
            if flat:
                deps.append(service)
            else:
                deps[service.UID()] = {}
        return deps

    def getCalculationDependants(self):
        """Return a flat list of services who's calculations depend on this."""
        deps = []
        for service in self.getBackReferences('AnalysisServiceCalculation'):
            calc = service.getCalculation()
            if calc and calc.UID() != self.UID():
                calc.getCalculationDependants(deps)
            deps.append(service)
        return deps

    def workflow_script_activate(self):
        wf = getToolByName(self, 'portal_workflow')
        pu = getToolByName(self, 'plone_utils')
        # A calculation cannot be re-activated if services it depends on
        # are deactivated.
        services = self.getDependentServices()
        inactive_services = []
        for service in services:
            if wf.getInfoFor(service, "inactive_state") == "inactive":
                inactive_services.append(service.Title())
        if inactive_services:
            msg = _("Cannot activate calculation, because the following "
                    "service dependencies are inactive: ${inactive_services}",
                    mapping={'inactive_services': safe_unicode(
                        ", ".join(inactive_services))})
            pu.addPortalMessage(msg, 'error')
            transaction.get().abort()
            raise WorkflowException

    def workflow_script_deactivate(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        pu = getToolByName(self, 'plone_utils')
        # A calculation cannot be deactivated if active services are using it.
        services = bsc(portal_type="AnalysisService", inactive_state="active")
        calc_services = []
        for service in services:
            service = service.getObject()
            calc = service.getCalculation()
            if calc and calc.UID() == self.UID():
                calc_services.append(service.Title())
        if calc_services:
            msg = _(
                'Cannot deactivate calculation, because it is in use by the '
                'following services: ${calc_services}',
                mapping={
                    'calc_services': safe_unicode(", ".join(calc_services))})
            pu.addPortalMessage(msg, 'error')
            transaction.get().abort()
            raise WorkflowException


registerType(Calculation, PROJECTNAME)
