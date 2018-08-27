import re

from bika.lims import api

_marker = object()
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


class Alphanumber(object):
    """Represents an alphanumeric number
    """

    def __init__(self, number=0, num_chars=3, num_digits=3, alphabet=ALPHABET):
        self.alpha_str = None
        self.alphabet = alphabet
        self.num_chars = num_chars
        self.num_digits = num_digits
        self.int10 = to_int10(number, alphabet=alphabet)
        self.alpha_format = '%sa%sd' % (self.num_chars, self.num_digits)
        self.alpha_str = self.__format__(self.alpha_format)

    def __int__(self):
        return self.int10

    def __index__(self):
        return self.__int__()

    def __str__(self):
        return self.alpha_str

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
        return self.int10 < int(other)

    def __gt__(self, other):
        return self.int10 > int(other)

    def __eq__(self, other):
        return self.int10 == int(other)

    def __format__(self, format):
        if self.alpha_str and self.alpha_format == format:
            # no need to resolve parts again
            return self.alpha_str

        # Resolve custom format
        match = re.match(r"^(\d+)a(\d+)d", format)
        if not match or not match.groups() or len(match.groups()) != 2:
            raise ValueError("Not a valid format: {}".format(format))

        matches = match.groups()
        num_chars = int(matches[0])
        num_digits = int(matches[1])
        base_format = "{alpha:%s>%s}{number:0%sd}" % (self.alphabet[0],
                                                      num_chars, num_digits)
        alpha, number = get_alpha_parts(number=self.int10, num_chars=num_chars,
                                        num_digits=num_digits,
                                        alphabet=self.alphabet)
        values = dict(alpha=alpha, number=number)
        return base_format.format(**values)

    def format(self, format):
        return self.__format__(format)


def split_parts(alpha_number, default=_marker):
    """Returns the two parts that conforms the alphanumeric number passed in
    """
    num = api.to_int(alpha_number, default=None)
    if num is not None:
        return ('', str(num))

    regex = re.compile(r"([A-Z]+)(\d+)", re.IGNORECASE)
    matches = re.findall(regex, alpha_number)
    if not matches:
        if default is not _marker:
            return default
        raise ValueError("Not a valid alpha number: {}".format(alpha_number))

    return (matches[0][0], matches[0][1])


def is_alphanumeric(alpha_number):
    parts = split_parts(alpha_number, default=None)
    if not parts or not parts[0]:
        return False
    return True


def get_alphanumber(number, format, alphabet=ALPHABET):
    match = re.match(r"(\d+)a(\d+)d", format)
    if not match or not match.groups() or len(match.groups()) != 2:
        raise ValueError("Format not supported: {}".format(format))
    matches = match.groups()
    num_chars = int(matches[0])
    num_digits = int(matches[1])
    return Alphanumber(number=number, num_chars=num_chars,
                       num_digits=num_digits, alphabet=alphabet)


def to_int10(alpha_number, alphabet=ALPHABET, default=_marker):
    """Converts the alphanumeric value to an int (base 10)
    """
    parts = split_parts(alpha_number, default=None)
    if not parts or parts is None:
        if default is not _marker:
            return default
        raise ValueError("Not a valid alpha number: {}".format(alpha_number))
    alpha = parts[0]
    number = int(parts[1])
    max_num = 10 ** len(parts[1]) - 1
    len_alphabet = len(alphabet)
    for pos_char, alpha_char in enumerate(reversed(alpha)):
        index_char = alphabet.find(alpha_char)
        number += (index_char * max_num * len_alphabet ** pos_char)

    return number


def get_alpha_parts(number, num_chars, num_digits, alphabet=ALPHABET):
    """Returns the alphanumeric parts that represents the number passed in
    :param number: integer number
    :param num_chars: number of characters to consider for the alpha part
    :param num_digits: number of digits to consider for the numeric part
    :param alphabet: alphabet to use for the alpha part
    """
    def get_alpha(alpha_index, alphabet):
        if alpha_index >= len(alphabet):
            lead = get_alpha(alpha_index / len(alphabet), alphabet)
            trail = alphabet[alpha_index % len(alphabet)]
            return "{}{}".format(lead, trail)
        return alphabet[alpha_index]

    max_digits = 10 ** num_digits - 1
    alpha_number = max_digits
    alpha_index = 0
    while alpha_number < abs(number):
        alpha_number += max_digits
        alpha_index += 1

    alpha_number = abs(number) - alpha_number + max_digits
    alpha = get_alpha(alpha_index, alphabet)
    if len(alpha) > num_chars:
        raise ValueError("Out of bounds. Requires {} chars, {} set"
                         .format(len(alpha), num_chars))

    return alpha, alpha_number
