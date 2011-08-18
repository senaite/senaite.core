from Products.CMFCore.utils import getToolByName
from Products.validation.interfaces.IValidator import IValidator
from Products.validation import validation
from zope.interface import Interface, implements
from zope.site.hooks import getSite
from zExceptions import Redirect
from plone.memoize import instance
import sys,re
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('bika')

class ServiceKeywordValidator:
    """Validate a keyword against all service and interim field keywords.
    """

    if issubclass(IValidator, Interface):
        implements(IValidator)
    else:
        __implements__ = (IValidator, )

    name = "servicekeywordvalidator"

    def __call__(self, value, *args, **kwargs):
        instance = kwargs['instance']

        # check the value against all AnalysisService keywords
        pc = getToolByName(instance, 'portal_catalog')
        services = pc(portal_type='AnalysisService', getKeyword = value)
        for service in services:
            if service.UID != instance.UID():
                return instance.translate(
                    "message_keyword_is_not_unique",
                    default = "Keyword ${title} is used by ${used_by}.",
                    mapping = {'title': value, 'used_by': service.Title},
                    domain = "bika")

        # instance can be a calculation or a service
        # we just need the UID
        if instance.portal_type == 'AnalysisService':
            our_calc_uid = instance.getCalculation() and \
                     instance.getCalculation().UID() or ''
        else:
            our_calc_uid = instance.UID()

        # check the value against all Calculation Interim Field keywords
        calcs = [c for c in pc(portal_type='Calculation')]
        for calc in calcs:
            calc = calc.getObject()
            interim_fields = calc.getInterimFields()
            if not interim_fields: continue
            for field in interim_fields:
                if field['id'] == value and our_calc_uid != calc.UID():
                    return instance.translate(
                        "message_field_title_is_not_unique",
                        default = "Keyword ${title} is used by ${used_by}.",
                        mapping = {'title': value, 'used_by': calc.Title()},
                        domain = "bika")
        return True

validation.register(ServiceKeywordValidator())

class InterimFieldTitleValidator:

    if issubclass(IValidator, Interface):
        implements(IValidator)
    else:
        __implements__ = (IValidator, )

    name = "interimfieldtitlevalidator"

    def __call__(self, value, *args, **kwargs):
        instance = kwargs['instance']
        pc = getToolByName(instance, 'portal_catalog')
        calcs = (c.getObject() for c in pc(portal_type='Calculation'))
        for calc in calcs:
            interim_fields = calc.getInterimFields()
            if not interim_fields: continue
            for field in interim_fields:
                if field['title'] == value and instance.UID() != calc.UID():
                    return instance.translate(
                        "message_field_title_is_not_unique",
                        default = "Field Title '${title}' is used by ${used_by}.",
                        mapping = {'title': value, 'used_by': calc.Title()},
                        domain = "bika")
        return True

validation.register(InterimFieldTitleValidator())

class FormulaValidator:

    if issubclass(IValidator, Interface):
        implements(IValidator)
    else:
        __implements__ = (IValidator, )

    name = "formulavalidator"

    def __call__(self, value, *args, **kwargs):
        if not value:
            return True

        instance = kwargs['instance']
        pc = getToolByName(instance, 'portal_catalog')

        interim_keywords = [f['id'] for f in instance.getInterimFields()]
        keywords = re.compile(r"\%\(([^\)]+)\)").findall(value)

        for keyword in keywords:
            if not pc(getKeyword=keyword) and \
               not keyword in interim_keywords:
                return instance.translate(
                    "message_invalid_keyword",
                    default = "Keyword ${keyword} is invalid.",
                    mapping = {'keyword': keyword},
                    domain="bika")
        return True

validation.register(FormulaValidator())
