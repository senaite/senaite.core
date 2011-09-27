from Products.CMFCore.utils import getToolByName
from Acquisition import aq_parent
from Products.validation.interfaces.IValidator import IValidator
from Products.validation import validation
from bika.lims.utils import sortable_title
from zope.interface import Interface, implements
from zope.site.hooks import getSite
from zExceptions import Redirect
import sys,re
from bika.lims import bikaMessageFactory as _

class UniqueFieldValidator:
    """ Verifies that a field value is unique for items
    if the same type in this location """

    implements(IValidator)
    name = "uniquefieldvalidator"

    def __call__(self, value, *args, **kwargs):
        instance = kwargs['instance']
        fieldname = kwargs['field'].getName()
        request = kwargs.get('REQUEST', {})
        form = request.get('form', {})

        ts = getToolByName(instance, 'translation_service')

        if value == instance.get(fieldname):
            return True

        for item in aq_parent(instance).objectValues():
            if item.UID() != instance.UID() and \
               item.schema.get(fieldname).getAccessor(item)() == value:
                return ts.translate(
                    "message_field_is_not_unique",
                    "bika",
                    {'value': value},
                    instance,
                    default = "Validation failed: '${value}' is in use.")
        return True

validation.register(UniqueFieldValidator())

class ServiceKeywordValidator:
    """Validate AnalysisService Keywords
    must match isUnixLikeName
    may not be the same as another service keyword
    may not be the same as any InterimField id.
    """

    implements(IValidator)
    name = "servicekeywordvalidator"

    def __call__(self, value, *args, **kwargs):
        instance = kwargs['instance']
        fieldname = kwargs['field'].getName()
        request = kwargs.get('REQUEST', {})
        form = request.get('form', {})

        ts = getToolByName(instance, 'translation_service')

        if re.findall(r"[^A-Za-z\w\d\-\_]", value):
            return _("Validation failed: keyword contains invalid characters.")

        # check the value against all AnalysisService keywords
        # this has to be done from portal_catalog so we don't
        # clash with ourself
        pc = getToolByName(instance, 'portal_catalog')
        services = pc(portal_type='AnalysisService', getKeyword = value)
        for service in services:
            if service.UID != instance.UID():
                return ts.translate(
                    "message_keyword_used_by_service",
                    "bika",
                    {'title': value, 'used_by': service.Title},
                    instance,
                    default = "Validation failed: '${title}': "
                              "This keyword is used by service '${used_by}'.")

        calc = hasattr(instance, 'getCalculation') and \
             instance.getCalculation() or None
        our_calc_uid = calc and calc.UID() or ''

        # check the value against all Calculation Interim Field ids
        calcs = [c for c in pc(portal_type='Calculation')]
        for calc in calcs:
            calc = calc.getObject()
            interim_fields = calc.getInterimFields()
            if not interim_fields: continue
            for field in interim_fields:
                if field['keyword'] == value and our_calc_uid != calc.UID():
                    return ts.translate(
                        "message_keyword_used_by_calc",
                        "bika",
                        {'title': value, 'used_by': calc.Title()},
                        instance,
                        default = "Validation failed: '${title}': " \
                                  "This keyword is used by calculation '${used_by}'.")
        return True

validation.register(ServiceKeywordValidator())

class InterimFieldsValidator:
    """Validating InterimField keywords.  applied as a subfield validator
        on keyword subfield, but validates entire InterimFields field form
        data.
        keyword must match isUnixLikeName
        keyword may not be the same as any service keyword.
        keyword must be unique in this InterimFields field
        keyword must be unique for all interimfields which share the same title.
        title must be unique for all interimfields which share the same keyword.
    """

    implements(IValidator)
    name = "interimfieldsvalidator"

    def __call__(self, value, *args, **kwargs):
        instance = kwargs['instance']
        fieldname = kwargs['field'].getName()
        request = kwargs.get('REQUEST', {})
        form = request.form
        interim_fields = form.get(fieldname)

        ts = getToolByName(instance, 'translation_service')
        pc = getToolByName(instance, 'portal_catalog')

        if not re.match(r"^[A-Za-z][\w\d\-\_]+$", value):
            return _("Validation failed: keyword contains invalid characters.")

        # keywords and titles used once only in the submitted form
        keywords = {}
        titles = {}
        for field in interim_fields:
            if 'keyword' in field:
                if field['keyword'] in keywords:
                    keywords[field['keyword']] += 1
                else:
                    keywords[field['keyword']] = 1
            if 'title' in field:
                if field['title'] in titles:
                    titles[field['title']] += 1
                else:
                    titles[field['title']] = 1
        for k in [k for k in keywords.keys() if keywords[k] > 1]:
            return ts.translate(
                "message_interim_keyword_is_not_unique",
                "bika",
                {'keyword': k},
                instance,
                default = "Validation failed: '${keyword}': duplicate keyword.")
        for t in [t for t in titles.keys() if titles[t] > 1]:
            return ts.translate(
                "message_interim_title_is_not_unique",
                "bika",
                {'title': t},
                instance,
                default = "Validation failed: '${title}': duplicate title.")

        # check all keywords against all AnalysisService keywords for dups
        services = pc(portal_type='AnalysisService', getKeyword = value)
        for service in services:
            if value == service.getKeyword:
                return ts.translate(
                    "message_keyword_used_by_service",
                    "bika",
                    {'title': value, 'used_by': service.Title},
                    instance,
                    default = "Validation failed: '${title}': "\
                              "This keyword is used by service '${used_by}'.")

        # any duplicated interimfield titles must share the same keyword
        # any duplicated interimfield keywords must share the same title
        calcs = pc(portal_type='Calculation')
        keyword_titles = {}
        title_keywords = {}
        for calc in calcs:
            if calc.UID == instance.UID():
                continue
            calc = calc.getObject()
            for field in calc.getInterimFields():
                keyword_titles[field['keyword']] = field['title']
                title_keywords[field['title']] = field['keyword']
        for field in interim_fields:
            if field['keyword'] != value:
                continue
            if 'title' in field and \
               field['title'] in title_keywords.keys() and \
               title_keywords[field['title']] != field['keyword']:
                return ts.translate(
                    "message_interimfield_keyword_mismatch",
                    "bika",
                    {'title': field['title'],
                     'keyword': title_keywords[field['title']]},
                    instance,
                    default = "Validation failed: column '${title}' "\
                              "must have keyword '${keyword}'.")
            if 'keyword' in field and \
               field['keyword'] in keyword_titles.keys() and \
               keyword_titles[field['keyword']] != field['title']:
                return ts.translate(
                    "message_interimfield_title_mismatch",
                    "bika",
                    {'keyword': field['keyword'],
                     'title': keyword_titles[field['keyword']]},
                    instance,
                    default = "Validation failed: keyword '${keyword}' " \
                              "must have column title '${title}'.")

        return True

validation.register(InterimFieldsValidator())

class FormulaValidator:
    """ Validate keywords in calculation formula entry
    """
    implements(IValidator)
    name = "formulavalidator"

    def __call__(self, value, *args, **kwargs):
        if not value:
            return True

        instance = kwargs['instance']
        fieldname = kwargs['field'].getName()
        request = kwargs.get('REQUEST', {})
        form = request.form
        interim_fields = form.get('InterimFields')

        ts = getToolByName(instance, 'translation_service')
        pc = getToolByName(instance, 'portal_catalog')

        interim_keywords = [f['keyword'] for f in interim_fields]
        keywords = re.compile(r"\%\(([^\)]+)\)").findall(value)

        for keyword in keywords:
            # Check if the service keyword exists and is active.
            dep_service = pc(getKeyword=keyword, inactive_state="active")
            if not dep_service and \
               not keyword in interim_keywords:
                return ts.translate(
                    "message_invalid_keyword",
                    "bika",
                    {'keyword': keyword},
                    instance,
                    default = "Validation failed: Keyword '${keyword}' is invalid.")
        return True

validation.register(FormulaValidator())

class LatLongValidator:
    """ Validate latitude or longitude field values
      52<nondigits>12<nondigits>17.0<nondigits>N == 52deg12'17.0"N etc.
    """
    implements(IValidator)
    def __init__(self, name):
        self.name = name

    def __call__(self, value, *args, **kwargs):
        if not value:
            return True

        instance = kwargs['instance']
        fieldname = kwargs['field'].getName()
        request = kwargs.get('REQUEST', {})

        ts = getToolByName(instance, 'translation_service')
        pc = getToolByName(instance, 'portal_catalog')

        if self.name == 'latitude_validator':
            parts = re.compile(r"(\d+)\D+(\d+)\D+([\d\.]+)\D*([nsNS]{1})").findall(value)
            if not parts:
                return _("Invalid Latitude. Use DEG MIN SEC N/S")
        else:
            parts = re.compile(r"(\d+)\D+(\d+)\D+([\d\.]+)\D*([ewEW]{1})").findall(value)
            if not parts:
                return _("Invalid Longitude. Use DEG MIN SEC E/W")

        return True



validation.register(LatLongValidator("latitude_validator"))
validation.register(LatLongValidator("longitude_validator"))
