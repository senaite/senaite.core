from Products.CMFCore.utils import getToolByName
from Products.validation.interfaces.IValidator import IValidator
from zope.interface import implements
from zope.site.hooks import getSite
from zExceptions import Redirect
from plone.memoize import instance
import sys,re
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('bika')

class ServiceKeywordValidator:
    implements(IValidator)
    def __init__(self, name):
        self.name = name
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

class InterimFieldTitleValidator:
    implements(IValidator)
    def __init__(self, name):
        self.name = name
    def __call__(self, value, *args, **kwargs):
        pc = getSite().portal_catalog
        service = [s for s in pc(portal_type='AnalysisService') if s.getKeyword == value]
        if service:
            return "Interim field ID '%s' is the same as Analysis Service Keyword from '%s'"%\
                   (value, service[0].Title)
        return True

class FormulaValidator:
    implements(IValidator)
    def __init__(self, name):
        self.name = name
    def __call__(self, value, *args, **kwargs):
        if not value:
            self.setDependentServices(None)
            return True
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
