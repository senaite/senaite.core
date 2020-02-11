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

import re

from bika.lims import api

_marker = object()
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


class Alphanumber(object):
    """Represents an alphanumeric number
    """

    def __init__(self, number=0, num_chars=3, num_digits=3, alphabet=ALPHABET):
        if num_chars < 1:
            raise ValueError("num_chars param is lower than 1")
        if num_digits < 1:
            raise ValueError("num_digits param is lower than 1")

        self.alphabet = alphabet
        self.num_chars = num_chars
        self.num_digits = num_digits
        self.number = to_decimal(number, alphabet=alphabet)

        if self.number < 0:
            # TODO Support for negative values?
            raise ValueError("number is lower than 0")

    @property
    def alpha_format(self):
        return '%sa%sd' % (self.num_chars, self.num_digits)

    def __int__(self):
        return self.number

    def __index__(self):
        return self.__int__()

    def __str__(self):
        return self.__format__(self.alpha_format)

    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        number = self.__int__() + int(other)
        return Alphanumber(number=number, num_chars=self.num_chars,
                           num_digits=self.num_digits, alphabet=self.alphabet)

    def __sub__(self, other):
        number = self.__int__() - int(other)
        return Alphanumber(number=number, num_chars=self.num_chars,
                           num_digits=self.num_digits, alphabet=self.alphabet)

    def __lt__(self, other):
        return self.__int__() < int(other)

    def __gt__(self, other):
        return self.__int__() > int(other)

    def __eq__(self, other):
        return self.__int__() == int(other)

    def __format__(self, format):
        if self.alpha_format != format:
            return to_alpha(self.number, format, self.alphabet).format(format)

        base_format = "{alpha:%s>%s}{number:0%sd}" % (self.alphabet[0],
                                                      self.num_chars,
                                                      self.num_digits)
        alpha, number = self.parts()
        values = dict(alpha=alpha, number=number)
        return base_format.format(**values)

    def format(self, format):
        return self.__format__(format)

    def parts(self):
        """Returns the alphanumeric parts (chars + digits) of this Alphanum
        """
        def get_alpha(alpha_index, alphabet):
            if alpha_index >= len(alphabet):
                lead = get_alpha(alpha_index / len(alphabet), alphabet)
                trail = alphabet[alpha_index % len(alphabet)]
                return "{}{}".format(lead, trail)
            return alphabet[alpha_index]

        max_digits = 10 ** self.num_digits - 1
        alpha_index = abs(self.number) / max_digits
        alpha_number = abs(self.number) % max_digits
        # Note the 1 digit leap e.g. AA99 + 1 == AB01 (not AB00)
        if not alpha_number and abs(self.number):
            alpha_number = max_digits
            alpha_index -= 1

        alpha = get_alpha(alpha_index, self.alphabet)
        if len(alpha) > self.num_chars:
            raise ValueError("Out of bounds. Requires {} chars, {} set"
                             .format(len(alpha), self.num_chars))

        return alpha, alpha_number


def to_alpha(number, format, alphabet=ALPHABET, default=_marker):
    """Returns an Alphanumber object that represents the number in accordance
    with the format specified.
    :param number: a number representation used to create the Alphanumber
    :param format: the format to use. eg. '2a3d' for 2 chars and 3 digits
    :param alphabet: alphabet to use
    :type number: int, string, Alphanumber, float
    :type format: string
    :type alphabet: string
    """
    match = re.match(r"^(\d+)a(\d+)d", format)
    if not match or not match.groups() or len(match.groups()) != 2:
        if default is not _marker:
            return default
        raise ValueError("Format not supported: {}".format(format))
    matches = match.groups()
    num_chars = int(matches[0])
    num_digits = int(matches[1])
    try:
        return Alphanumber(number=number, num_chars=num_chars,
                           num_digits=num_digits, alphabet=alphabet)
    except ValueError as e:
        if default is not _marker:
            return default
        raise e


def to_decimal(alpha_number, alphabet=ALPHABET, default=_marker):
    """Converts an alphanumeric code (e.g AB12) to an integer
    :param alpha_number: representation of an alphanumeric code
    :param alphabet: alphabet to use when alpha_number is a non-int string
    :type number: int, string, Alphanumber, float
    :type alphabet: string
    """
    num = api.to_int(alpha_number, default=None)
    if num is not None:
        return num

    alpha_number = str(alpha_number)
    regex = re.compile(r"([A-Z]+)(\d+)", re.IGNORECASE)
    matches = re.findall(regex, alpha_number)
    if not matches:
        if default is not _marker:
            return default
        raise ValueError("Not a valid alpha number: {}".format(alpha_number))

    alpha = matches[0][0]
    number = int(matches[0][1])
    max_num = 10 ** len(matches[0][1]) - 1
    len_alphabet = len(alphabet)
    for pos_char, alpha_char in enumerate(reversed(alpha)):
        index_char = alphabet.find(alpha_char)
        number += (index_char * max_num * len_alphabet ** pos_char)

    return number
