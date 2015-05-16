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

        # ARs get stickers for their respective samples.
        new_items = []
        for i in self.items:
            if i.portal_type == 'AnalysisRequest':
                new_items.append(i.getSample())
            else:
                new_items.append(i)
        self.items = new_items

        # Samples get stickers for their partitions.
        new_items = []
        for i in self.items:
            if i.portal_type == 'Sample':
                new_items += i.objectValues('SamplePartition')
            else:
                new_items.append(i)
        self.items = new_items

        if not self.items:
            logger.warning("Cannot print stickers: no items specified in request")
            self.request.response.redirect(self.context.absolute_url())
            return

        if self.items[0].portal_type == 'SamplePartition':
            template = self.request.get('template', '')
            prefix, tmpl = template.split(':')
            templates_dir = queryResourceDirectory('stickers', prefix).directory

            stickertemplate = ViewPageTemplateFile(os.path.join(templates_dir, tmpl))
            return stickertemplate(self)

        elif self.items[0].portal_type == 'ReferenceSample':
            return self.referencesample_sticker()
