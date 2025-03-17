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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

import glob
import os

from pkg_resources import resource_filename
from plone.resource.utils import iterDirectoriesOfType
from senaite.core.schema.vocabulary import to_simple_vocabulary
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory


@implementer(IVocabularyFactory)
class StickerTemplatesVocabulary(object):
    """Provides available stickers
    """

    def __call__(self, context, filter_by_type=False):
        templates = get_sticker_templates(filter_by_type=filter_by_type)
        return to_simple_vocabulary([(t["id"], t["title"]) for t in templates])


StickerTemplatesVocabularyFactory = StickerTemplatesVocabulary()


def get_sticker_templates(filter_by_type=False):
    """Returns an array with the sticker templates available. Retrieves the
        TAL templates saved in templates/stickers folder.

    Each array item is a dictionary with the following structure:

        {
            "id": <template_id>,
            "title": <template_title>,
        }

    If the template lives outside the senaite.core add-on, both the
    template_id and template_title include a prefix that matches with
    the add-on identifier. template_title is the same name as the id,
    but with whitespaces and without extension.

    As an example, for a template from the my.product add-on located in
    templates/stickers, and with a filename "EAN128_default_small.pt",
    the dictionary will look like:

        {
            'id': 'my.product:EAN128_default_small.pt',
            'title': 'my.product: EAN128 default small',
        }

    If filter by type is given in the request, only the templates under
    the path with the type name will be rendered given as vocabulary.
    Example: If filter_by_type=='worksheet', only *.tp files under a
    folder with this name will be displayed.

    :param filter_by_type:
    :type filter_by_type: string/bool.
    :returns: an array with the sticker templates available
    """
    # Retrieve the templates from bika.lims add-on
    # resdirname

    resdirname = "stickers"
    if filter_by_type:
        fs_path = os.path.join(
            "browser", "templates", resdirname, filter_by_type)
    else:
        fs_path = os.path.join("browser", "stickers", "templates", resdirname)
    # getTemplates needs two parameters, the first one is the bikalims path
    # where the stickers will be found. The second one is the resource
    # directory type. This allows us to filter stickers by the type we want.
    return get_templates(fs_path, resdirname, filter_by_type)


def get_templates(fs_path, restype, filter_by_type=False):
    """ Returns an array with the Templates available in the Bika LIMS path
        specified plus the templates from the resources directory specified and
        available on each additional product (restype).

        Each array item is a dictionary with the following structure:
            {'id': <template_id>,
            'title': <template_title>}

        If the template lives outside the bika.lims add-on, both the template_id
        and template_title include a prefix that matches with the add-on
        identifier. template_title is the same name as the id, but with
        whitespaces and without extension.

        As an example, for a template from the my.product add-on located in
        <restype> resource dir, and with a filename "My_cool_report.pt",
    the dictionary will look like:
            {'id': 'my.product:My_cool_report.pt',
            'title': 'my.product: My cool report'}

        :param fs_path: the path inside bika lims to find the stickers.
        :type fs_path: an string as a path
        :param restype: the resource directory type to search for inside
            an addon.
        :type restype: string
        :param filter_by_type: the folder name to look for inside the
        templates path
        :type filter_by_type: string/boolean
    """
    # Retrieve the templates from bika.lims add-on
    templates_dir = resource_filename("senaite.core", fs_path)
    tempath = os.path.join(templates_dir, "*.pt")
    templates = [os.path.split(x)[-1] for x in glob.glob(tempath)]

    # Retrieve the templates from other add-ons
    for templates_resource in iterDirectoriesOfType(restype):
        prefix = templates_resource.__name__
        if prefix == "senaite.core":
            continue
        directory = templates_resource.directory
        # Only use the directory asked in "filter_by_type"
        if filter_by_type:
            directory = directory + "/" + filter_by_type
        if os.path.isdir(directory):
            dirlist = os.listdir(directory)
            exts = ["{0}:{1}".format(prefix, tpl) for tpl in dirlist if
                    tpl.endswith(".pt")]
            templates.extend(exts)

    out = []
    templates.sort()
    for template in templates:
        title = template[:-3]
        title = title.replace("_", " ")
        title = title.replace(":", ": ")
        out.append({"id": template,
                    "title": title})

    return out
