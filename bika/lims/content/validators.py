from Products.CMFCore.utils import getToolByName
from Products.validation.ZService import ZService as Service
from Products.validation.interfaces.IValidator import IValidator
from zope.interface import implements
from zope.site.hooks import getSite
from zExceptions import Redirect
from plone.memoize import instance
import sys,re

validation = Service()

class ServiceKeywordValidator:
    implements(IValidator)
    name = "service_keyword_validator"
    title = "Interim Field ID/Service Keyword Validator"
    description = "Interim Field IDs aand service Keywords must be unique."
    def __call__(self, value, *args, **kwargs):
        """return True if valid, error string if not"""
        pc = getSite().portal_catalog
        services = pc(portal_type='AnalysisService', getKeyword = value)
        if services and services[0].UID() != self.UID():
            return self.context.translate(
                "message_keyword_is_not_unique",
                default = "Keyword {$keyword} is in use.",
                mapping = {'keyword': value},
                domain = "bika")
        return True
service_keyword_validator = ServiceKeywordValidator()
validation.register(service_keyword_validator)

class InterimFieldTitleValidator:
    implements(IValidator)
    name = "interim_field_title_validator"
    title = "Interim Field Title Validator"
    description = "Interim field Titles may not be the same as an AnalysisService Keyword."
    def __call__(self, value, *args, **kwargs):
        pc = getSite().portal_catalog
        service = [s for s in pc(portal_type='AnalysisService') if s.getKeyword == value]
        if service:
            return "Interim field ID '%s' is the same as Analysis Service Keyword from '%s'"%\
                   (value, service[0].Title)
        return True
interim_field_title_validator = InterimFieldTitleValidator()
validation.register(interim_field_title_validator)

class FormulaValidator:
    implements(IValidator)
    name = "formula_validator"
    title = "Validate existence of keywords in Formula."
    description = "Scans against all service Keywords and InterimFields for this calculation."
    def __call__(self, value, *args, **kwargs):
        if not value:
            self.setDependentServices(None)
        else:
            pc = getToolByName(self, "portal_catalog")
            interim_keywords = [f['id'] for f in self.getInterimFields()]
            keywords = re.compile(r"\%\(([^\)]+)\)").findall(Formula)
            for keyword in keywords:
                if not pc(getKeyword == keyword) and \
                   not keyword in interim_keywords:
                    return self.translate(
                        "message_keyword_is_not_unique",
                        default = "Keyword {$keyword} is in use.",
                        mapping = {'keyword': keyword},
                        domain="bika")
        return True
formula_validator = FormulaValidator()
validation.register(formula_validator)
