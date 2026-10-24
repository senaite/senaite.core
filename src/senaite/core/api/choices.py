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

"""A choices string, as interim fields and analysis conditions write it.

The format is documented in several places as::

    key1:value1|key2:value2|...|keyN:valueN

The key is what gets stored, the value is what the person sees. Parsing
it used to be written out wherever it was needed, four times, in three
different ways: one raised on a value containing a colon, one dropped
such an entry silently, and the one behind analysis conditions never
split at all, so a condition offering "37:37 degC" said exactly that on
screen.

An entry without a colon is its own key and its own label, which is how
most conditions are written today and what keeps them working.
"""

from collections import OrderedDict

ENTRY_SEPARATOR = "|"
KEY_SEPARATOR = ":"


def to_choices(choices):
    """Parse a choices string into an ordered mapping of key to label.

    :param choices: the raw string, or anything falsy for no choices
    :returns: an OrderedDict of key to label, empty when there are none
    """
    parsed = OrderedDict()
    for entry in (choices or "").split(ENTRY_SEPARATOR):
        entry = entry.strip()
        if not entry:
            continue
        # Only the first colon separates: a label may contain more, and
        # splitting on every one of them is what used to raise.
        parts = entry.split(KEY_SEPARATOR, 1)
        key = parts[0].strip()
        label = parts[1].strip() if len(parts) > 1 else key
        parsed[key] = label
    return parsed


def to_options(choices):
    """Parse a choices string into a list of option dicts.

    :param choices: the raw string, or anything falsy for no choices
    :returns: a list of {"value": key, "text": label}, in the order the
        choices were written
    """
    return [{"value": key, "text": label}
            for key, label in to_choices(choices).items()]


def get_label(choices, value):
    """Return the label a stored value stands for.

    A value that is not among the keys is returned unchanged. Conditions
    stored before the key form was understood hold the label itself, and
    they have to keep reading the way they were written.

    :param choices: the raw choices string
    :param value: the stored value
    :returns: the label to show
    """
    return to_choices(choices).get(value, value)
