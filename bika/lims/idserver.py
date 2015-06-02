from AccessControl import ModuleSecurityInfo, allow_module
from DateTime import DateTime
from Products.Archetypes.public import DisplayList
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.TranslationServiceTool import TranslationServiceTool
from bika.lims.browser import BrowserView
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims import interfaces
from bika.lims import logger
from plone.i18n.normalizer.interfaces import IFileNameNormalizer
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility
from zope.interface import providedBy
import copy,re,urllib
import plone.protect
import transaction

class IDServerUnavailable(Exception):
    pass

def idserver_generate_id(context, prefix, batch_size = None):
    """ Generate a new id using external ID server.
    """
    plone = context.portal_url.getPortalObject()
    url = context.bika_setup.getIDServerURL()

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
            f = urllib.urlopen('%s/%s/%s'%(url, plone.getId(), prefix))
        new_id = f.read()
        f.close()
    except:
        from sys import exc_info
        info = exc_info()
        import zLOG; zLOG.LOG('INFO', 0, '', 'generate_id raised exception: %s, %s \n ID server URL: %s' % (info[0], info[1], url))
        raise IDServerUnavailable(_('ID Server unavailable'))

    return new_id

def generateUniqueId(context):
    """ Generate pretty content IDs.
        - context is used to find portal_type; in case there is no
          prefix specified for the type, the normalized portal_type is
          used as a prefix instead.
    """

    fn_normalize = getUtility(IFileNameNormalizer).normalize
    id_normalize = getUtility(IIDNormalizer).normalize
    prefixes = context.bika_setup.getPrefixes()

    year = context.bika_setup.getYearInPrefix() and \
        DateTime().strftime("%Y")[2:] or ''
    separator = '-'
    for e in prefixes:
        if 'separator' not in e:
            e['separator'] = ''
        if e['portal_type'] == context.portal_type:
            separator = e['separator']

    # Analysis Request IDs
    if context.portal_type == "AnalysisRequest":
        sample = context.getSample()
        s_prefix = fn_normalize(sample.getSampleType().getPrefix())
        sample_padding = context.bika_setup.getSampleIDPadding()
        ar_padding = context.bika_setup.getARIDPadding()
        sample_id = sample.getId()
        sample_number = sample_id.split(s_prefix)[1]
        ar_number = sample.getLastARNumber()
        ar_number = ar_number and ar_number + 1 or 1
        return fn_normalize(
            ("%s%s" + separator + "R%s") % (s_prefix,
                          str(sample_number).zfill(sample_padding),
                          str(ar_number).zfill(ar_padding))
        )

    # Sample Partition IDs
    if context.portal_type == "SamplePartition":
        # We do not use prefixes.  There are actually codes that require the 'P'.
        # matches = [p for p in prefixes if p['portal_type'] == 'SamplePartition']
        # prefix = matches and matches[0]['prefix'] or 'samplepartition'
        # padding = int(matches and matches[0]['padding'] or '0')

        # at this time the part exists, so +1 would be 1 too many
        partnr = str(len(context.aq_parent.objectValues('SamplePartition')))
        # parent id is normalized already
        return ("%s" + separator + "P%s") % (context.aq_parent.id, partnr)

    if context.bika_setup.getExternalIDServer():

        # if using external server

        for d in prefixes:
            # Sample ID comes from SampleType
            if context.portal_type == "Sample":
                prefix = context.getSampleType().getPrefix()
                padding = context.bika_setup.getSampleIDPadding()
                new_id = str(idserver_generate_id(context, "%s%s-" % (prefix, year)))
                if padding:
                    new_id = new_id.zfill(int(padding))
                return ('%s%s' + separator + '%s') % (prefix, year, new_id)
            elif d['portal_type'] == context.portal_type:
                prefix = d['prefix']
                padding = d['padding']
                new_id = str(idserver_generate_id(context, "%s%s-" % (prefix, year)))
                if padding:
                    new_id = new_id.zfill(int(padding))
                return ('%s%s' + separator + '%s') % (prefix, year, new_id)
        # no prefix; use portal_type
        # year is not inserted here
        # portal_type is be normalized to lowercase
        npt = id_normalize(context.portal_type)
        new_id = str(idserver_generate_id(context, npt + "-"))
        return ('%s' + separator + '%s') % (npt, new_id)

    else:

        # No external id-server.

        def next_id(prefix):
            # normalize before anything
            prefix = fn_normalize(prefix)
            plone = context.portal_url.getPortalObject()
            # grab the first catalog we are indexed in.
            at = getToolByName(plone, 'archetype_tool')
            if context.portal_type in at.catalog_map:
                catalog_name = at.catalog_map[context.portal_type][0]
            else:
                catalog_name = 'portal_catalog'
            catalog = getToolByName(plone, catalog_name)

            # get all IDS that start with prefix
            # this must specifically exclude AR IDs (two -'s)
            rr = re.compile("^"+prefix+separator+"[\d+]+$")
            ids = [int(i.split(prefix+separator)[1]) \
                   for i in catalog.Indexes['id'].uniqueValues() \
                   if rr.match(i)]

            #plone_tool = getToolByName(context, 'plone_utils')
            #if not plone_tool.isIDAutoGenerated(l.id):
            ids.sort()
            _id = ids and ids[-1] or 0
            new_id = _id + 1
            return str(new_id)

        for d in prefixes:
            if context.portal_type == "Sample":
                # Special case for Sample IDs
                prefix = fn_normalize(context.getSampleType().getPrefix())
                padding = context.bika_setup.getSampleIDPadding()
                sequence_start = context.bika_setup.getSampleIDSequenceStart()
                new_id = next_id(prefix+year)
                # If sequence_start is greater than new_id. Set
                # sequence_start as new_id. (Jira LIMS-280)
                if sequence_start > int(new_id):
                    new_id = str(sequence_start)
                if padding:
                    new_id = new_id.zfill(int(padding))
                return ('%s%s' + separator + '%s') % (prefix, year, new_id)
            elif d['portal_type'] == context.portal_type:
                prefix = d['prefix']
                padding = d['padding']
                sequence_start = d.get("sequence_start", None)
                new_id = next_id(prefix+year)
                # Jira-tracker LIMS-280
                if sequence_start and int(sequence_start) > int(new_id):
                    new_id = str(sequence_start)
                if padding:
                    new_id = new_id.zfill(int(padding))
                return ('%s%s' + separator + '%s') % (prefix, year, new_id)

        # no prefix; use portal_type
        # no year inserted here
        # use "IID" normalizer, because we want portal_type to be lowercased.
        prefix = id_normalize(context.portal_type);
        new_id = next_id(prefix)
        return ('%s' + separator + '%s') % (prefix, new_id)

def renameAfterCreation(obj):
    # Can't rename without a subtransaction commit when using portal_factory
    transaction.savepoint(optimistic=True)
    # The id returned should be normalized already
    new_id = generateUniqueId(obj)
    obj.aq_inner.aq_parent.manage_renameObject(obj.id, new_id)
    return new_id
