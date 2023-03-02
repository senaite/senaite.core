# -*- coding: utf-8 -*-

from bika.lims import senaiteMessageFactory as _
from plone.autoform import directives
from plone.supermodel import model
from senaite.core.schema.registry import DataGridRow
from senaite.core.z3cform.widgets.datagrid import DataGridWidgetFactory
from zope import schema
from zope.interface import Interface
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory


class IColumn(Interface):
    visible = schema.Bool(
        title=_(u"Visible"),
        required=True,
    )
    name = schema.ASCIILine(
        title=_(u"Column Name"),
        required=True,
    )


@provider(IContextAwareDefaultFactory)
def default_analysis_columns_config(context):
    """Deafult sample analysis columns
    """
    default = [
        {"visible": False, "name": "created"},
        {"visible": True, "name": "Service"},
        {"visible": True, "name": "DetectionLimitOperand"},
        {"visible": True, "name": "Result"},
        {"visible": True, "name": "Uncertainty"},
        {"visible": True, "name": "Unit"},
        {"visible": True, "name": "Specification"},
        {"visible": True, "name": "retested"},
        {"visible": True, "name": "Method"},
        {"visible": True, "name": "Instrument"},
        {"visible": True, "name": "Calculation"},
        {"visible": True, "name": "Attachments"},
        {"visible": True, "name": "SubmittedBy"},
        {"visible": True, "name": "Analyst"},
        {"visible": True, "name": "CaptureDate"},
        {"visible": True, "name": "DueDate"},
        {"visible": True, "name": "state_title"},
        {"visible": True, "name": "Hidden"},
    ]
    return default[:]


class ISenaiteRegistry(model.Schema):
    """Senaite registry schema
    """


class ISampleViewRegistry(ISenaiteRegistry):
    """Registry settings for sample settings
    """
    model.fieldset(
        "sample_view",
        label=_(u"Sample View"),
        description=_("Configuration for the sample view"),
        fields=[
            "sampleview_collapse_field_analysis_table",
            "sampleview_collapse_lab_analysis_table",
            "sampleview_collapse_qc_analysis_table",
            "sampleview_analysis_columns_config",
        ],
    )
    sampleview_collapse_field_analysis_table = schema.Bool(
        title=_("Collapse field analysis table"),
        description=_("Collapse field analysis table in sample view"),
        default=False,
        required=False,
    )

    sampleview_collapse_lab_analysis_table = schema.Bool(
        title=_("Collapse lab analysis table"),
        description=_("Collapse lab analysis table in sample view"),
        default=False,
        required=False,
    )

    sampleview_collapse_qc_analysis_table = schema.Bool(
        title=_("Collapse qc analysis table"),
        description=_("Collapse qc analysis table in sample view"),
        default=True,
        required=False,
    )

    directives.widget(
        "sampleview_analysis_columns_config",
        DataGridWidgetFactory,
        allow_reorder=True,
        allow_delete=True,
        auto_append=True)
    sampleview_analysis_columns_config = schema.List(
        title=_(u"Analysis columns config"),
        description=_(
            u"Default column configuration for sample analysis listings"
        ),
        value_type=DataGridRow(
            title=u"Column",
            schema=IColumn),
        required=False,
        defaultFactory=default_analysis_columns_config,
    )


class ISampleHeaderRegistry(ISenaiteRegistry):
    """Registry settings for sample header configuration
    """

    model.fieldset(
        "sample_header",
        label=_(u"Sample Header"),
        description=_("Configuration for the sample header information"),
        fields=[
            "sampleheader_show_standard_fields",
            "sampleheader_prominent_columns",
            "sampleheader_standard_columns",
            "sampleheader_prominent_fields",
            "sampleheader_standard_fields",
            "sampleheader_field_visibility",
        ],
    )

    sampleheader_show_standard_fields = schema.Bool(
        title=_("Show standard fields"),
        description=_("Toggle visibility of standard sample header fields"),
        default=True,
        required=False,
    )

    sampleheader_prominent_columns = schema.Int(
        title=_("Number of prominent columns"),
        description=_("Number of prominent columns"),
        default=1,
        required=False,
        min=0,
        max=10,
    )

    sampleheader_standard_columns = schema.Int(
        title=_("Number of standard columns"),
        description=_("Number of standard columns"),
        default=3,
        required=False,
        min=0,
        max=10,
    )

    sampleheader_prominent_fields = schema.List(
        title=_("Prominent fields"),
        description=_("Prominent fields"),
        value_type=schema.ASCIILine(),
        required=False,
    )

    sampleheader_standard_fields = schema.List(
        title=_("Standard fields"),
        description=_("Standard fields"),
        value_type=schema.ASCIILine(),
        required=False,
    )

    sampleheader_field_visibility = schema.Dict(
        title=_("Field visibility"),
        description=_("Visible fields"),
        key_type=schema.ASCIILine(title=_("Field Name"),),
        value_type=schema.Bool(title=_("Field visibility"), default=True),
        required=False,
    )
