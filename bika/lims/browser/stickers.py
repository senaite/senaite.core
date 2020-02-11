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

import os
import os.path
import tempfile
import traceback

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.browser import BrowserView
from bika.lims.interfaces import IGetStickerTemplates
from bika.lims.utils import createPdf
from bika.lims.utils import to_int
from bika.lims.vocabularies import getStickerTemplates
from plone.resource.utils import queryResourceDirectory
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.supermodel import SuperModel
from zope.component import getAdapters
from zope.component.interfaces import ComponentLookupError


class Sticker(BrowserView):
    """Invoked via URL on an object or list of objects from the types
       AnalysisRequest, Sample or ReferenceSample.

       Renders a preview for the objects, a control to allow the user to
       select the sticker template to be invoked and print.

       In order to create a sticker inside an Add-on you have to create a
       directory inside the resource directory

       This defines the resource folder to look for:

       - path: addon/stickers/configure.zcml
           ...
           **Defining stickers for samples, analysisrequests and partitions
           <plone:static
             directory="templates"
             type="stickers"
             name="ADDON stickers" />
           ...

       This is how to add general stickers for samples:

       - addon/stickers/templates/

           -- code_39_40x20mm.{css,pt}
           -- other_{sample,ar,partition}_stickers_...

       This is the way to create specific sticker for a content type.

       Note that in this case the directory '/worksheet' should contain the
       sticker templates for worksheet objects.

       - addon/stickers/templates/worksheet
           -- code_...mm.{css,pt}
           -- other_worksheet_stickers_...
    """
    template = ViewPageTemplateFile("templates/stickers_preview.pt")

    def __init__(self, context, request):
        super(Sticker, self).__init__(context, request)
        self.context = context
        self.request = request
        self.current_item = None

    def __call__(self):
        # Need to generate a PDF with the stickers?
        if self.request.form.get("pdf", "0") == "1":
            response = self.request.response
            response.setHeader("Content-type", "application/pdf")
            response.setHeader("Content-Disposition", "inline")
            response.setHeader("filename", "sticker.pdf")
            pdfstream = self.pdf_from_post()
            return pdfstream

        # If filter by type is given in the request, only the templates under
        # the path with the type name will be given as vocabulary.
        # Example: If filter_by_type=='worksheet', only *.pt files under a
        # folder with filter_by_type as name will be displayed.
        self.filter_by_type = self.request.get("filter_by_type", False)

        self.items = self.get_items()
        if not self.items:
            logger.warning(
                "Cannot print stickers: no items specified in request")
            self.request.response.redirect(self.context.absolute_url())
            return

        return self.template()

    def get_items(self):
        """Returns a list of SuperModel items
        """
        uids = self.get_uids()
        if not uids:
            return [SuperModel(self.context)]
        items = map(lambda uid: SuperModel(uid), uids)
        return self._resolve_number_of_copies(items)

    def get_uids(self):
        """Parse the UIDs from the request `items` parameter
        """
        return filter(None, self.request.get("items", "").split(","))

    def getAvailableTemplates(self):
        """Returns an array with the templates of stickers available.

        Each array item is a dictionary with the following structure:

            {'id': <template_id>,
            'title': <teamplate_title>,
            'selected: True/False'}
        """
        # Getting adapters for current context. those adapters will return
        # the desired sticker templates for the current context:
        try:
            adapters = getAdapters((self.context, ), IGetStickerTemplates)
        except ComponentLookupError:
            logger.info("No IGetStickerTemplates adapters found.")
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
            out["selected"] = temp.get("id", "") == seltemplate
            templates.append(out)
        return templates

    def getSelectedTemplate(self, default="Code_39_40x20mm.pt"):
        """Returns the id of the sticker template selected.

        If no specific template found in the request (parameter template),
        returns the default template set in Setup > Stickers.

        If the template doesn't exist, uses the default template.

        If no template selected but size param, get the sticker template set as
        default in Bika Setup for the size set.
        """
        # Default sticker
        bs_template = self.context.bika_setup.getAutoStickerTemplate()
        size = self.request.get("size", "")

        if self.filter_by_type:
            templates = getStickerTemplates(filter_by_type=self.filter_by_type)
            # Get the first sticker
            bs_template = templates[0].get("id", "") if templates else ""
        elif size == "small":
            bs_template = self.context.bika_setup.getSmallStickerTemplate()
        elif size == "large":
            bs_template = self.context.bika_setup.getLargeStickerTemplate()
        rq_template = self.request.get("template", bs_template)
        # Check if the template exists. If not, fallback to default's
        # 'prefix' is also the resource folder's name
        prefix = ""
        templates_dir = ""
        if rq_template.find(":") >= 0:
            prefix, rq_template = rq_template.split(":")
            templates_dir = self._getStickersTemplatesDirectory(prefix)
        else:
            this_dir = os.path.dirname(os.path.abspath(__file__))
            templates_dir = os.path.join(this_dir, "templates/stickers/")
            if self.filter_by_type:
                templates_dir = templates_dir + "/" + self.filter_by_type
        if not os.path.isfile(os.path.join(templates_dir, rq_template)):
            rq_template = default
        return "%s:%s" % (prefix, rq_template) if prefix else rq_template

    def getSelectedTemplateCSS(self):
        """Looks for the CSS file from the selected template and return its
           contents.

        If the selected template is default.pt, looks for a file named
        default.css in the stickers path and return its contents. If no CSS
        file found, retrns an empty string
        """
        template = self.getSelectedTemplate()
        # Look for the CSS
        content = ""
        if template.find(":") >= 0:
            # A template from another add-on
            prefix, template = template.split(":")
            templates_dir = self._getStickersTemplatesDirectory(prefix)
            css = "{0}.css".format(template[:-3])
            if css in os.listdir(templates_dir):
                path = "%s/%s.css" % (templates_dir, template[:-3])
                if os.path.isfile(path):
                    with open(path, "r") as content_file:
                        content = content_file.read()
        else:
            this_dir = os.path.dirname(os.path.abspath(__file__))
            templates_dir = os.path.join(this_dir, "templates/stickers/")
            # Only use the directory asked in "filter_by_type"
            if self.filter_by_type:
                templates_dir = templates_dir + "/" + self.filter_by_type
            path = "%s/%s.css" % (templates_dir, template[:-3])
            if os.path.isfile(path):
                with open(path, "r") as content_file:
                    content = content_file.read()
        return content

    def renderItem(self, item):
        """Renders the next available sticker.

        Uses the template specified in the request ('template' parameter) by
        default. If no template defined in the request, uses the default
        template set by default in Setup > Stickers.

        If the template specified doesn't exist, uses the default bika.lims'
        Code_128_1x48mm.pt template (was sticker_small.pt).
        """
        self.current_item = item
        templates_dir = "templates/stickers"
        embedt = self.getSelectedTemplate()
        if embedt.find(":") >= 0:
            prefix, embedt = embedt.split(":")
            templates_dir = self._getStickersTemplatesDirectory(prefix)
        elif self.filter_by_type:
            templates_dir = "/".join([templates_dir, self.filter_by_type])
        fullpath = os.path.join(templates_dir, embedt)

        try:
            embed = ViewPageTemplateFile(fullpath)
            return embed(self, item=item)
        except Exception:
            exc = traceback.format_exc()
            msg = "<div class='error'>{} - {} '{}':<pre>{}</pre></div>".format(
                item.id, _("Failed to load sticker"), embedt, exc)
            return msg

    def getItemsURL(self):
        """Used in stickers_preview.pt
        """
        req_items = self.get_uids()
        req_items = req_items or [api.get_uid(self.context)]
        req = "{}?items={}".format(self.request.URL, ",".join(req_items))
        return req

    def _getStickersTemplatesDirectory(self, resource_name):
        """Returns the paths for the directory containing the css and pt files
        for the stickers deppending on the filter_by_type.

        :param resource_name: The name of the resource folder.
        :type resource_name: string
        :returns: a string as a path
        """
        templates_dir =\
            queryResourceDirectory("stickers", resource_name).directory
        if self.filter_by_type:
            templates_dir = templates_dir + "/" + self.filter_by_type
        return templates_dir

    def pdf_from_post(self):
        """Returns a pdf stream with the stickers
        """
        html = self.request.form.get("html")
        style = self.request.form.get("style")
        reporthtml = "<html><head>{0}</head><body>{1}</body></html>"
        reporthtml = reporthtml.format(style, html)
        reporthtml = safe_unicode(reporthtml).encode("utf-8")
        pdf_fn = tempfile.mktemp(suffix=".pdf")
        pdf_file = createPdf(htmlreport=reporthtml, outfile=pdf_fn)
        return pdf_file

    def _resolve_number_of_copies(self, items):
        """For the given objects generate as many copies as the desired number
        of stickers.

        :param items: list of objects whose stickers are going to be previewed.
        :type items: list
        :returns: list containing n copies of each object in the items list
        :rtype: list
        """
        copied_items = []
        for obj in items:
            for copy in range(self.get_copies_count()):
                copied_items.append(obj)
        return copied_items

    def get_copies_count(self):
        """Return the copies_count number request parameter

        :returns: the number of copies for each sticker as stated
        in the request
        :rtype: int
        """
        setup = api.get_setup()
        default_num = setup.getDefaultNumberOfCopies()
        request_num = self.request.form.get("copies_count")
        return to_int(request_num, default_num)
