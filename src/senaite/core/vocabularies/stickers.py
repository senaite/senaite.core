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
    """Provides all available stickers
    """

    def __call__(self, context, filter_by_type=False):
        templates = get_sticker_templates(filter_by_type=filter_by_type)
        return to_simple_vocabulary([(t["id"], t["title"]) for t in templates])


StickerTemplatesVocabularyFactory = StickerTemplatesVocabulary()


def get_sticker_templates(filter_by_type=None):
    """Returns a list of sticker records

    Each sticker record is a dictionary of the following structure:

        {
            "id": <template_id>,
            "title": <template_title>,
        }

    If the template lives outside the senaite.core add-on, both the
    template_id and template_title include a prefix that matches with
    the add-on identifier.

    The template_title is the same name as the id, but with whitespaces and
    without extension.

    As an example, for a template from the my.product add-on located in
    templates/stickers, and with a filename "EAN128_default_small.pt",
    the dictionary will look like:

        {
            "id": "my.product:EAN128_default_small.pt",
            "title": "my.product: EAN128 default small",
        }

    If filter by type is given in the request, only the templates under the
    path with the type name will be fetched.

    Example: If filter_by_type=='worksheet', only *.pt files under a folder
    with this name will be displayed.

    :param filter_by_type: sticker type, e.g. "batch" or "worksheet"
    :returns: list of sticker records
    """
    resdirname = "stickers"
    if filter_by_type:
        fs_path = os.path.join(
            "browser", "stickers", "templates", resdirname, filter_by_type)
    else:
        fs_path = os.path.join("browser", "stickers", "templates", resdirname)

    templates_dir = resource_filename("senaite.core", fs_path)
    templates_subdir = os.path.join(templates_dir, "*.pt")
    templates = [os.path.split(x)[-1] for x in glob.glob(templates_subdir)]

    # Retrieve the templates from other add-ons
    for templates_resource in iterDirectoriesOfType(resdirname):
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
