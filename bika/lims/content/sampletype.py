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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATExtensions.ateapi import RecordsField
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from magnitude import mg
from zope.interface import implements

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.browser.fields import DurationField
from bika.lims.browser.widgets import DurationWidget
from bika.lims.browser.widgets import SampleTypeStickersWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IDeactivable
from bika.lims.interfaces import ISampleType
from bika.lims.interfaces import ISampleTypeAwareMixin
from bika.lims.vocabularies import getStickerTemplates

SMALL_DEFAULT_STICKER = 'small_default'
LARGE_DEFAULT_STICKER = 'large_default'


def sticker_templates():
    """
    It returns the registered stickers in the system.
    :return: a DisplayList object
    """
    voc = DisplayList()
    stickers = getStickerTemplates()
    for sticker in stickers:
        voc.add(sticker.get('id'), sticker.get('title'))
    if voc.index == 0:
        logger.warning('Sampletype: getStickerTemplates is empty!')
    return voc


class SampleTypeAwareMixin(BaseObject):
    implements(ISampleTypeAwareMixin)

    security = ClassSecurityInfo()

    @security.public
    def getSampleType(self):
        """Returns the sample type(s) assigned to this object, if any
        """
        if ISampleType.providedBy(self):
            return self

        field = self._get_field()
        if not field:
            return None

        sample_type = field.get(self)
        return sample_type or None

    @security.public
    def getSampleTypeUID(self):
        """Returns the UID(s) of the Sample Type(s) assigned to this object
        """
        sample_type = self.getSampleType()
        if isinstance(sample_type, (list, tuple)):
            return map(api.get_uid, sample_type)
        elif sample_type:
            return api.get_uid(sample_type)
        return None

    @security.public
    def getSampleTypeTitle(self):
        """Returns the title or a comma separated list of sample type titles
        """
        sample_type = self.getSampleType()
        if isinstance(sample_type, (list, tuple)):
            title = map(api.get_title, sample_type)
            return ", ".join(title)
        elif sample_type:
            return api.get_title(sample_type)
        return None

    def _get_field(self):
        """Returns the field that stores the SampleType object, if any
        """
        field = self.getField("SampleType", None)
        if not field:
            field = self.getField("SampleTypes", None)

        return field


schema = BikaSchema.copy() + Schema((
    DurationField('RetentionPeriod',
        required = 1,
        default_method = 'getDefaultLifetime',
        widget = DurationWidget(
            label=_("Retention Period"),
            description =_(
                "The period for which un-preserved samples of this type can be kept before "
                "they expire and cannot be analysed any further"),
        )
    ),
    BooleanField('Hazardous',
        default = False,
        widget = BooleanWidget(
            label=_("Hazardous"),
            description=_("Samples of this type should be treated as hazardous"),
        ),
    ),
    ReferenceField('SampleMatrix',
        required = 0,
        allowed_types = ('SampleMatrix',),
        vocabulary = 'SampleMatricesVocabulary',
        relationship = 'SampleTypeSampleMatrix',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 0,
            label=_("Sample Matrix"),
        ),
    ),
    StringField('Prefix',
        required = True,
        validators=('no_white_space_validator'),
        widget = StringWidget(
            label=_("Sample Type Prefix"),
            description=_("Prefixes can not contain spaces."),
        ),
    ),
    StringField('MinimumVolume',
        required = 1,
        widget = StringWidget(
            label=_("Minimum Volume"),
            description=_("The minimum sample volume required for analysis eg. '10 ml' or '1 kg'."),
        ),
    ),
    ReferenceField('ContainerType',
        required = 0,
        allowed_types = ('ContainerType',),
        vocabulary = 'ContainerTypesVocabulary',
        relationship = 'SampleTypeContainerType',
        widget = ReferenceWidget(
            checkbox_bound = 0,
            label=_("Default Container Type"),
            description =_(
                "The default container type. New sample partitions "
                "are automatically assigned a container of this "
                "type, unless it has been specified in more details "
                "per analysis service"),
        ),
    ),
    RecordsField(
        'AdmittedStickerTemplates',
        subfields=(
            'admitted',
            SMALL_DEFAULT_STICKER,
            LARGE_DEFAULT_STICKER,
            ),
        subfield_labels={
            'admitted': _(
                'Admitted stickers for the sample type'),
            SMALL_DEFAULT_STICKER: _(
                'Default small sticker'),
            LARGE_DEFAULT_STICKER: _(
                'Default large sticker')},
        subfield_sizes={
            'admitted': 6,
            SMALL_DEFAULT_STICKER: 1,
            LARGE_DEFAULT_STICKER: 1},
        subfield_types={
            'admitted': 'selection',
            SMALL_DEFAULT_STICKER: 'selection',
            LARGE_DEFAULT_STICKER: 'selection'
                        },
        subfield_vocabularies={
            'admitted': sticker_templates(),
            SMALL_DEFAULT_STICKER: '_sticker_templates_vocabularies',
            LARGE_DEFAULT_STICKER: '_sticker_templates_vocabularies',
        },
        required_subfields={
            'admitted': 1,
            SMALL_DEFAULT_STICKER: 1,
            LARGE_DEFAULT_STICKER: 1},
        default=[{}],
        fixedSize=1,
        widget=SampleTypeStickersWidget(
            label=_("Admitted sticker templates"),
            description=_(
                "Defines the stickers to use for this sample type."),
            allowDelete=False,
        ),
    ),
))

schema['description'].schemata = 'default'
schema['description'].widget.visible = True


class SampleType(BaseContent, HistoryAwareMixin, SampleTypeAwareMixin):

    implements(ISampleType, IDeactivable)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        return safe_unicode(self.getField('title').get(self)).encode('utf-8')

    def getJSMinimumVolume(self, **kw):
        """Try convert the MinimumVolume to 'ml' or 'g' so that JS has an
        easier time working with it.  If conversion fails, return raw value.
        """
        default = self.Schema()['MinimumVolume'].get(self)
        try:
            mgdefault = default.split(' ', 1)
            mgdefault = mg(float(mgdefault[0]), mgdefault[1])
        except:
            mgdefault = mg(0, 'ml')
        try:
            return str(mgdefault.ounit('ml'))
        except:
            pass
        try:
            return str(mgdefault.ounit('g'))
        except:
            pass
        return str(default)

    def getDefaultLifetime(self):
        """ get the default retention period """
        settings = getToolByName(self, 'bika_setup')
        return settings.getDefaultSampleLifetime()

    def getSamplePoints(self):
        """Returns the Sample Points where current Sample Type is supported
        """
        return self.getBackReferences("SamplePointSampleType")

    def getSamplePointTitle(self):
        """Returns a list of Sample Point titles
        """
        return map(api.get_title, self.getSamplePoints())

    def SampleMatricesVocabulary(self):
        from bika.lims.content.samplematrix import SampleMatrices
        return SampleMatrices(self, allow_blank=True)

    def ContainerTypesVocabulary(self):
        from bika.lims.content.containertype import ContainerTypes
        return ContainerTypes(self, allow_blank=True)

    def _get_sticker_subfield(self, subfield):
        values = self.getField('AdmittedStickerTemplates').get(self)
        if not values:
            return ''
        value = values[0].get(subfield)
        return value

    def getDefaultSmallSticker(self):
        """
        Returns the small sticker ID defined as default.

        :return: A string as an sticker ID
        """
        return self._get_sticker_subfield(SMALL_DEFAULT_STICKER)

    def getDefaultLargeSticker(self):
        """
        Returns the large sticker ID defined as default.

        :return: A string as an sticker ID
        """
        return self._get_sticker_subfield(LARGE_DEFAULT_STICKER)

    def getAdmittedStickers(self):
        """
        Returns the admitted sticker IDs defined.

        :return: An array of sticker IDs
        """
        admitted = self._get_sticker_subfield('admitted')
        if admitted:
            return admitted
        return []

    def _sticker_templates_vocabularies(self):
        """
        Returns the vocabulary to be used in
        AdmittedStickerTemplates.small_default

        If the object has saved not AdmittedStickerTemplates.admitted stickers,
        this method will return an empty DisplayList. Otherwise it returns
        the stickers selected in admitted.

        :return: A DisplayList
        """
        admitted = self.getAdmittedStickers()
        if not admitted:
            return DisplayList()
        voc = DisplayList()
        stickers = getStickerTemplates()
        for sticker in stickers:
            if sticker.get('id') in admitted:
                voc.add(sticker.get('id'), sticker.get('title'))
        return voc

    def setDefaultSmallSticker(self, value):
        """
        Sets the small sticker ID defined as default.

        :param value: A sticker ID
        """
        self._set_sticker_subfield(SMALL_DEFAULT_STICKER, value)

    def setDefaultLargeSticker(self, value):
        """
        Sets the large sticker ID defined as default.

        :param value: A sticker ID
        """
        self._set_sticker_subfield(LARGE_DEFAULT_STICKER, value)

    def setAdmittedStickers(self, value):
        """
        Sets the admitted sticker IDs.

        :param value: An array of sticker IDs
        """
        self._set_sticker_subfield('admitted', value)

    def _set_sticker_subfield(self, subfield, value):
        if value is None:
            logger.error(
                "Setting wrong 'AdmittedStickerTemplates/admitted' value"
                " to Sample Type '{}'"
                .format(self.getId()))
            return
        if not isinstance(value, list):
            logger.error(
                "Setting wrong 'AdmittedStickerTemplates/admitted' value"
                " type to Sample Type '{}'"
                .format(self.getId()))
            return
        field = self.getField('AdmittedStickerTemplates')
        stickers = field.get(self)
        stickers[0][subfield] = value
        field.set(self, stickers)


registerType(SampleType, PROJECTNAME)
