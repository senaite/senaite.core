import urllib
from sys import exc_info

from bika.lims import bikaMessageFactory as _
from bika.lims.interfaces import IIdServer
from DateTime import DateTime
from plone.i18n.normalizer.interfaces import IFileNameNormalizer
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility, getAdapter
from zope.interface import implements
import re
import transaction
import zLOG;


class IDServerUnavailable(Exception):
    pass


def renameAfterCreation(instance):
    """This is explicitly fired for all bika types.
    :param instance: the instance we are renaming here.
    :return: the new ID the instance was given.
    """
    # Can't rename without a subtransaction commit when using portal_factory
    transaction.savepoint(optimistic=True)
    # get new ID from nearest adapter
    new_id = IIdServer(instance).generateUniqueId()
    # rename objects
    instance.aq_inner.aq_parent.manage_renameObject(instance.id, new_id)
    return new_id


class DefaultBikaIdServer(object):
    """This Id server is capable of giving back IDs for any new object.
    - ARs are named with -Rx
    - Partitions are named with -Px
    - Samples are named with the Prefix from their sampletype
    - May be delegated to bika external ID Server
    - May include the year in IDs
    """
    implements(IIdServer)

    def __init__(self, context):
        self.context = context

    def generateUniqueId(self):
        """ Generate pretty content IDs.
            - context is used to find portal_type; in case there is no
              prefix specified for the type, the lowercased portal_type is
              used as a prefix instead.  In this case the year is not inserted,
              regardless of the include_year setting.
        """

        portal_type = self.context.portal_type

        fn_normalize = getUtility(IFileNameNormalizer).normalize
        id_normalize = getUtility(IIDNormalizer).normalize

        year = self.context.bika_setup.getYearInPrefix() and \
               DateTime().strftime("%Y")[2:] or ''

        # ARs use the Sample ID, with '-R<arnumber>' appended
        if portal_type == "AnalysisRequest":
            sample = self.context.getSample()
            s_prefix = fn_normalize(sample.getSampleType().getPrefix())
            sample_padding = self.context.bika_setup.getSampleIDPadding()
            ar_padding = self.context.bika_setup.getARIDPadding()
            sample_id = sample.getId()
            sample_number = sample_id.split(s_prefix)[1]
            ar_number = sample.getLastARNumber()
            ar_number = ar_number and ar_number + 1 or 1
            # There is possibly stuff that require the '-Rx'.
            return fn_normalize(
                "%s%s-R%s" % (s_prefix,
                              str(sample_number).zfill(sample_padding),
                              str(ar_number).zfill(ar_padding))
            )

        # SamplePartitions use the Sample ID, with '-P<partnr>' appended
        if portal_type == "SamplePartition":
            # at this time the part exists, so +1 would be 1 too many
            partnr = str(
                len(self.context.aq_parent.objectValues('SamplePartition')))
            # parent id is normalized already
            # There is possibly stuff that require the '-Px'.
            return "%s-P%s" % (self.context.aq_parent.id, partnr)

        # External ID Server enabled
        if self.context.bika_setup.getExternalIDServer():
            # For the default external ID server, we must pass in a prefix,
            # and optionally pass along the batch_size we are given.
            # So first we try lookup prefix in default bika_setup prefix field.
            prefixes = self.context.bika_setup.getPrefixes()
            for d in prefixes:
                # Sample ID comes from SampleType
                if portal_type == "Sample":
                    prefix = self.context.getSampleType().getPrefix()
                    padding = self.context.bika_setup.getSampleIDPadding()
                    new_id = str(
                        self.get_external_id("%s%s-" % (prefix, year)))
                    if padding:
                        new_id = new_id.zfill(int(padding))
                    return '%s%s-%s' % (prefix, year, new_id)
                elif d['portal_type'] == portal_type:
                    prefix = d['prefix']
                    padding = d['padding']
                    new_id = str(
                        self.get_external_id("%s%s-" % (prefix, year)))
                    if padding:
                        new_id = new_id.zfill(int(padding))
                    return '%s%s-%s' % (prefix, year, new_id)
            # no prefix found, using portal_type to invoke external ID server.
            npt = id_normalize(portal_type)
            new_id = str(self.get_external_id(npt + "-"))
            return '%s-%s' % (npt, new_id)
        else:
            # No external id-server.  So now we'll just grab the ID by looking
            # at the existing content object Ids.
            # This isn't very good XXX

            def next_id(prefix):
                # normalize before anything
                prefix = fn_normalize(prefix)
                plone = self.context.portal_url.getPortalObject()
                # grab the first catalog we are indexed in.
                at = getToolByName(plone, 'archetype_tool')
                if portal_type in at.catalog_map:
                    catalog_name = at.catalog_map[portal_type][0]
                else:
                    catalog_name = 'portal_catalog'
                catalog = getToolByName(plone, catalog_name)
                # get all IDS that start with prefix
                # this must specifically exclude AR IDs (two -'s)
                r = re.compile("^" + prefix + "-[\d+]+$")
                ids = [int(i.split(prefix + "-")[1]) \
                       for i in catalog.Indexes['id'].uniqueValues() \
                       if r.match(i)]

                # plone_tool = getToolByName(self.context, 'plone_utils')
                # if not plone_tool.isIDAutoGenerated(l.id):
                ids.sort()
                _id = ids and ids[-1] or 0
                new_id = _id + 1
                return str(new_id)

            prefixes = self.context.bika_setup.getPrefixes()
            for d in prefixes:
                if portal_type == "Sample":
                    # Special case for Sample IDs
                    prefix = fn_normalize(
                        self.context.getSampleType().getPrefix())
                    padding = self.context.bika_setup.getSampleIDPadding()
                    new_id = next_id(prefix + year)
                    if padding:
                        new_id = new_id.zfill(int(padding))
                    return '%s%s-%s' % (prefix, year, new_id)
                elif d['portal_type'] == portal_type:
                    prefix = d['prefix']
                    padding = d['padding']
                    new_id = next_id(prefix + year)
                    if padding:
                        new_id = new_id.zfill(int(padding))
                    return '%s%s-%s' % (prefix, year, new_id)
            # no prefix, use portal_type
            prefix = id_normalize(portal_type);
            new_id = next_id(prefix)
            return '%s-%s' % (prefix, new_id)

    def get_external_id(self, context, prefix, batch_size=None):
        """ Generate a new id using external ID server.
        """
        plone = self.context.portal_url.getPortalObject()
        url = self.context.bika_setup.getIDServerURL()

        try:
            if batch_size:
                # GET
                f = urllib.urlopen('%s/%s/%s?%s' % (
                    url,
                    plone.getId(),
                    prefix,
                    urllib.urlencode({'batch_size': batch_size}))
                )
            else:
                f = urllib.urlopen('%s/%s/%s' % (url, plone.getId(), prefix))
            new_id = f.read()
            f.close()
        except:
            info = exc_info()
            zLOG.LOG('INFO', 0, '',
                     'generate_id raised exception: %s, %s\nURL=%s' % (
                         info[0], info[1], url))
            raise IDServerUnavailable(_('ID Server unavailable'))

        return new_id
