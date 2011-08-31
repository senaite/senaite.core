from Products.CMFCore.utils import getToolByName
from Products.validation.interfaces.IValidator import IValidator
from Products.validation import validation
from bika.lims.utils import sortable_title
from zope.interface import Interface, implements
from zope.site.hooks import getSite
from zExceptions import Redirect
from plone.memoize import instance
import sys,re
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('bika')

class UniqueTitleValidator:
    """ Verifies that an item's sortable_title is not the same as any
    other object of the same type """

    if issubclass(IValidator, Interface):
        implements(IValidator)
    else:
        __implements__ = (IValidator, )

    name = "uniquetitlevalidator"

    def __call__(self, value, *args, **kwargs):
        instance = kwargs['instance']
        pc = getToolByName(instance, 'portal_catalog')
        items = pc(portal_type=instance.portal_type,
                   sortable_title = sortable_title(instance, value))
        for item in items:
            if item.UID != instance.UID():
                return instance.translate(
                    "message_title_is_not_unique",
                    default = "Validation failed(UniqueTitleValidator): '${title}': this name is already in use.",
                    mapping = {'title': value},
                    domain = "bika")
        return True

validation.register(UniqueTitleValidator())

class ServiceKeywordValidator:
    """Validate Service Keywords
    may not be the same as another service keyword
    may not be the same as any InterimField id.
    """

    if issubclass(IValidator, Interface):
        implements(IValidator)
    else:
        __implements__ = (IValidator, )

    name = "servicekeywordvalidator"

    def __call__(self, value, *args, **kwargs):
        instance = kwargs['instance']

        # make sure the keyword is a valid content id
        if not re.match(r"^[A-Za-z\w\d\-\_]+$", value):
            return instance.translate(
                "message_invalid_keyword",
                default = "Keyword '${keyword}' is invalid. Only letters, numbers, spaces, _ and - are allowed.",
                mapping = {'keyword': value},
                domain="bika")

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

        our_calc_uid = instance.getCalculation() and \
                 instance.getCalculation().UID() or ''

        # check the value against all Calculation Interim Field ids
        calcs = [c for c in pc(portal_type='Calculation')]
        for calc in calcs:
            calc = calc.getObject()
            interim_fields = calc.getInterimFields()
            if not interim_fields: continue
            for field in interim_fields:
                if field['id'] == value and our_calc_uid != calc.UID():
                    return instance.translate(
                        "message_keyword_is_not_unique",
                        default = "Keyword ${title} is used by ${used_by}.",
                        mapping = {'title': value, 'used_by': calc.Title()},
                        domain = "bika")
        return True

validation.register(ServiceKeywordValidator())

class InterimFieldIDValidator:
    """Validating InterimFields :
        ID may not be the same as any service keyword.
        title must be identical for all interim fields which
        share the same id.
    """

    if issubclass(IValidator, Interface):
        implements(IValidator)
    else:
        __implements__ = (IValidator, )

    name = "interimfieldidvalidator"

    def __call__(self, value, *args, **kwargs):
        instance = kwargs['instance']

        # make sure the keyword is a valid content id
        if not re.match(r"^[A-Za-z\w\d\-\_]+$", value):
            return instance.translate(
                "message_invalid_keyword",
                default = "Keyword '${keyword}' is invalid. Only letters, numbers, spaces, _ and - are allowed.",
                mapping = {'keyword': value},
                domain="bika")

        # check the id against all AnalysisService keywords
        pc = getToolByName(instance, 'portal_catalog')
        services = pc(portal_type='AnalysisService', getKeyword = value)
        for service in services:
            if service.UID != instance.UID():
                return instance.translate(
                    "message_keyword_is_not_unique",
                    default = "Keyword ${title} is used by ${used_by}.",
                    mapping = {'title': value, 'used_by': service.Title},
                    domain = "bika")

        our_calc_uid = instance.UID()

        # check the id against all Calculation Interim Field keywords
        calcs = [c for c in pc(portal_type='Calculation')]
        for calc in calcs:
            calc = calc.getObject()
            interim_fields = calc.getInterimFields()
            if not interim_fields: continue
            for field in interim_fields:
                if field['id'] == value and our_calc_uid != calc.UID():
                    return instance.translate(
                        "message_keyword_is_not_unique",
                        default = "Keyword ${title} is used by ${used_by}.",
                        mapping = {'title': value, 'used_by': calc.Title()},
                        domain = "bika")


        return True
validation.register(InterimFieldIDValidator())

class InterimFieldTitleValidator:
    """Validating InterimFields :
        title must be identical for all interim fields which
        share the same id.
    """
    if issubclass(IValidator, Interface):
        implements(IValidator)
    else:
        __implements__ = (IValidator, )

    name = "interimfieldtitlevalidator"

    def __call__(self, value, *args, **kwargs):
        """Check that the titles of this calculation are unique
        in this calculation."""

        instance = kwargs['instance']
        pc = getToolByName(instance, 'portal_catalog')
        interim_fields = instance.getInterimFields()
        if not interim_fields:
            return True
        found = 0
        for field in interim_fields:
            if field['title'] == value:
                found += 1
        if found > 1:
            return instance.translate(
                    "message_interim_title_is_not_unique",
                    default = "${title}: duplicate field title for field.",
                    mapping = {'title': value},
                    domain = "bika")

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
                    default = "Keyword '${keyword}' is invalid.",
                    mapping = {'keyword': keyword},
                    domain="bika")
        return True

validation.register(FormulaValidator())
