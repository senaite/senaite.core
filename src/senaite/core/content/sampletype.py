# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from datetime import timedelta

from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.interfaces import IDeactivable
from plone.autoform import directives
from plone.supermodel import model
from Products.CMFCore import permissions
from senaite.core.api import dtime
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.content.base import Container
from senaite.core.interfaces import ISampleType
from senaite.core.schema import DurationField
from senaite.core.schema import UIDReferenceField
from senaite.core.schema.fields import DataGridField
from senaite.core.schema.fields import DataGridRow
from senaite.core.z3cform.widgets.datagrid import DataGridWidgetFactory
from senaite.core.z3cform.widgets.duration.widget import DurationWidgetFactory
from senaite.core.z3cform.widgets.uidreference import UIDReferenceWidgetFactory
from z3c.form import validator
from zope import schema
from zope.interface import Interface
from zope.interface import Invalid
from zope.interface import implementer

STICKERS_VOCABULARY = "senaite.core.vocabularies.stickertemplates"
DEFAULT_ADMITTED_STICKER_TEMPLATES = [{
    "admitted": set(),
    "small_default": None,
    "large_default": None
}]


def default_retention_period():
    """Returns the default retention period
    """
    period = api.get_setup().getDefaultSampleLifetime()
    return dtime.to_timedelta(period, default=timedelta(0))


def prefix_whitespaces_constraint(value):
    """Check that the prefix does not contain whitespaces
    """
    if " " in value:
        raise Invalid(_(
            u"sampletype_prefix_whitespace_validator_message",
            default=u"No whitespaces in prefix allowed"
        ))
    return True


class IStickersRecordSchema(Interface):
    """DataGrid Row for Selecting Stickers Settings
    """

    admitted = schema.Set(
        title=_(
            u"label_sampletype_admitted",
            default=u"Admitted stickers for the sample type"
        ),
        value_type=schema.Choice(
            vocabulary=STICKERS_VOCABULARY,
        ),
        required=False,
    )

    small_default = schema.Choice(
        title=_(
            u"label_sampletype_small_default",
            default=u"Default small sticker"
        ),
        vocabulary=STICKERS_VOCABULARY,
        required=False,
    )

    large_default = schema.Choice(
        title=_(
            u"label_sampletype_large_default",
            default=u"Default large sticker"
        ),
        vocabulary=STICKERS_VOCABULARY,
        required=False,
    )


class ISampleTypeSchema(model.Schema):
    """SampleType Schema
    """

    title = schema.TextLine(
        title=_(
            u"label_sampletype_title",
            default=u"Name"
        ),
        required=True,
    )

    description = schema.Text(
        title=_(
            u"label_sampletype_description",
            default=u"Description"
        ),
        required=False,
    )

    directives.widget("retention_period", DurationWidgetFactory)
    retention_period = DurationField(
        title=_(
            u"title_sampletype_duration_period",
            default=u"Retention Period"
        ),
        description=_(
            u"description_sampletype_duration_period",
            default=u"The period for which unpreserved samples of "
                    u"this type can be kept before they expire "
                    u"and cannot be analysed any further"
        ),
        required=True,
        defaultFactory=default_retention_period
    )

    hazardous = schema.Bool(
        title=_(u"title_sampletype_hazardous",
                default=u"Hazardous"),
        description=_(u"description_sampletype_hazardous",
                      default=u"Samples of this type should "
                              u"be treated as hazardous"),
        default=False,
        required=False)

    directives.widget(
        "sample_matrix",
        UIDReferenceWidgetFactory,
        catalog=SETUP_CATALOG,
        query={
            "is_active": True,
            "sort_on": "title",
            "sort_order": "ascending",
        },
    )
    sample_matrix = UIDReferenceField(
        title=_(
            u"label_sampletype_samplematrix",
            default=u"Sample Matrix"
        ),
        description=_(
            u"description_sampletype_samplematrix",
            default=u"Select the sample matrix for this sample type"
        ),
        allowed_types=("SampleMatrix", ),
        multi_valued=False,
        required=False,
    )

    prefix = schema.TextLine(
        title=_(
            u"title_sampletype_prefix",
            default=u"Sample Type Prefix"
        ),
        description=_(
            u"description_sampletype_prefix",
            default=u"Please provide a unique profile keyword"
        ),
        constraint=prefix_whitespaces_constraint,
        required=True,
    )

    min_volume = schema.TextLine(
        title=_(
            u"title_sampletype_min_volume",
            default=u"Minimum Volume"
        ),
        description=_(
            u"description_sampletype_min_volume",
            default=u"The minimum sample volume required for analysis "
                    u"eg. '10 ml' or '1 kg'."
        ),
        required=True,
    )

    directives.widget(
        "container_type",
        UIDReferenceWidgetFactory,
        catalog=SETUP_CATALOG,
        query={
            "is_active": True,
            "sort_on": "title",
            "sort_order": "ascending",
        },
    )
    container_type = UIDReferenceField(
        title=_(
            u"label_sampletype_containertype",
            default=u"Default Container Type"
        ),
        description=_(
            u"description_sampletype_containertype",
            default=u"The default container type. New sample partitions "
                    u"are automatically assigned a container of this "
                    u"type, unless it has been specified in more details "
                    u"per analysis service"
        ),
        allowed_types=("ContainerType", ),
        multi_valued=False,
        required=False,
    )

    # Stickers (Data Grid)
    directives.widget(
        "admitted_sticker_templates",
        DataGridWidgetFactory,
        allow_insert=False,
        allow_delete=False,
        allow_reorder=False,
        auto_append=False)
    admitted_sticker_templates = DataGridField(
        title=_(u"label_sampletype_admitted_stickers_templates",
                default=u"Admitted sticker templates"),
        description=_(u"description_sampletype_admitted_stickers_templates",
                      default=u"Defines the stickers to use for "
                              u"this sample type."),
        value_type=DataGridRow(schema=IStickersRecordSchema),
        required=True,
        default=DEFAULT_ADMITTED_STICKER_TEMPLATES,
    )


class StickersFieldValidator(validator.SimpleFieldValidator):
    """Custom validator for DGF
    """

    def validate(self, value):
        if value is None:
            value = []

        valid = False
        msg = _(u"Invalid sticker object format")

        if len(value) == 1:
            valid = True
            errors = []
            if not len(value[0]["admitted"]):
                valid = False
                errors.append(
                    _(u"at least one admitted sticker must be chosen"))
            if not value[0]["small_default"]:
                valid = False
                errors.append(_(u"select small default sticker"))
            if not value[0]["large_default"]:
                valid = False
                errors.append(_(u"select large default sticker"))
            msg = _(u"ERRORS: ") + ", ".join(errors)

        if not valid:
            raise Invalid(msg)


validator.WidgetValidatorDiscriminators(
    StickersFieldValidator,
    field=ISampleTypeSchema["admitted_sticker_templates"],
)


@implementer(ISampleType, ISampleTypeSchema, IDeactivable)
class SampleType(Container):
    """SampleType
    """
    # Catalogs where this type will be catalogued
    _catalogs = [SETUP_CATALOG]

    security = ClassSecurityInfo()

    @security.protected(permissions.View)
    def getRawRetentionPeriod(self):
        accessor = self.accessor("retention_period")
        return accessor(self)

    @security.protected(permissions.View)
    def getRetentionPeriod(self):
        return dtime.timedelta_to_dict(self.getRawRetentionPeriod())

    @security.protected(permissions.ModifyPortalContent)
    def setRetentionPeriod(self, value):
        default_period = default_retention_period()
        mutator = self.mutator("retention_period")
        mutator(self, dtime.to_timedelta(value, default=default_period))

    # BBB: AT schema field property
    RetentionPeriod = property(getRetentionPeriod, setRetentionPeriod)

    @security.protected(permissions.View)
    def getHazardous(self):
        accessor = self.accessor("hazardous")
        return bool(accessor(self))

    @security.protected(permissions.ModifyPortalContent)
    def setHazardous(self, value):
        mutator = self.mutator("hazardous")
        mutator(self, bool(value))

    # BBB: AT schema field property
    Hazardous = property(getHazardous, setHazardous)

    @security.protected(permissions.View)
    def getRawSampleMatrix(self):
        accessor = self.accessor("sample_matrix", raw=True)
        return accessor(self)

    @security.protected(permissions.View)
    def getSampleMatrix(self):
        accessor = self.accessor("sample_matrix")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setSampleMatrix(self, value):
        mutator = self.mutator("sample_matrix")
        mutator(self, value)

    # BBB: AT schema field property
    SampleMatrix = property(getSampleMatrix, setSampleMatrix)

    @security.protected(permissions.View)
    def getPrefix(self):
        accessor = self.accessor("prefix")
        value = accessor(self) or ""
        return value.encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setPrefix(self, value):
        mutator = self.mutator("prefix")
        mutator(self, api.safe_unicode(value))

    # BBB: AT schema field property
    Prefix = property(getPrefix, setPrefix)

    @security.protected(permissions.View)
    def getMinimumVolume(self):
        accessor = self.accessor("min_volume")
        value = accessor(self) or ""
        return value.encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setMinimumVolume(self, value):
        mutator = self.mutator("min_volume")
        mutator(self, api.safe_unicode(value))

    # BBB: AT schema field property
    MinimumVolume = property(getMinimumVolume, setMinimumVolume)

    @security.protected(permissions.View)
    def getRawContainerType(self):
        accessor = self.accessor("container_type", raw=True)
        return accessor(self)

    @security.protected(permissions.View)
    def getContainerType(self):
        accessor = self.accessor("container_type")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setContainerType(self, value):
        mutator = self.mutator("container_type")
        mutator(self, value)

    # BBB: AT schema field property
    ContainerType = property(getContainerType, setContainerType)

    @security.protected(permissions.View)
    def getAdmittedStickerTemplates(self):
        accessor = self.accessor("admitted_sticker_templates")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setAdmittedStickerTemplates(self, value):
        mutator = self.mutator("admitted_sticker_templates")
        # ensure list and filter out empty dictionaries
        value = filter(None, api.to_list(value))
        if not value:
            value = DEFAULT_ADMITTED_STICKER_TEMPLATES
        mutator(self, value)

    # BBB: AT schema field property
    AdmittedStickerTemplates = property(getAdmittedStickerTemplates,
                                        setAdmittedStickerTemplates)

    def getAdmittedStickers(self):
        """
        Returns the admitted sticker IDs defined.

        :return: An array of sticker IDs
        """
        admitted = self.getAdmittedStickerTemplates()[0].get("admitted")
        if admitted:
            return admitted
        return []

    def getDefaultSmallSticker(self):
        """
        Returns the small sticker ID defined as default.

        :return: A string as an sticker ID
        """
        return self.getAdmittedStickerTemplates()[0].get("small_default")

    def getDefaultLargeSticker(self):
        """
        Returns the large sticker ID defined as default.

        :return: A string as an sticker ID
        """
        return self.getAdmittedStickerTemplates()[0].get("large_default")
