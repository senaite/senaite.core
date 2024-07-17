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

from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.interfaces import IDeactivable
from datetime import timedelta
from magnitude import mg
from plone.autoform import directives
from plone.supermodel import model
from Products.CMFCore import permissions
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.content.base import Container
from senaite.core.content.mixins import SampleTypeAwareMixin
from senaite.core.interfaces import ISampleType
from senaite.core.schema import DurationField
from senaite.core.schema import UIDReferenceField
from senaite.core.schema.fields import DataGridField
from senaite.core.schema.fields import DataGridRow
from senaite.core.z3cform.widgets.datagrid import DataGridWidgetFactory
from senaite.core.z3cform.widgets.duration.widget import DurationWidgetFactory
from senaite.core.z3cform.widgets.uidreference import UIDReferenceWidgetFactory
from zope import schema
from z3c.form import validator
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import Invalid


STICKERS_VOCABULARY = 'senaite.core.vocabularies.stickertemplates'


def default_retention_period():
    """Returns the default retention period
    """
    rp = api.get_setup().getDefaultSampleLifetime()
    if isinstance(rp, timedelta):
        return rp
    elif isinstance(rp, dict):
        return timedelta(days=int(rp['days']),
                         hours=int(rp['hours']),
                         minutes=int(rp['minutes']))
    return timedelta(0)


def prefix_whitespaces_constraint(value):
    """Check that the prefix does not contain whitespaces
    """
    if ' ' in value:
        raise Invalid(_(
            u"sampletype_prefix_whitespace_validator_message",
            default=u'No whitespaces in prefix allowed'
        ))
    return True


class IStickersRecordSchema(Interface):
    """DataGrid Row for Selecting Stickers Settings
    """

    admitted = schema.Set(
        title=_(
            u"label_sampletype_admitted",
            default=u'Admitted stickers for the sample type'
        ),
        value_type=schema.Choice(
            vocabulary=STICKERS_VOCABULARY,
        ),
        required=False,
    )

    small_default = schema.Choice(
        title=_(
            u"label_sampletype_small_default",
            default=u'Default small sticker'
        ),
        vocabulary=STICKERS_VOCABULARY,
        required=False,
    )

    large_default = schema.Choice(
        title=_(
            u"label_sampletype_large_default",
            default=u'Default large sticker'
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
        "samplematrix",
        UIDReferenceWidgetFactory,
        catalog=SETUP_CATALOG,
        query={
            "is_active": True,
            "sort_on": "title",
            "sort_order": "ascending",
        },
    )
    samplematrix = UIDReferenceField(
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
        "containertype",
        UIDReferenceWidgetFactory,
        catalog=SETUP_CATALOG,
        query={
            "is_active": True,
            "sort_on": "title",
            "sort_order": "ascending",
        },
    )
    containertype = UIDReferenceField(
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
        default=[{
            'admitted': set(),
            'small_default': None,
            'large_default': None
        }]
    )


class StickersFieldValidator(validator.SimpleFieldValidator):
    """Custom validator for DGF
    (https://community.plone.org/t/how-do-i-validate-in-datagridfield/17717)
    """

    def validate(self, value):
        if value is None:
            value = []

        _valid = True if len(value) == 1 else False
        _msg = _("Invalid data")

        if not _valid:
            raise Invalid(_msg)


validator.WidgetValidatorDiscriminators(
    StickersFieldValidator,
    field=ISampleTypeSchema["admitted_sticker_templates"],
)


@implementer(ISampleType, ISampleTypeSchema, IDeactivable)
class SampleType(Container, SampleTypeAwareMixin):
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
    def getRetentionPeriod(self, raw=False):
        rp = self.getRawRetentionPeriod()
        if raw:
            return rp
        ret_val = {
            'days': rp.days,
            'hours': rp.seconds // (60*60),
            'minutes': (rp.seconds % (60*60)) // 60,
        }
        return ret_val

    @security.protected(permissions.ModifyPortalContent)
    def setRetentionPeriod(self, value):
        mutator = self.mutator("retention_period")
        mutator(self, value)

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
        accessor = self.accessor("samplematrix", raw=True)
        return accessor(self)

    @security.protected(permissions.View)
    def getSampleMatrix(self):
        samplematrix = self.getRawSampleMatrix()
        if not samplematrix:
            return None
        return api.get_object(samplematrix)

    @security.protected(permissions.ModifyPortalContent)
    def setSampleMatrix(self, value):
        mutator = self.mutator("samplematrix")
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

    def getJSMinimumVolume(self, **kw):
        """Try convert the MinimumVolume to 'ml' or 'g' so that JS has an
        easier time working with it.  If conversion fails, return raw value.
        """
        default = self.Schema()['MinimumVolume'].get(self)
        try:
            mgdefault = default.split(' ', 1)
            mgdefault = mg(float(mgdefault[0]), mgdefault[1])
        except Exception:
            mgdefault = mg(0, 'ml')
        try:
            return str(mgdefault.ounit('ml'))
        except Exception:
            pass
        try:
            return str(mgdefault.ounit('g'))
        except Exception:
            pass
        return str(default)

    @security.protected(permissions.View)
    def getRawContainerType(self):
        accessor = self.accessor("containertype", raw=True)
        return accessor(self)

    @security.protected(permissions.View)
    def getContainerType(self):
        containertype = self.getRawContainerType()
        if not containertype:
            return None
        return api.get_object(containertype)

    @security.protected(permissions.ModifyPortalContent)
    def setContainerType(self, value):
        mutator = self.mutator("containertype")
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
        mutator(self, value)

    # BBB: AT schema field property
    AdmittedStickerTemplates = property(getAdmittedStickerTemplates,
                                        setAdmittedStickerTemplates)
