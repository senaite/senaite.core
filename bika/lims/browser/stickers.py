from Products.CMFCore.utils import getToolByName
from bika.lims import logger
from bika.lims.browser import BrowserView
from plone.resource.utils import iterDirectoriesOfType, queryResourceDirectory
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

import os

class Sticker(BrowserView):
    """ Invoked via URL on an object, we render a sticker for that object.
        Used manually with a list of objects, renders stickers for all
        provided objects, and invokes a print dialog.
    """
    #sample_small = ViewPageTemplateFile("templates/sample_sticker_small.pt")
    #sample_large = ViewPageTemplateFile("templates/sample_sticker_large.pt")
    #referencesample_sticker = ViewPageTemplateFile("templates/referencesample_sticker.pt")

    def __call__(self):
        bc = getToolByName(self.context, 'bika_catalog')
        items = self.request.get('items', '')
        if items:
            self.items = [o.getObject() for o in bc(id=items.split(","))]
        else:
            self.items = [self.context,]

        """
        A given sample can be used in more than one Analysis Request
        via secondary AR creation, so in case we want to print the AR-ID
        together with the Sample ID, we cannot throw out the ARs.

        a) For posted items from AnalysisRequest type, populates an array
        where each item is an array of objects as follows:
            [ar, sample, partition]

        b) For posted items from Sample type, populates an array as follows:
            [None, sample, partition]

        c) For posted items from ReferenceSample type, populates an array:
            [None, refsample, None]
        """
        new_items = []
        for i in self.items:
            outitems = self._populateItems(i)
            new_items.extend(outitems)

        self.items = new_items
        if not self.items:
            logger.warning("Cannot print stickers: no items specified in request")
            self.request.response.redirect(self.context.absolute_url())
            return

        template = self.request.get('template', '')
        prefix, tmpl = template.split(':')
        templates_dir = queryResourceDirectory('stickers', prefix).directory
        stickertemplate = ViewPageTemplateFile(os.path.join(templates_dir, tmpl))
        return stickertemplate(self)

    def _populateItems(self, item):
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

        items = []
        for p in parts:
            items.append([ar, sample, p])
        return items


    def StickerFormatCode(self):
        # It'll be used in a condition to know which sticker type should be rendered
        return self.context.bika_setup.getCodeBarType()
