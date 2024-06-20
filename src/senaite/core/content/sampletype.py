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
from plone.autoform import directives
from plone.supermodel import model
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.content.base import Container
from senaite.core.interfaces import ISampleTemplate
from senaite.core.schema import DurationField
from senaite.core.schema import UIDReferenceField
from senaite.core.z3cform.widgets.uidreference import UIDReferenceWidgetFactory
from zope import schema
from zope.interface import implementer
from zope.interface import Invalid
from zope.interface import invariant
from zope.schema.interfaces import IContextAwareDefaultFactory


SMALL_DEFAULT_STICKER = "small_default"
LARGE_DEFAULT_STICKER = "large_default"


def default_retention_period():
    """Returns the default retention period
    """
    defaultVAT = api.get_setup().getDefaultSampleLifetime()
    return Decimal(defaultVAT)


def prefix_whitespaces_constraint(value):
    """Check that the prefix does not contain whitespaces
    """
    if ' ' in value:
        raise Invalid(_(
            u"sampletype_prefix_whitespace_validator_message",
            default=u'No whitespaces in prefix allowed'
        ))
    return True


class ISampleTypeSchema(model.Schema):
    """SampleType Schema
    """

    retention_period = DurationField(
        title=_(
            u"title_sampletype_duration_period",
            default=u"Retention Period"
        ),
        description=_(
            u"description_sampletype_duration_period",
            default=u"The period for which un-preserved samples of "
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
            default=u"he minimum sample volume required for analysis "
                    u"eg. '10 ml' or '1 kg'."
        ),
        constraint=prefix_whitespaces_constraint,
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
