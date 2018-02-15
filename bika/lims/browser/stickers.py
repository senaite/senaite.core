# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _, t
from bika.lims import logger
from bika.lims.browser import BrowserView
from zope.component.interfaces import ComponentLookupError
from bika.lims.utils import createPdf, to_int
from bika.lims.vocabularies import getStickerTemplates
from plone.resource.utils import iterDirectoriesOfType, queryResourceDirectory
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
import glob, os, os.path, sys, traceback
from bika.lims.interfaces import IGetStickerTemplates
from zope.component import getAdapters

import os
import App
import tempfile


class Sticker(BrowserView):
    """ Invoked via URL on an object or list of objects from the types
        AnalysisRequest, Sample, SamplePartition or ReferenceSample.
        Renders a preview for the objects, a control to allow the user to
        select the stcker template to be invoked and print.

        In order to create a sticker inside an Add-on you have to create a
        directory inside the resource directory. Look at those examples:
        This defines the resource folder to look for.
        - path: bika/addon/stickers/configure.zcml
            ...
            **Defining stickers for samples, analysisrequests and partitions
            <plone:static
              directory="templates"
              type="stickers"
              name="ADDON stickers" />
            ...
        This is how to add general stickers for analysis requests, samples
        and partitions.
        - bika/addon/stickers/templates/
            -- code_39_40x20mm.{css,pt}
            -- other_{sample,ar,partition}_stickers_...

        This is the wasy to create specific sticker for a content type.
        Note that in this case the directory '/worksheet' should contain the
        sticker templates for worksheet objects.
        - bika/addon/stickers/templates/worksheet
            -- code_...mm.{css,pt}
            -- other_worksheet_stickers_...
    """
    template = ViewPageTemplateFile("templates/stickers_preview.pt")

    def __init__(self, context, request):
        super(Sticker, self).__init__(context, request)
        self.item_index = 0
        self.current_item = None
        self.copies_count = None
        self.context = context
        self.request = request

    def __call__(self):
        # Need to generate a PDF with the stickers?
        if self.request.form.get('pdf', '0') == '1':
            response = self.request.response
            response.setHeader('Content-type', 'application/pdf')
            response.setHeader('Content-Disposition', 'inline')
            response.setHeader('filename', 'sticker.pdf')
            pdfstream = self.pdf_from_post()
            return pdfstream

        self.copies_count = self.get_copies_count()

        items = self.request.get('items', '')
        # If filter by type is given in the request, only the templates under
        # the path with the type name will be given as vocabulary.
        # Example: If filter_by_type=='worksheet', only *.tp files under a
        # folder with filter_by_type as name will be displayed.
        self.filter_by_type = self.request.get('filter_by_type', False)
        catalog = getToolByName(self.context, 'uid_catalog')
        self.items = [o.getObject() for o in catalog(UID=items.split(","))]
        if not self.items:
            # Default fallback, load from context
            self.items = [self.context, ]

        # before retrieving the required data for each type of object copy
        # each object as many times as the number of desired sticker copies
        self.items = self._resolve_number_of_copies(self.items)
        new_items = []
        for i in self.items:
            outitems = self._populateItems(i)
            new_items.extend(outitems)

        self.items = new_items
        if not self.items:
            logger.warning(
                "Cannot print stickers: no items specified in request")
            self.request.response.redirect(self.context.absolute_url())
            return

        return self.template()

    def _populateItems(self, item):
        """ Creates an wel-defined array for this item to make the sticker
            template easy to render. Each position of the array has a secondary
            array, one per partition.

            If the item is an object from an AnalysisRequest type, returns an
            array with the following structure:
                [
                 [ar_object, ar_sample, ar_sample_partition-1],
                 [ar_object, ar_sample, ar_sample_partition-2],
                 ...
                 [ar_object, ar_sample, ara_sample_partition-n]
                ]

            If the item is an object from Sample type, returns an arary with the
            following structure:
                [
                 [None, sample, sample_partition-1],
                 [None, sample, sample_partition-2],
                 ...
                ]
            If the item is an object from ReferenceSample type, returns an
            array with the following structure:
                [[None, refsample, None]]
            Note that in this case, the array always have a length=1

            If the type of the item is a worksheet, returns an iterable with
            the following structure:
                [[None, AssignedAnalyst, workhseet]]

            If the type of the item is a worksheet, returns an iterable with
            the following structure:
                [[None, None, batch]]
        """
        ar = None
        sample = None
        parts = []
        portal_type = item.portal_type
        if portal_type == 'AnalysisRequest':
            ar = item
            sample = item.getSample()
            parts = sample.objectValues('SamplePartition')
        elif portal_type == 'Sample':
            sample = item
            parts = sample.objectValues('SamplePartition')
        elif portal_type == 'SamplePartition':
            sample = item.aq_parent
            parts = [item, ]
        elif portal_type == 'ReferenceSample':
            sample = item
        elif portal_type == 'Worksheet':
            return [[None, item.getAnalystName(), item]]
        elif portal_type == 'Batch':
            return [[None, None, item]]
        items = []
        for part in parts:
            items.append([ar, sample, part])
        return items

    def getAvailableTemplates(self):
        """ Returns an array with the templates of stickers available. Each
            array item is a dictionary with the following structure:
                {'id': <template_id>,
                 'title': <teamplate_title>,
                 'selected: True/False'}
        """
        # Getting adapters for current context. those adapters will return
        # the desired sticker templates for the current context:
        try:
            adapters = getAdapters((self.context, ), IGetStickerTemplates)
        except ComponentLookupError:
            logger.info('No IGetStickerTemplates adapters found.')
            adapters = None
        templates = []
        if adapters is not None:
            # Gather all templates
            for name, adapter in adapters:
                templates += adapter(self.request)
        if templates:
            return templates
        # If there are no adapters, get all sticker templates in the system
        seltemplate = self.getSelectedTemplate()
        for temp in getStickerTemplates(filter_by_type=self.filter_by_type):
            out = temp
            out['selected'] = temp.get('id', '') == seltemplate
            templates.append(out)
        return templates

    def getSelectedTemplate(self):
        """ Returns the id of the sticker template selected. If no specific
            template found in the request (parameter template), returns the
            default template set in Bika Setup > Stickers.
            If the template doesn't exist, uses the default bika.lims'
            Code_128_1x48mm.pt template (was sticker_small.pt).
            If no template selected but size param, get the sticker template
            set as default in Bika Setup for the size set.
        """
        # Default sticker
        bs_template = self.context.bika_setup.getAutoStickerTemplate()
        size = self.request.get('size', '')
        resource_type = 'stickers'
        if self.filter_by_type:
            templates = getStickerTemplates(filter_by_type=self.filter_by_type)
            # Get the first sticker
            bs_template = templates[0].get('id', '') if templates else ''
        elif size == 'small':
            bs_template = self.context.bika_setup.getSmallStickerTemplate()
        elif size == 'large':
            bs_template = self.context.bika_setup.getLargeStickerTemplate()
        rq_template = self.request.get('template', bs_template)
        # Check if the template exists. If not, fallback to default's
        # 'prefix' is also the resource folder's name
        prefix = ''
        templates_dir = ''
        if rq_template.find(':') >= 0:
            prefix, rq_template = rq_template.split(':')
            templates_dir = self._getStickersTemplatesDirectory(prefix)
        else:
            this_dir = os.path.dirname(os.path.abspath(__file__))
            templates_dir = os.path.join(this_dir, 'templates/stickers/')
            if self.filter_by_type:
                templates_dir = templates_dir + '/' + self.filter_by_type
        if not os.path.isfile(os.path.join(templates_dir, rq_template)):
            rq_template = 'Code_128_1x48mm.pt'
        return '%s:%s' % (prefix, rq_template) if prefix else rq_template

    def getSelectedTemplateCSS(self):
        """ Looks for the CSS file from the selected template and return its
            contents. If the selected template is default.pt, looks for a
            file named default.css in the stickers path and return its contents.
            If no CSS file found, retrns an empty string
        """
        template = self.getSelectedTemplate()
        # Look for the CSS
        content = ''
        if template.find(':') >= 0:
            # A template from another add-on
            prefix, template = template.split(':')
            templates_dir = self._getStickersTemplatesDirectory(prefix)
            css = '{0}.css'.format(template[:-3])
            if css in os.listdir(templates_dir):
                path = '%s/%s.css' % (templates_dir, template[:-3])
                if os.path.isfile(path):
                    with open(path, 'r') as content_file:
                        content = content_file.read()
        else:
            this_dir = os.path.dirname(os.path.abspath(__file__))
            templates_dir = os.path.join(this_dir, 'templates/stickers/')
            # Only use the directory asked in 'filter_by_type'
            if self.filter_by_type:
                templates_dir = templates_dir + '/' + self.filter_by_type
            path = '%s/%s.css' % (templates_dir, template[:-3])
            if os.path.isfile(path):
                with open(path, 'r') as content_file:
                    content = content_file.read()
        return content

    def nextItem(self):
        """ Iterates to the next item in the list and moves one position up the
            item index. If the end of the list of items is reached, returns the
            first item of the list.
        """
        if self.item_index == len(self.items):
            self.item_index = 0
        self.current_item = self.items[self.item_index]
        self.item_index += 1
        return self.current_item

    def renderItem(self):
        """ Renders the next available sticker.
            Uses the template specified in the request ('template' parameter) by
            default. If no template defined in the request, uses the default
            template set by default in Bika Setup > Stickers.
            If the template specified doesn't exist, uses the default
            bika.lims' Code_128_1x48mm.pt template (was sticker_small.pt).
        """
        curritem = self.nextItem()
        templates_dir = 'templates/stickers'
        embedt = self.getSelectedTemplate()
        if embedt.find(':') >= 0:
            prefix, embedt = embedt.split(':')
            templates_dir = self._getStickersTemplatesDirectory(prefix)
        elif self.filter_by_type:
            templates_dir = '/'.join([templates_dir, self.filter_by_type])
        fullpath = os.path.join(templates_dir, embedt)
        try:
            embed = ViewPageTemplateFile(fullpath)
            return embed(self)
        except:
            tbex = traceback.format_exc()
            stickerid = curritem[2].id if curritem[2] else curritem[1].id
            return "<div class='error'>%s - %s '%s':<pre>%s</pre></div>" % \
                    (stickerid, _("Unable to load the template"), embedt, tbex)

    def getItemsURL(self):
        req_items = self.request.get('items', '')
        req_items = req_items if req_items else self.context.getId()
        req = '%s?items=%s' % (self.request.URL, req_items)
        return req

    def getClientFromCurrentItem(self):
        """
        This function tries to return the client from the current item.
        :returns: A client object or None.
        :rtype: ATContentType/NoneType
        """
        # 'current' will be an array such as [None, sample, sample_partition-1]
        current = self.current_item
        # Since the second item in the array is always a sample or reference
        # sample, we can start getting it in order to get the client.
        sample = current[1]
        ars = sample.getAnalysisRequests()
        if not ars:
            return None
        # Getting the real client object
        client = ars[0].aq_parent.aq_inner
        return client

    def _getStickersTemplatesDirectory(self, resource_name):
        """
        Returns the paths for the directory containing the css and pt files
        for the stickers deppending on the filter_by_type.
        :param resource_name: The name of the resource folder.
        :type resource_name: string
        :returns: a string as a path
        """
        templates_dir =\
            queryResourceDirectory('stickers', resource_name).directory
        if self.filter_by_type:
            templates_dir = templates_dir + '/' + self.filter_by_type
        return templates_dir

    def pdf_from_post(self):
        """Returns a pdf stream with the stickers
        """
        html = self.request.form.get('html')
        style = self.request.form.get('style')
        reporthtml = '<html><head>{0}</head><body>{1}</body></html>'
        reporthtml = reporthtml.format(style, html)
        reporthtml = safe_unicode(reporthtml).encode('utf-8')
        pdf_fn = tempfile.mktemp(suffix='.pdf')
        pdf_file = createPdf(htmlreport=reporthtml, outfile=pdf_fn)
        return pdf_file

    def _resolve_number_of_copies(self, items):
        """For the given objects generate as many copies as the desired
        number of stickers. The desired number of stickers for each
        object is given by copies_count

        :param items: list of objects whose stickers are going to be previewed.
        :type items: list
        :returns: list containing n copies of each object in the items list,
        where n is self.copies_count
        :rtype: list
        """
        copied_items = []
        for obj in items:
            for copy in range(self.copies_count):
                copied_items.append(obj)
        return copied_items

    def get_copies_count(self):
        """Return the copies_count number request parameter

        :returns: the number of copies for each sticker as stated
        in the request
        :rtype: int
        """
        default_num = self.context.bika_setup.getDefaultNumberOfCopies()
        request_num = self.request.form.get("copies_count")
        return to_int(request_num, default_num)
