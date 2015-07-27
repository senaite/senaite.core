from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _, t
from bika.lims import logger
from bika.lims.browser import BrowserView
from bika.lims.vocabularies import getStickerTemplates
from plone.resource.utils import iterDirectoriesOfType, queryResourceDirectory
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
import glob, os, os.path, sys, traceback

import os

class Sticker(BrowserView):
    """ Invoked via URL on an object or list of objects from the types
        AnalysisRequest, Sample, SamplePartition or ReferenceSample.
        Renders a preview for the objects, a control to allow the user to
        select the stcker template to be invoked and print.
    """
    template = ViewPageTemplateFile("templates/stickers_preview.pt")
    item_index = 0
    current_item = None

    def __call__(self):
        bc = getToolByName(self.context, 'bika_catalog')
        items = self.request.get('items', '')
        if items:
            self.items = [o.getObject() for o in bc(id=items.split(","))]
        else:
            self.items = [self.context,]

        new_items = []
        for i in self.items:
            outitems = self._populateItems(i)
            new_items.extend(outitems)

        self.items = new_items
        if not self.items:
            logger.warning("Cannot print stickers: no items specified in request")
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
        """
        ar = None
        sample = None
        parts = []
        if item.portal_type == 'AnalysisRequest':
            ar = item
            sample = item.getSample()
            parts = sample.objectValues('SamplePartition')
        elif item.portal_type == 'Sample':
            sample = item
            parts = sample.objectValues('SamplePartition')
        elif item.portal_type == 'SamplePartition':
            sample = item.aq_parent
            parts = [item,]
        elif item.portal_type == 'ReferenceSample':
            sample = item

        items = []
        for p in parts:
            items.append([ar, sample, p])
        return items

    def getAvailableTemplates(self):
        """ Returns an array with the templates of stickers available. Each
            array item is a dictionary with the following structure:
                {'id': <template_id>,
                 'title': <teamplate_title>,
                 'selected: True/False'}
        """
        seltemplate = self.getSelectedTemplate()
        templates = []
        for temp in getStickerTemplates():
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
        bs_template = self.context.bika_setup.getAutoStickerTemplate()
        size = self.request.get('size', '')
        if size == 'small':
            bs_template = self.context.bika_setup.getSmallStickerTemplate()
        elif size == 'large':
            bs_template = self.context.bika_setup.getLargeStickerTemplate()
        rq_template = self.request.get('template', bs_template)
        # Check if the template exists. If not, fallback to default's
        if rq_template.find(':') >= 0:
            prefix, rq_template = rq_template.split(':')
            templates_dir = queryResourceDirectory('stickers', prefix).directory
        else:
            this_dir = os.path.dirname(os.path.abspath(__file__))
            templates_dir = os.path.join(this_dir, 'templates/stickers/')
        if not os.path.isfile(os.path.join(templates_dir, rq_template)):
            rq_template = 'Code_128_1x48mm.pt'
        return rq_template

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
            resource = queryResourceDirectory('stickers', prefix)
            css = '{0}.css'.format(template[:-3])
            if css in resource.listDirectory():
                content = resource.readFile(css)
        else:
            this_dir = os.path.dirname(os.path.abspath(__file__))
            templates_dir = os.path.join(this_dir, 'templates/stickers/')
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
            self.item_index = 0;
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
            templates_dir = queryResourceDirectory('stickers', prefix).directory
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
