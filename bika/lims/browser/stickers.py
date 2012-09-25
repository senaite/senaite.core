from Products.CMFCore.utils import getToolByName
from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class Sticker(BrowserView):
    """ Invoked via URL on an object, we render a sticker for that object.
        Used manually with a list of objects, renders stickers for all
        provided objects, and invokes a print dialog.
    """
    sample_small = ViewPageTemplateFile("templates/sample_sticker_small.pt")
    sample_large = ViewPageTemplateFile("templates/sample_sticker_large.pt")
    referencesample_sticker = ViewPageTemplateFile("templates/referencesample_sticker.pt")

    def __call__(self):
        bc = getToolByName(self.context, 'bika_catalog')
        items = self.request.get('items', '')
        if items:
            self.items = [o.getObject() for o in bc(id=items.split(","))]
        else:
            self.items = [self.context,]

        # ARs get labels for their respective samples.
        new_items = []
        for i in self.items:
            if i.portal_type == 'AnalysisRequest':
                new_items.append(i.getSample())
            else:
                new_items.append(i)
        self.items = new_items

        # Samples get labels for their partitions.
        new_items = []
        for i in self.items:
            if i.portal_type == 'Sample':
                new_items += i.objectValues('SamplePartition')
            else:
                new_items.append(i)
        self.items = new_items

        if self.items[0].portal_type == 'SamplePartition':
            if self.request.get('size', '') == 'small':
                return self.sample_small()
            else:
                return self.sample_large()
        elif self.items[0].portal_type == 'ReferenceSample':
            return self.referencesample_sticker()
