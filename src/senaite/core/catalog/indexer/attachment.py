# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims import logger
from plone.indexer import indexer
from senaite.core.interfaces import ISimpleFile
from senaite.core.interfaces import ISimpleImage


def extract_text_from_file(blob):
    """Extract text content from a file blob

    This function attempts to extract searchable text from various file types:
    - Plain text files (text/plain, text/html, etc.)
    - PDF files (application/pdf) using portal_transforms with pdftotext
    - Other text-based formats

    :param blob: NamedBlobFile or NamedBlobImage object
    :return: Extracted text as unicode string
    """
    if not blob:
        return u""

    # Get the content type
    content_type = getattr(blob, "contentType", "")
    if not content_type:
        return u""

    # Get the binary data
    data = blob.data
    if not data:
        return u""

    # Handle text files directly
    if content_type.startswith("text/"):
        try:
            # Try to decode as text
            if isinstance(data, bytes):
                # Try common encodings
                for encoding in ["utf-8", "latin-1", "cp1252"]:
                    try:
                        return data.decode(encoding)
                    except (UnicodeDecodeError, AttributeError):
                        continue
            return api.safe_unicode(data)
        except Exception as e:
            logger.warning(
                "Error extracting text from text file: {}".format(str(e))
            )
            return u""

    # Handle PDF files using portal_transforms
    if content_type == "application/pdf":
        try:
            portal_transforms = api.get_tool("portal_transforms")

            # Transform PDF to text using pdftotext (poppler)
            # The transform uses: pdftotext -layout -enc UTF-8 -nopgbrk
            result = portal_transforms.convertTo(
                "text/plain",
                data,
                mimetype="application/pdf",
                filename=getattr(blob, "filename", "file.pdf")
            )

            if result:
                text = result.getData()
                if isinstance(text, bytes):
                    text = text.decode("utf-8", errors="ignore")
                return api.safe_unicode(text)
        except Exception as e:
            logger.warning(
                "Error extracting text from PDF: {}. "
                "Make sure poppler-utils (pdftotext) is installed.".format(
                    str(e)
                )
            )
            return u""

    # For other file types, return empty string
    return u""


@indexer(ISimpleFile)
def listing_searchable_text(instance):
    """Extract searchable text from SimpleFile

    This indexer extracts text content from files for fulltext search.
    It supports:
    - Plain text files
    - PDF files (requires poppler-utils/pdftotext)
    - HTML and other text-based formats

    :param instance: SimpleFile object
    :return: Searchable text including title, description, and file content
    """
    # Collect searchable text parts
    parts = []

    # Add title
    title = api.get_title(instance)
    if title:
        parts.append(api.safe_unicode(title))

    # Add description
    description = instance.description
    if description:
        parts.append(api.safe_unicode(description))

    # Extract text from the file blob
    blob = instance.file
    if blob:
        content = extract_text_from_file(blob)
        if content:
            parts.append(content)

    # Join all parts
    return u" ".join(parts)


@indexer(ISimpleImage)
def listing_searchable_text_image(instance):
    """Extract searchable text from SimpleImage

    This indexer extracts metadata from images for search.
    Images don't have extractable text content, so we index:
    - Title
    - Description

    :param instance: SimpleImage object
    :return: Searchable text including title and description
    """
    # Collect searchable text parts
    parts = []

    # Add title
    title = api.get_title(instance)
    if title:
        parts.append(api.safe_unicode(title))

    # Add description
    description = instance.description
    if description:
        parts.append(api.safe_unicode(description))

    # Join all parts
    return u" ".join(parts)
