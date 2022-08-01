# -*- coding: utf-8 -*-

from bika.lims import api
from plone.formwidget.namedfile.converter import b64decode_file
from plone.namedfile.browser import Download
from plone.namedfile.file import NamedImage


class SiteLogo(Download):
    def __init__(self, context, request):
        super(SiteLogo, self).__init__(context, request)
        self.filename = None
        self.data = None
        setup = api.get_senaite_setup()
        site_logo = setup.getSiteLogo()
        if site_logo:
            filename, data = b64decode_file(site_logo)
            data = NamedImage(data=data, filename=filename)
            self.data = data
            self.filename = filename
            # self.width, self.height = self.data.getImageSize()

    def _getFile(self):
        return self.data
