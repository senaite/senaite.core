from operator import itemgetter

from Products.ATExtensions.field import RecordField
from Products.ATExtensions.field import RecordsField
from Products.Archetypes.Registry import registerField
from Products.Archetypes.interfaces import IFieldDefaultProvider
from zope.interface import implements

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import AnalysisSpecificationWidget
from bika.lims.catalog import SETUP_CATALOG
from bika.lims.interfaces.analysis import IRequestAnalysis

# A tuple of (subfield_id, subfield_label,)
SUB_FIELDS = (
    ("keyword", _("Analysis Service")),
    ("min_operator", _("Min operator")),
    ("min", _('Min')),
    ("max_operator", _("Max operator")),
    ("max", _('Max')),
    ("warn_min", _('Min warn')),
    ("warn_max", _('Max warn')),
    ("hidemin", _('< Min')),
    ("hidemax", _('> Max')),
    ("rangecomment", _('Range Comment')),
)


class ResultsRangeField(RecordField):
    """A field that stores a results range
    """
    _properties = RecordField._properties.copy()
    _properties.update({
        "type": "results_range_field",
        "subfields": map(itemgetter(0), SUB_FIELDS),
        "subfield_labels": dict(SUB_FIELDS),
    })

    def get(self, instance, **kwargs):
        from bika.lims.content.analysisspec import ResultsRangeDict
        value = super(ResultsRangeField, self).get(instance, **kwargs)
        if value:
            return ResultsRangeDict(dict(value.items()))
        return {}


registerField(ResultsRangeField, title="ResultsRange",
              description="Used for storing a results range",)


class SpecificationsField(RecordsField):
    """A field that stores a list of results ranges
    """
    _properties = RecordsField._properties.copy()
    _properties.update({
        "type": "specifications",
        "subfields": map(itemgetter(0), SUB_FIELDS),
        "subfield_labels": dict(SUB_FIELDS),
        "subfield_validators": {
            "min": "analysisspecs_validator",
            "max": "analysisspecs_validator",
        },
        "required_subfields": ("keyword", ),
        "widget": AnalysisSpecificationWidget,
    })

    def get(self, instance, **kwargs):
        from bika.lims.content.analysisspec import ResultsRangeDict
        values = super(SpecificationsField, self).get(instance, **kwargs)

        # If a keyword or an uid has been specified, return the result range
        # for that uid or keyword only
        uid = kwargs.get("uid")
        keyword = kwargs.get("keyword")
        if uid or keyword:
            return self.getResultsRange(values, uid or keyword)

        # Convert the dict items to ResultRangeDict for easy handling
        return map(lambda val: ResultsRangeDict(dict(val.items())), values)

    def getResultsRange(self, values, uid_keyword_service):
        from bika.lims.content.analysisspec import ResultsRangeDict
        if not uid_keyword_service:
            return None

        if api.is_object(uid_keyword_service):
            uid_keyword_service = api.get_uid(uid_keyword_service)

        key = "keyword"
        if api.is_uid(uid_keyword_service) and uid_keyword_service != "0":
            # We always assume a uid of "0" refers to portal
            key = "uid"

        # Find out the item for the given uid/keyword
        value = filter(lambda v: v.get(key) == uid_keyword_service, values)
        return value and ResultsRangeDict(dict(value[0].items())) or None

    def _to_dict(self, value):
        """Convert the records to persistent dictionaries
        """
        # Resolve items to guarantee all them have the key uid
        value = super(SpecificationsField, self)._to_dict(value)
        return map(self.resolve_uid, value)

    def resolve_uid(self, raw_dict):
        value = raw_dict.copy()
        uid = value.get("uid")
        if api.is_uid(uid) and uid != "0":
            return value

        # uid key does not exist or is not valid, try to infere from keyword
        keyword = value.get("keyword")
        if keyword:
            query = dict(portal_type="AnalysisService", getKeyword=keyword)
            brains = api.search(query, SETUP_CATALOG)
            if len(brains) == 1:
                uid = api.get_uid(brains[0])
        value["uid"] = uid
        return value


class DefaultResultsRangeProvider(object):
    """Default Results Range provider for analyses
    This is used for backwards-compatibility for when the analysis' ResultsRange
    was obtained directly from Sample's ResultsRanges field, before this:
    https://github.com/senaite/senaite.core/pull/1506
    """
    implements(IFieldDefaultProvider)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        """Get the default value.
        """
        if not IRequestAnalysis.providedBy(self.context):
            return {}

        keyword = self.context.getKeyword()
        sample = self.context.getRequest()
        if sample and keyword:
            field = sample.getField("ResultsRange")
            rr = field.get(sample, keyword=keyword)
            if rr:
                #self.context.setResultsRange(rr)
                return rr
                #return self.context.getResultsRange()

        return {}
        #from bika.lims.content.analysisspec import ResultsRangeDict
        #return ResultsRangeDict(uid=api.get_uid(self.context), keyword=keyword)
