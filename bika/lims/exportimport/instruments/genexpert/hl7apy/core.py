# -*- coding: utf-8 -*-
#
# Copyright (c) 2012-2015, CRS4
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
HL7apy - core classes
"""

from __future__ import absolute_import
import re
import collections
import datetime
from itertools import takewhile
import importlib

from bika.lims.exportimport.instruments.genexpert.hl7apy import get_default_version, get_default_encoding_chars, \
    get_default_validation_level, check_validation_level, \
    check_encoding_chars, check_version, load_library, \
    find_reference, load_reference
from bika.lims.exportimport.instruments.genexpert.hl7apy.validation import Validator
from bika.lims.exportimport.instruments.genexpert.hl7apy.exceptions import ChildNotFound, ChildNotValid, \
    MaxChildLimitReached, OperationNotAllowed, \
    InvalidName, MessageProfileNotFound
from bika.lims.exportimport.instruments.genexpert.hl7apy.factories import datatype_factory
from bika.lims.exportimport.instruments.genexpert.hl7apy.base_datatypes import BaseDataType
from bika.lims.exportimport.instruments.genexpert.hl7apy.consts import MLLP_ENCODING_CHARS
from bika.lims.exportimport.instruments.genexpert.hl7apy.utils import iteritems

try:
    basestring = basestring
except NameError:
    basestring = (str, bytes)

try:
    xrange = xrange
except NameError:
    xrange = range


def is_base_datatype(datatype, version=None):
    """
    Check if the given datatype is a base datatype of the specified version

    :type datatype: ``str``
    :param datatype: the datatype (e.g. ST)

    :type version: ``str``
    :param version: the HL7 version (e.g. 2.5)

    :return: ``True`` if it is a base datatype, ``False`` otherwise

    >>> is_base_datatype('ST')
    True
    >>> is_base_datatype('CE')
    False
    """
    if version is None:
        version = get_default_version()
    lib = load_library(version)
    return lib.is_base_datatype(datatype)


def _remove_trailing(children):
    trailing = list(takewhile(lambda x: not x, reversed(children)))
    if len(trailing) > 0:
        children = children[:-len(trailing)]
    return children


def _valid_child_name(child_name, expected_parent):
    try:
        parent, index = child_name.split("_")
        int(index)
    except (ValueError, AttributeError):
        return False
    else:
        if str(parent).upper() != str(expected_parent).upper():
            return False
        return True


def _valid_z_message_name(name):
    if name is None:
        return False
    regex = '^z[a-z0-9]{2}_z[a-z0-9]{2}$'
    return re.match(regex, name, re.IGNORECASE) is not None


def _valid_z_segment_name(name):
    return name.upper().startswith('Z') and len(name) == 3


def _valid_z_field_name(name):
    regex = '^z[a-z1-9]{2}_\d+$'
    return re.match(regex, name, re.IGNORECASE) is not None


class ElementProxy(collections.Sequence):
    """
    It contains the results of a child traversal, and provides lazy child instantiation
    in order to support the following API:

    >>> m = Message("OML_O33")
    >>> print(m.msh)
    [<Segment MSH>]
    >>> print(isinstance(m.msh, ElementProxy))
    True
    >>> print(isinstance(m.msh.msh_7, ElementProxy))
    True
    """
    cls_attrs = ('element_list', 'list', 'element_name')

    def __init__(self, element_list, element_name):
        self.element_name = element_name.upper()
        self.element_list = element_list

    @property
    def list(self):
        return self.element_list.indexes.get(self.element_name, [])

    @property
    def traversal_list(self):
        return self.element_list.traversal_indexes.get(self.element_name, [])

    def __len__(self):
        return len(self.list)

    def __iter__(self):
        if not self.list:
            return iter([])
        else:
            return super(ElementProxy, self).__iter__()

    def __getattr__(self, name):
        try:
            element = self.list[0]
        except IndexError:  # first child not found, create the element
            try:
                element = self.traversal_list[0]
            except IndexError:
                element = self.element_list.create_element(self.element_name, traversal_parent=True)
        return getattr(element, name)

    def __setattr__(self, name, value):
        if name in self.cls_attrs:
            super(ElementProxy, self).__setattr__(name, value)
        else:
            try:
                element = self.list[0]
            except IndexError:  # first child not found, create the element
                try:
                    element = self.traversal_list[0]
                except IndexError:
                    element = self.element_list.create_element(self.element_name, traversal_parent=True)
            if name == 'value':
                element.set_parent_to_traversal()
            setattr(element, name, value)

    def __setitem__(self, index, value):
        self.element_list.set(self.element_name, value, index)

    def __getitem__(self, index):
        return self.list[index]

    def __delitem__(self, index):
        self.element_list.remove(self.list[index])

    def __delattr__(self, name):
        delattr(self.list[0], name)

    def __repr__(self):
        return repr(self.list)


class ElementList(collections.MutableSequence):
    """
    Delegate for handling the children of a given Element.

    It stores the children inside a list and indexes them using a dictionary (e.g. self.indexes['SPM'] will
    return all child named 'SPM' found in the :class:` Message <hl7apy.core.Message>` instance)

    """
    def __init__(self, element):
        self.element = element
        self.list = []
        self.indexes = {}
        self.traversal_indexes = {}
        self.proxies = {}

    def get_ordered_children(self):
        """
        Return the list of children ordered according to the element structure

        :return: a list of :class:`Element <hl7apy.core.Element>`
        """
        ordered_keys = self.element.ordered_children if self.element.ordered_children is not None else []
        children = [self.indexes.get(k, None) for k in ordered_keys]
        return children

    def get_children(self):
        """
        Return the list of children according to their insertion order

        :return: a list of :class:`Element <hl7apy.core.Element>`
        """
        return [(v,) for v in self.list]

    def insert(self, index, child, by_name_index=-1):
        """
        Add the child at the given index

        :type index: ``int``
        :param index: child position

        :type child: :class:`Element <hl7apy.core.Element>`
        :param child: an instance of an :class:`Element <hl7apy.core.Element>` subclass
        """
        if self._can_add_child(child):
            try:
                if by_name_index == -1:
                    self.indexes[child.name].append(child)
                else:
                    self.indexes[child.name].insert(by_name_index, child)
            except KeyError:
                self.indexes[child.name] = [child]
            self.list.insert(index, child)

    def append(self, child):
        """
        Append the given child

        :class:`Element <hl7apy.core.Element>`
        :param child: an instance of an :class:`Element <hl7apy.core.Element>` subclass
        """
        if self._can_add_child(child):
            if self.element == child.parent:
                self._remove_from_traversal_index(child)
                self.list.append(child)
                try:
                    self.indexes[child.name].append(child)
                except KeyError:
                    self.indexes[child.name] = [child]
            elif self.element == child.traversal_parent:
                try:
                    self.traversal_indexes[child.name].append(child)
                except KeyError:
                    self.traversal_indexes[child.name] = [child]

    def pop(self, index=0):
        child = super(ElementList, self).pop(index)
        self._remove_from_index(child)
        return child

    def get(self, name):
        """
        Get the children having the given name

        :type name: ``str``
        :param name: the name of the children (e.g. PID)

        :return: an instance of :class:`ElementProxy <hl7apy.core.ElementProxy>` containing the results
        """
        return self._default_child_lookup(name)

    def set(self, name, value, index=-1):
        """
        Assign the ``value`` to the child having the given ``name`` at the ``index`` position

        :type name: ``str``
        :param name: the child name (e.g. PID)

        :type value: an instance of :class:`Element <hl7apy.core.Element>`, a `str` or an instance of
            :class:`ElementProxy <hl7apy.core.ElementProxy>`
        :param value: the child value

        :type index: ``int``
        :param index: the child position (e.g. 1)
        """

        # just copy the first element of the ElementProxy (e.g. message.pid = message2.pid)
        if isinstance(value, ElementProxy):
            value = value[0].to_er7()

        name = name.upper()
        reference = None if name is None else self.element.find_child_reference(name)
        child_ref, child_name = (None, None) if reference is None else (reference['ref'], reference['name'])

        if isinstance(value, basestring):  # if the value is a basestring, parse it
            child = self.element.parse_child(value, child_name=child_name, reference=child_ref)
        elif isinstance(value, Element):  # it is already an instance of Element
            child = value
        elif isinstance(value, BaseDataType):
            child = self.create_element(name, False, reference)
            child.value = value
        else:
            raise ChildNotValid(value, child_name)

        if child.name != child_name:  # e.g. message.pid = Segment('SPM') is forbidden
            raise ChildNotValid(value, child_name)

        child_to_remove = self.child_at_index(child_name, index)

        if child_to_remove is None:
            self.append(child)
        else:
            self.replace_child(child_to_remove, child)

        # a set has been called, change the temporary parent to be the actual one
        self.element.set_parent_to_traversal()

    def remove(self, child):
        """
        Remove the given child from both child list and child indexes

        :type child: :class:`Element <hl7apy.core.Element>`
        :param child: an instance of :class:`Element <hl7apy.core.Element>` subclass
        """
        if self.element == child.traversal_parent:
            self._remove_from_traversal_index(child)
        else:
            self._remove_from_index(child)
            self.list.remove(child)

    def remove_by_name(self, name, index=0):
        """
        Remove the child having the given name at the given position

        :type name: ``str``
        :param name: child name (e.g. PID)

        :type index: ``int``
        :param index: child index

        :return: an instance of :class:`Element <hl7apy.core.Element>` subclass
        """
        child = self.child_at_index(name, index)
        self.remove(child)
        return child

    def child_at_index(self, name, index):
        """
        Return the child named `name` at the given index

        :type name: ``str``
        :param name: child name (e.g. PID)

        :type index: ``int``
        :param index: child index

        :return: an instance of :class:`Element <hl7apy.core.Element>` subclass
        """
        child_name = None if name is None else self._find_name(name)
        try:
            child = self.indexes[child_name][index]
        except (KeyError, IndexError):
            try:
                child = self.traversal_indexes[child_name][index]
            except (KeyError, IndexError):
                child = None
        return child

    def replace_child(self, old_child, new_child):
        # in case it was a traversal child we just remove it from traversal children and append
        # the new child to children
        if old_child.traversal_parent == self.element:
            self.remove(old_child)
            self.append(new_child)
        else:
            list_index = self.list.index(old_child)
            by_name_index = self.indexes[old_child.name].index(old_child)
            self.remove(old_child)
            self.insert(list_index, new_child, by_name_index)

    def create_element(self, name, traversal_parent=False, reference=None):
        """
        Create an element having the given name

        :type name: ``str``
        :param name: the name of the element to be created (e.g. PID)

        :type traversal_parent: ``bool``
        :param traversal_parent: if ``True``, the parent will be set as temporary for traversal purposes

        :param reference: the new element structure (see :func:`load_reference <hl7apy.load_reference>`)

        :return: an instance of an :class:`hl7apy.core.Element` subclass

        :raises: :exc:`ChildNotFound <hl7apy.exceptions.ChildNotFound>` if the element does not exist
        """
        if reference is None:
            reference = self.element.find_child_reference(name)
        if reference is not None:
            cls = reference['cls']
            element_name = reference['name']
            kwargs = {'reference': reference['ref'],
                      'validation_level': self.element.validation_level,
                      'version': self.element.version}
            if not traversal_parent:
                kwargs['parent'] = self.element
            else:
                kwargs['traversal_parent'] = self.element
            return cls(element_name, **kwargs)
        else:
            raise ChildNotFound(name)

    def _find_name(self, name):
        """
        Find the reference of a child having the given name

        :type name: ``str``
        :param name: the child name (e.g. PID)

        :return: the element structure (see :func:`load_reference <hl7apy.load_reference>`) or ``None`` if the
            element has not been found
        """
        name = name.upper()
        element = self.element.find_child_reference(name)
        return element['name'] if element is not None else None

    def _default_child_lookup(self, name):
        """
        Return an instance of :class:`ElementProxy <hl7apy.core.ElementProxy>` containing the children found
        having the given name

        :type name: ``str``
        :param name: the name of the children (e.g. PID)

        :return: an instance of :class:`ElementProxy <hl7apy.core.ElementProxy>` containing the results
        """
        if name in self.indexes or name in self.traversal_indexes:
            try:
                return self.proxies[name]
            except KeyError:
                self.proxies[name] = ElementProxy(self, name)
                return self.proxies[name]
        else:  # child not found in the indexes dictionary (e.g. msh_9.message_code, msh_9.msh_9_1)
            child_name = self._find_name(name)
            if child_name is not None:
                try:
                    return self.proxies[child_name]
                except KeyError:
                    self.proxies[child_name] = ElementProxy(self, child_name)
                    return self.proxies[child_name]

    def _can_add_child(self, child):
        if self.element._is_valid_child(child):
            if child.parent != self.element and child.traversal_parent != self.element:  # avoid infinite recursion
                child.parent = self.element
            else:
                # if validation is strict, check the child cardinality
                if Validator.is_strict(self.element.validation_level):
                    min_rep, max_rep = self.element.repetitions.get(child.name, (0, -1))
                    if len(self.indexes.get(child.name, [])) + 1 > int(max_rep) and max_rep > -1:
                        raise MaxChildLimitReached(self.element, child, max_rep)
                if self.element.validation_level != child.validation_level:
                    raise OperationNotAllowed('Cannot add a child with a different validation_level')
                if self.element.version != child.version:
                    raise OperationNotAllowed('Cannot add a child with a different HL7 version')
                return True
        else:
            raise ChildNotValid(child, self.element)
        return False

    def _remove_from_index(self, child):
        try:
            self.indexes[child.name].remove(child)
        except (KeyError, ValueError):
            pass

    def _remove_from_traversal_index(self, child):
        try:
            self.traversal_indexes[child.name].remove(child)
            if len(self.traversal_indexes[child.name]) == 0:
                del self.traversal_indexes[child.name]
        except (KeyError, ValueError):
            pass

    def __len__(self):
        return len(self.list)

    def __getitem__(self, index):
        return self.list[index]

    def __delitem__(self, index):
        child = self.list[index]
        self._remove_from_index(child)
        del self.list[index]

    def __setitem__(self, index, value):
        child_name = self.list[index].name
        self.set(child_name, value, index)

    def __str__(self):
        return str(self.list)

    def __repr__(self):
        return repr(self.list)


class ElementFinder(object):

    @staticmethod
    def get_structure(element, reference=None):
        """
        Get the element structure

        :type element: :class:`Element <hl7apy.core.Element>`
        :param element: element having the given reference structure

        :param reference: the element structure from :func:`load_reference <hl7apy.load_reference>` or from a
            message profile

        :return: a dictionary containing the structure data
        """
        if reference is None:
            try:
                reference = load_reference(element.name, element.classname, element.version)
            except (ChildNotFound, KeyError):
                raise InvalidName(element.classname, element.name)
        if not isinstance(reference, collections.Sequence):
            raise Exception
        return ElementFinder._parse_structure(element, reference)

    @staticmethod
    def _parse_structure(element, reference):
        """
        Parse the given reference

        :type element: :class:`Element <hl7apy.core.Element>`
        :param element: element having the given reference structure

        :param reference: the element structure from :func:`load_reference <hl7apy.load_reference>` or from a
            message profile

        :return: a dictionary containing the structure data
        """
        data = {
            'reference': reference
        }
        if reference[0] == 'mp':
            reference = reference[1:]
            is_profile = True
        else:
            is_profile = False

        content_type = reference[0]  # content type can be sequence, choice or leaf
        if content_type in ('sequence', 'choice'):
            children = reference[1] if is_profile is False else reference[2]
            ordered_children = []
            structure = {}
            repetitions = {}
            counters = collections.defaultdict(int)
            for c in children:
                if is_profile is False:
                    child_name, cardinality = c
                    k = child_name if child_name not in structure \
                        else '{0}_{1}'.format(child_name, counters[child_name])
                    structure[k] = find_reference(child_name, element.child_classes, element.version)
                    counters[child_name] += 1
                else:
                    child_name, cardinality, cls = c[2], c[4], c[5]
                    if child_name in structure:
                        child_name = '{0}_{1}'.format(child_name, counters['child_name'])
                    structure[child_name] = {'name': child_name,
                                             'cls': eval(cls),  # TODO: is there another way?
                                             'ref': c}
                    counters[child_name] += 1
                repetitions[child_name] = cardinality
                ordered_children.append(child_name)
            data['repetitions'] = repetitions
            data['ordered_children'] = ordered_children
            data['structure_by_name'] = structure
            if is_profile is False:
                data['structure_by_longname'] = {e['ref'][2]: e for e in structure.values()
                                                 if e['ref'][0] == 'leaf'}
            else:
                # in this case the len is 6 and not 5 as above because here the first is 'mp'
                data['structure_by_longname'] = {e['ref'][7]: e for e in structure.values()
                                                 if e['ref'][1] == 'leaf' or len(e['ref']) > 6}

        if content_type == 'leaf' or (is_profile and len(reference) > 5):
            if is_profile is False:
                datatype, long_name, table = reference[1:]
            else:
                datatype, long_name, table, max_length = reference[5:]
            data['datatype'] = datatype
            data['table'] = table
            data['long_name'] = long_name
        return data


class Element(object):
    """
    Base class for all HL7 elements. It is not meant to be directly instantiated.
    """

    cls_attrs = ['name', 'validation_level', 'version', 'children', 'ordered_children',
                 'table', 'long_name', 'value', '_value', 'parent',  '_parent', '_traversal_parent',
                 'traversal_parent', 'child_classes', 'encoding_chars', 'structure_by_name',
                 'structure_by_longname', 'repetitions', 'reference']

    def __init__(self, name=None, parent=None, reference=None, version=None,
                 validation_level=None, traversal_parent=None):

        if self.__class__ == Element:
            raise OperationNotAllowed("Cannot instantiate an Element")

        if validation_level is None:
            validation_level = get_default_validation_level()

        if version is None:
            version = get_default_version()

        check_validation_level(validation_level)
        check_version(version)
        
        self.validation_level = validation_level
        self.name = name.upper() if name is not None else None
        self.version = version
        self.table = None
        self.long_name = None
        self.children = ElementList(self)
        self.structure_by_name = None
        self.structure_by_longname = None
        self.ordered_children = None
        self.repetitions = {}
        self._find_structure(reference)
        self.parent = parent
        if parent is None:
            self.traversal_parent = traversal_parent
        else:
            self.traversal_parent = None

    def find_child_reference(self, name):
        name = name.upper()
        if isinstance(self.structure_by_name, collections.MutableMapping):
            element = self.structure_by_name.get(name) or self.structure_by_longname.get(name)
        else:
            element = None
        if element is None:  # not found in self.structure
            element = find_reference(name, self.child_classes, self.version)
            if Validator.is_strict(self.validation_level):  # cannot be created if validation is strict
                raise ChildNotValid(name, self)
        return element

    def add(self, obj):
        """
        Add an instance of :class:`Element <hl7apy.core.Element>` subclass to the list of children

        :type obj: :class:`hl7apy.core.Element`
        :param obj: an instance of :class:`hl7apy.core.Element` subclass

        >>> s = Segment('PID')
        >>> f = Field('PID_5')
        >>> f.value = 'EVERYMAN^ADAM'
        >>> s.add(f)
        >>> print(s.to_er7())
        PID|||||EVERYMAN^ADAM
        """
        self.children.append(obj)

    def is_named(self, name):
        name = name.upper()
        return name in (self.name, self.long_name)

    def is_unknown(self):
        return self.name is None

    def set_parent_to_traversal(self):
        if self.traversal_parent and self.parent is None:
            self.parent = self.traversal_parent
            self.parent.set_parent_to_traversal()
        else:
            self.traversal_parent = None

    def parse_child(self, text, **kwargs):
        if self.child_parser:
            kwargs['version'] = self.version
            kwargs['validation_level'] = self.validation_level
            module = importlib.import_module("hl7apy.parser")
            parser = getattr(module, self.child_parser[0])
            return parser(text, **kwargs)
        return None

    def parse_children(self, text, **kwargs):
        if self.child_parser:
            kwargs['version'] = self.version
            kwargs['validation_level'] = self.validation_level
            kwargs['encoding_chars'] = self.encoding_chars

            module = importlib.import_module("hl7apy.parser")
            parser = getattr(module, self.child_parser[1])
            return parser(text, **kwargs)

    def to_er7(self, encoding_chars=None, trailing_children=False):
        """
        Returns the HL7 representation of the :class:`Element <hl7apy.core.Element>`. It adds the appropriate
        separator at the end if needed

        :type encoding_chars: ``dict``
        :param encoding_chars: The encoding chars to use.
            If it is ``None`` it uses :attr:`self.encoding_chars`,
            which by default is the ones return by
            :func:`get_default_encoding_chars <hl7apy.get_default_encoding_chars>`

        :rtype: ``str``
        :return: the HL7 representation of the :class:`Element <hl7apy.core.Element>`
        """
        if encoding_chars is None:
            encoding_chars = self.encoding_chars

        child_class = self.child_classes[0]
        separator = encoding_chars.get(child_class.__name__.upper(), '')

        s = []
        for child in self._get_children(trailing_children):
            if child:
                s.extend(repetition.to_er7(encoding_chars, trailing_children) for repetition in child)
            else:
                try:
                    s.append(self._handle_empty_children(encoding_chars))
                except NotImplementedError:
                    pass

        return separator.join(s)

    def validate(self, report_file=None):
        """
        Validate the HL7 element using the :attr:`STRICT <hl7apy.consts.VALIDATION_LEVEL.STRICT>` validation
        level. It calls the :func:`Validator.validate <hl7apy.validation.Validator.validate>` method passing
        the reference used in the instantiation of the element.

        :param: report_file: the report file to pass to the validator
        """
        return Validator.validate(self, reference=self.reference, report_file=report_file)

    def is_z_element(self):
        return False

    def _get_parent(self):
        return self._parent

    def _set_parent(self, parent):
        self._parent = parent
        if parent is not None:
            self.traversal_parent = None
            self.parent.add(self)

    parent = property(_get_parent, _set_parent,
                      doc="The parent :class:`Element <hl7apy.core.Element>` of this one")

    def _get_traversal_parent(self):
        return self._traversal_parent

    def _set_traversal_parent(self, parent):
        self._traversal_parent = parent
        if parent is not None:
            parent.add(self)

    traversal_parent = property(_get_traversal_parent, _set_traversal_parent)

    def _set_value(self, value):
        self.children = self.parse_children(value)

    def _get_value(self):
        return self.to_er7()

    value = property(_get_value, _set_value)

    @property
    def classname(self):
        """
        The name of the class
        """
        return self.__class__.__name__

    @property
    def encoding_chars(self):
        """
        A ``dict`` with the encoding chars of the :class:`Element <hl7apy.core.Element>`.
        If the :class:`Element <hl7apy.core.Element>` has a parent it is the parent's
        ``encoding_chars`` otherwise the ones returned by
        :func:`get_default_encoding_chars <hl7apy.get_default_encoding_chars>`
        The structure of the ``dict`` is:

        .. code-block:: python

            {'SEGMENT' : '\\r',
            'GROUP': '\\r',
            'FIELD' : '|',
            'COMPONENT' : '^',
            'SUBCOMPONENT' : '&',
            'REPETITION' : '~',
            'ESCAPE' : '\\'}

        """
        if self.parent is not None:
            return self.parent.encoding_chars
        return get_default_encoding_chars()

    def _find_structure(self, reference=None):
        if self.name is not None:
            structure = ElementFinder.get_structure(self, reference)
            for k, v in iteritems(structure):
                setattr(self, k, v)

    def _is_valid_child(self, child):
        valid = child.classname in (c.__name__ for c in self.child_classes)
        if valid:
            if child.name is not None:
                self.find_child_reference(child.name)
        return valid

    def _get_children(self, trailing=False):
        children = self.children.get_ordered_children()
        children.extend([c for c in self.children.get_children() if c[0].name in (None, 'ST')])
        if not trailing:
            children = _remove_trailing(children)
        return children

    def _handle_empty_children(self, encoding_chars=None):
        """
        Subclasses should implement this method, which must returns the string
        that should be used when a child of the structure is empty
        """
        raise NotImplementedError

    def __getattr__(self, name):
        if hasattr(self, 'children') and name not in self.cls_attrs:
            return self.children.get(name)
        else:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        if name in self.cls_attrs:
            children = []
            if name == 'children':
                if not isinstance(value, ElementList):
                    children = value
                    value = ElementList(self)
            super(Element, self).__setattr__(name, value)
            for c in children:
                self.add(c)
        elif hasattr(self, 'children'):
            self.children.set(name, value, 0)

    def __delattr__(self, name):
        if name in self.cls_attrs:
            super(Element, self).__delattr__(name)
        else:
            self.children.remove_by_name(name)

    def __repr__(self):
        return "<{0} {1}>".format(self.classname, self.name or '')


class SupportComplexDataType(Element):
    """
    Mixin for classes that support complex datatypes
    """
    cls_attrs = Element.cls_attrs + ['_datatype', 'datatype', 'table', 'long_name', 'max_length']

    def __init__(self):

        if self.__class__ == SupportComplexDataType:
            raise OperationNotAllowed("Cannot instantiate a SupportComplexDataType")

        self._datatype = None

    def find_child_reference(self, name):
        name = name.upper()
        if isinstance(self.structure_by_name, collections.MutableMapping):
            element = self.structure_by_name.get(name) or self.structure_by_longname.get(name)
        else:
            element = None

        if element is None:  # not found in self.structure
            element = find_reference(name, self.child_classes, self.version)
            if element is None:
                raise ChildNotFound(name)
            # it means that the child exists but it's not valid for the Element (e.g. Field('pid_3').ce_1)
            if self.structure_by_name is not None:
                raise ChildNotValid(name, self)
        return element

    def is_unknown(self):
        return self.name == self.datatype

    def _get_datatype(self):
        return self._datatype

    def _set_datatype(self, datatype):
        if Validator.is_strict(self.validation_level) and self.datatype and \
                datatype != self.datatype:
            raise OperationNotAllowed("Cannot change datatype using STRICT validation")

        if not is_base_datatype(datatype, self.version) and \
                datatype not in ('varies', None, self.datatype):
            reference = load_reference(datatype, 'Component', self.version)
            structure = ElementFinder.get_structure(self, reference)
            for k, v in iteritems(structure):
                setattr(self, k, v)

        if hasattr(self, 'children') and len(self.children) >= 1:
            if is_base_datatype(self.datatype, self.version):
                self._datatype = datatype
                if is_base_datatype(datatype, self.version):
                    self.children[0].datatype = datatype
            else:
                raise OperationNotAllowed("Cannot change datatype: the Element already contains children")
        else:
            self._datatype = datatype

    datatype = property(_get_datatype, _set_datatype)

    def _set_value(self, value):
        if isinstance(value, BaseDataType):
            if not is_base_datatype(self.datatype, self.version):
                raise ChildNotValid(value, self)
            cls = self.child_classes[0]
            child = cls(datatype=value.classname, version=self.version,
                        validation_level=self.validation_level)
            child.value = value
            try:
                old_child = self.children[0]
            except IndexError:
                self.add(child)
            else:
                self.children.replace_child(old_child, child)
        else:
            children = self.parse_children(value)
            if Validator.is_tolerant(self.validation_level) and \
                    is_base_datatype(self.datatype, self.version) and len(children) > 1:
                self.datatype = None
            self.children = children

    def _get_value(self):
        return super(SupportComplexDataType, self)._get_value()

    value = property(_get_value, _set_value)

    def _get_children(self, trailing=False):
        if is_base_datatype(self.datatype, self.version) or self.datatype is None:
            return [[c for c in self.children]]
        else:
            return Element._get_children(self, trailing=False)

    def _is_valid_child(self, child):
        if not is_base_datatype(self.datatype, self.version):
            if self.datatype == 'varies' and _valid_child_name(child.name, self.datatype):
                return True
            if self.datatype is None and _valid_child_name(self.name, 'varies') and child.is_unknown():
                return True
            if child.is_unknown() and Validator.is_strict(self.validation_level):
                return False
            if not child.is_unknown() and self.datatype and not _valid_child_name(child.name, self.datatype):
                return False
        try:
            valid = Element._is_valid_child(self, child)
            if valid and is_base_datatype(self.datatype, self.version):
                if child.datatype and child.datatype != self.datatype:
                    valid = False
            return valid
        except ChildNotFound:
            if is_base_datatype(self.datatype, self.version):
                if child.datatype and child.datatype != self.datatype:
                    return False
            return True

    def _handle_empty_children(self, encoding_chars=None):
        return ''

    def __repr__(self):
        if self.name:
            return '<{0} {1} ({2}) of type {3}>'.format(self.classname, self.name, self.long_name,
                                                        self.datatype)
        else:
            return '<{0} of type {1}>'.format(self.classname, self.datatype)


class CanBeVaries(Element):
    """
    Mixin for Elements that can be of VARIES datatype
    """
    def __init__(self, name=None, datatype=None, parent=None, reference=None,
                 version=None, validation_level=None, traversal_parent=None):

        if self.__class__ == CanBeVaries:
            raise OperationNotAllowed("Cannot instantiate a CanBeVaries")

        if datatype == 'varies' and reference is None:
            reference = ('leaf', 'varies', None, None)

        if name is not None and _valid_child_name(name, 'VARIES'):
            Element.__init__(self, None, parent, reference, version,
                             validation_level, traversal_parent)
            self.name = name.upper()
        else:
            try:
                Element.__init__(self, name, parent, reference, version,
                                 validation_level, traversal_parent)
            except ChildNotFound:
                raise InvalidName(self.classname, self.name)

        # the name was found in the references but it's not a valid reference (e.g. Component('CX'))
        if self.name and not self.name.startswith('VARIES') and self.datatype is None:
            raise InvalidName(self.classname, self.name)

        if self.name:  # the datatype has been valued by the finder
            # if it is STRICT we don't allow to change the official datatype
            # TODO: should check if it is VARIES
            if Validator.is_strict(self.validation_level) and None not in (datatype, self.datatype) and \
                    datatype != self.datatype:
                raise OperationNotAllowed("Cannot override datatype in strict mode")
            # in TOLERANT we overwrite it only if the given one is not None
            elif datatype is not None:
                self.datatype = datatype
        else:
            self.datatype = datatype
            self.name = self.datatype

    def is_unknown(self):
        return self.name == self.datatype


class SubComponent(CanBeVaries):
    """
    Class representing an HL7 subcomponent.

    :type name: ``str``
    :param name: the HL7 name of the subcomponent (e.g. CWE_1)

    :type datatype: ``str``
    :param datatype: the datatype of the component (e.g. ST)

    :type value: ``str`` or instance of :class:`BaseDataType <hl7apy.base_datatypes.BaseDataType>`
    :param value: the value of the subcomponent (e.g. ADT_A01)

    :type parent: an instance of :class:`Component <hl7apy.core.Component>` or None
    :param parent: the parent

    :param reference: the reference structure (see :func:`load_refernce <hl7apy.load_reference>`)

    :type version: ``str``
    :param version: the HL7 version (e.g. "2.5"), or ``None`` to use the default
        (see :func:`get_default_version <hl7apy.get_default_version>`)

    :type validation_level: ``int``
    :param validation_level: the validation level. Possible values are defined in
        :class:`VALIDATION_LEVEL <hl7apy.consts.VALIDATION_LEVEL>` class or ``None`` to use the default
        validation level (see :func:`get_default_validation_level <hl7apy.get_default_validation_level>`)

    :type traversal_parent: an instance of :class:`Component <hl7apy.core.Component>` or None
    :param traversal_parent: the temporary parent used during traversal
    """
    child_classes = ()
    cls_attrs = Element.cls_attrs + ['datatype', '_datatype', 'table', 'long_name', 'max_length']

    def __init__(self, name=None, datatype=None, value=None, parent=None,
                 reference=None, version=None, validation_level=None,
                 traversal_parent=None):

        self._parent = None  # we need to initialize it
        self._datatype = None  # we need to initialize it
        if not name and datatype is None:
            raise OperationNotAllowed("Cannot instantiate a SubComponent with name and datatype both empty")

        CanBeVaries.__init__(self, name, datatype, parent, reference,
                             version, validation_level, traversal_parent)

        if _valid_child_name(name, 'VARIES') and self.datatype is None:
            self.datatype = 'ST'

        self.value = value

    def add(self, obj):
        raise OperationNotAllowed("Cannot add children to a SubComponent")

    def to_er7(self, encoding_chars=None, trailing_children=False):
        """
        Return the ER7-encoded string

        :type encoding_chars: ``dict``
        :param encoding_chars: a dictionary containing the encoding chars or None to use the default
            (see :func:`get_default_encoding_chars <hl7apy.get_default_encoding_chars>`)

        :type trailing_children: ``bool``
        :param trailing_children: if ``True``, trailing children will be added even if their value is None

        :return: the ER7-encoded string

        >>> s = SubComponent("CE_1")
        >>> s.value = "IDENTIFIER"
        >>> print(s.to_er7())
        IDENTIFIER
        """

        if encoding_chars is None:
            encoding_chars = self.encoding_chars
        try:
            return self.value.to_er7(encoding_chars)
        except AttributeError:
            return self.value

    def _set_value(self, value):
        if value is None:
            self._value = None
        else:
            if value and isinstance(value, basestring):
                self._value = datatype_factory(self.datatype, value, self.version,
                                               self.validation_level)
            elif not value or isinstance(value, BaseDataType):
                self._value = value
            else:
                raise ValueError('Cannot assign {0}'.format(value.classname))
            self.set_parent_to_traversal()

    def _get_value(self):
        return self._value

    value = property(_get_value, _set_value)

    def _get_datatype(self):
        return self._datatype

    def _set_datatype(self, datatype):

        if datatype and not is_base_datatype(datatype, self.version):  # only base datatypes allowed
            raise OperationNotAllowed("Cannot set a complex datatype to a SubComponent")

        if Validator.is_strict(self.validation_level) and \
                self.datatype is not None and datatype != self.datatype:
            raise OperationNotAllowed("Cannot change datatype using STRICT validation")
        # if the SC is already valued it is impossible to change the datatype
        if hasattr(self, 'value') and self.value:
            raise OperationNotAllowed("Cannot change datatype: the Subcomponent is valued")
        else:
            # change also the parent datatype if it is a base datatype
            if self.parent is not None and is_base_datatype(self.parent.datatype, self.parent.version) and \
                    self.parent.datatype != datatype:  # avoid infinite recursion
                self.parent.datatype = datatype
            self._datatype = datatype

    datatype = property(_get_datatype, _set_datatype)

    def __repr__(self):
        return '<SubComponent {0}>'.format(self.name or self.datatype)


class Component(SupportComplexDataType, CanBeVaries):
    """
    Class representing an HL7 component.

    :type name: ``str``
    :param name: the HL7 name of the component (e.g. XPN_2)

    :type datatype: ``str``
    :param datatype: the datatype of the component (e.g. CE)

    :type parent: an instance of :class:`hl7apy.core.Field` or None
    :param parent: the parent

    :param reference: the reference structure (see :func:`load_reference <hl7apy.load_reference>`)

    :type version: ``str``
    :param version: the HL7 version (e.g. "2.5"), or ``None`` to use the default
        (see :func:`get_default_version <hl7apy.get_default_version>`)

    :type validation_level: ``int``
    :param validation_level: the validation level. Possible values are those defined in
        :class:`VALIDATION_LEVEL <hl7apy.consts.VALIDATION_LEVEL>` or ``None`` to use the default validation
        level (see :func:`get_default_validation_level <hl7apy.get_default_validation_level>`)

    :type traversal_parent: an instance of :class:`Field hl7apy.core.Field` or None
    :param traversal_parent: the temporary parent used during traversal
    """
    child_classes = (SubComponent,)
    child_parser = ('parse_subcomponent', 'parse_subcomponents')

    def __init__(self, name=None, datatype=None, parent=None, reference=None,
                 version=None, validation_level=None, traversal_parent=None):

        SupportComplexDataType.__init__(self)

        if datatype == 'varies' and reference is None:
            reference = ('leaf', 'varies', None, None)

        CanBeVaries.__init__(self, name, datatype, parent, reference,
                             version, validation_level, traversal_parent)

        if self.is_unknown() and Validator.is_strict(validation_level) and \
                not is_base_datatype(self.datatype, self.version) and self.datatype != 'varies':
            raise OperationNotAllowed("Cannot instantiate an unknown Element with strict validation")

        # TODO: This control should be deleted (see CanBeVaries)
        if datatype is not None and Validator.is_strict(validation_level) and \
                self.datatype != 'varies' and self.datatype != datatype:
            raise OperationNotAllowed("Cannot assign a different datatype with strict validation")

    def add_subcomponent(self, name):
        """
        Create an instance of :class:`SubComponent <hl7apy.core.SubComponent>` having the given name

        :param name: the name of the subcomponent to be created (e.g. CE_1)
        :return: an instance of :class:`SubComponent <hl7apy.core.SubComponent>`

        >>> c = Component(datatype='CE')
        >>> ce_1 = c.add_subcomponent('CE_1')
        >>> print(ce_1)
        <SubComponent CE_1>
        >>> print(ce_1 in c.children)
        True
        """
        if self.is_unknown() and is_base_datatype(self.datatype):
            # An unknown component can't have a child
            raise ChildNotValid(name, self)
        return self.children.create_element(name)

    def add(self, obj):
        """
        Add an instance of :class:`SubComponent <hl7apy.core.SubComponent>` to the list of children

        :param obj: an instance of :class:`SubComponent <hl7apy.core.SubComponent>`

        >>> c = Component('CX_10')
        >>> s = SubComponent(name='CWE_1', value='EXAMPLE_ID')
        >>> s2 = SubComponent(name='CWE_4', value='ALT_ID')
        >>> c.add(s)
        >>> c.add(s2)
        >>> print(c.to_er7())
        EXAMPLE_ID&&&ALT_ID
        """
        # base datatype components can't have more than one child
        if self.name and is_base_datatype(self.datatype, self.version) and \
                len(self.children) >= 1:
            raise MaxChildLimitReached(self, obj, 1)

        # the name is different from the datatype (i.e. the name has been forced to be equal to the datatype)
        try:
            if obj.name and obj.name != obj.datatype:
                try:
                    if not _valid_child_name(obj.name, self.datatype):
                        raise ChildNotValid(obj.name, self)
                except AttributeError:
                    pass
        except ChildNotFound:  # obj.datatype causes ChildNotFound for some Elements (Message, Groups etc)
            raise ChildNotValid(obj, self)

        return super(Component, self).add(obj)

    def parse_child(self, text, child_name=None, reference=None):
        kwargs = {'name': child_name}
        if reference is not None:
            kwargs['datatype'] = reference[6] if reference[0] == 'mp' else reference[1]
        return super(Component, self).parse_child(text, **kwargs)

    def parse_children(self, text, **kwargs):
        kwargs = {'component_datatype': self.datatype, 'encoding_chars': self.encoding_chars}
        return super(Component, self).parse_children(text, **kwargs)


class Field(SupportComplexDataType):
    """
    Class representing an HL7 field.

    :type name: ``str``
    :param name: the HL7 name of the field (e.g. PID_5)

    :type datatype: ``str``
    :param datatype: the datatype of the field (e.g. CE)

    :type parent: an instance of :class:`hl7apy.core.Segment` or None
    :param parent: the parent

    :param reference: the reference structure (see :func:`load_reference <hl7apy.load_reference>`)

    :type version: ``str``
    :param version: the HL7 version (e.g. "2.5"), or ``None`` to use the default
        (see :func:`get_default_version <hl7apy.get_default_version>`)

    :param validation_level: the validation level. Possible values are those defined in
        :class:`VALIDATION_LEVEL <hl7apy.consts.VALIDATION_LEVEL>` or ``None`` to use the default validation
        level (see :func:`get_default_validation_level <hl7apy.get_default_validation_level>`)

    :type traversal_parent: an instance of :class:`Segment <hl7apy.core.Segment>` or None
    :param traversal_parent: the temporary parent used during traversal
    """
    child_classes = (Component,)
    child_parser = ('parse_component', 'parse_components')

    def __init__(self, name=None, datatype=None, parent=None, reference=None,
                 version=None, validation_level=None, traversal_parent=None):

        SupportComplexDataType.__init__(self)

        if name is None and Validator.is_strict(validation_level) and datatype != 'varies':
            raise OperationNotAllowed("Cannot instantiate an unknown Element with strict validation")

        if datatype == 'varies' and reference is None:
            reference = ('leaf', 'varies', None, None)

        try:
            Element.__init__(self, name, parent, reference, version,
                             validation_level, traversal_parent)
        except InvalidName:
            if _valid_z_field_name(name):
                datatype = datatype or 'ST'
                reference = ('leaf', datatype, None, None)
                Element.__init__(self, name, parent, reference, version,
                                 validation_level, traversal_parent)
            else:
                raise

        if datatype is not None and Validator.is_strict(validation_level) and \
                datatype != 'varies' and datatype != self.datatype:
            raise OperationNotAllowed("Cannot assign a different datatype with strict validation")

        if datatype is not None:  # force the datatype to be the one chosen by the user
            self.datatype = datatype
        elif self.name is None:  # if it is unknown and no datatype has been given
            self.datatype = None

    def add_component(self, name):
        """
        Create an instance of :class:`Component <hl7apy.core.Component>` having the given name

        :param name: the name of the component to be created (e.g. XPN_2)
        :return: an instance of :class:`Component <hl7apy.core.Component>`

        >>> s = Field('PID_5')
        >>> print(s.add_component('XPN_2'))
        <Component XPN_2 (GIVEN_NAME) of type ST>
        """
        return self.children.create_element(name)

    def find_child_reference(self, name):
        if is_base_datatype(self.datatype, self.version):
            # create reference in case of base datatypes
            if name == self.datatype:
                element = {'cls': Component,
                           'name': self.datatype,
                           'ref': ('leaf', self.datatype, None, None)}
                return element
            raise ChildNotFound(name)
        elif self.datatype == 'varies' and _valid_child_name(name, self.datatype):
            # create reference for children in case of datatype VARIES
            element = {'cls': Component,
                       'name': name,
                       'ref': ('leaf', None, None, None)}
            return element

        return super(Field, self).find_child_reference(name)

    def add(self, obj):
        """
        Add an instance of :class:`Component <hl7apy.core.Component>` to the list of children

        :param obj: an instance of :class:`Component <hl7apy.core.Component>`

        >>> f = Field('PID_5')
        >>> f.xpn_1 = 'EVERYMAN'
        >>> c = Component('XPN_2')
        >>> c.value = 'ADAM'
        >>> f.add(c)
        >>> print(f.to_er7())
        EVERYMAN^ADAM
        """
        # base datatype components can't have more than one child
        if self.name and is_base_datatype(self.datatype, self.version) and \
                len(self.children) >= 1:
            raise MaxChildLimitReached(self, obj, 1)

        return super(Field, self).add(obj)

    def parse_child(self, text, child_name=None, reference=None):
        kwargs = {'encoding_chars': self.encoding_chars, 'reference': reference, 'name': child_name}
        if reference is not None:
            kwargs['datatype'] = reference[6] if reference[0] == 'mp' else reference[1]
        return super(Field, self).parse_child(text, **kwargs)

    def parse_children(self, text, **kwargs):
        kwargs = {'field_datatype': self.datatype, 'references': self.structure_by_name}
        return super(Field, self).parse_children(text, **kwargs)

    def to_er7(self, encoding_chars=None, trailing_children=False):
        """
        Return the ER7-encoded string

        :type encoding_chars: ``dict``
        :param encoding_chars: a dictionary containing the encoding chars or None to use the default
            (see :func:`get_default_encoding <hl7apy.get_default_encoding_chars>`)

        :type trailing_children: ``bool``
        :param trailing_children: if ``True``, trailing children will be added even if their value is None

        :return: the ER7-encoded string

        >>> msh_9 = Field("MSH_9")
        >>> msh_9.value = "ADT^A01^ADT_A01"
        >>> print(msh_9.to_er7())
        ADT^A01^ADT_A01
        """
        if encoding_chars is None:
            encoding_chars = self.encoding_chars
        if self.is_named('MSH_1'):
            try:
                return self.msh_1_1.children[0].value.value
            except IndexError:
                return self.msh_1_1.children[0].value
        elif self.is_named('MSH_2'):
            try:
                return self.msh_2_1.children[0].value.value
            except IndexError:
                return self.msh_2_1.children[0].value
        return super(Field, self).to_er7(encoding_chars, trailing_children)

    def is_z_element(self):
        return self.name is not None and _valid_z_field_name(self.name)

    def _set_value(self, value):
        if self.name in ('MSH_1', 'MSH_2'):
            c = Component(datatype='ST', version=self.version,
                          validation_level=self.validation_level)
            c.value = value
            self.add(c)
        else:
            super(Field, self)._set_value(value)

    def _get_value(self):
        return super(Field, self)._get_value()

    value = property(_get_value, _set_value)

    def _get_children(self, trailing=False):
        if self.datatype == 'varies':
            children = [self.children.indexes['VARIES_{0}'.format(i+1)] for i in xrange(len(self.children))]
            children = _remove_trailing(children)
            children.extend([[c] for c in self.children if c.is_unknown()])
            return children
        else:
            return SupportComplexDataType._get_children(self)

    def _get_traversal_children(self, name):
        """
        Retrieve component and subcomponent indexes from the given traversal path
        (e.g. PID_1_2 -> component=2, subcomponent=None)
        """
        name = name.upper()
        parts = name.split('_')
        try:
            assert 3 <= len(parts) <= 4
            prefix = "{0}_{1}".format(parts[0], parts[1])
            component = int(parts[2])
            subcomponent = int(parts[3]) if len(parts) == 4 else None
        except (AssertionError, ValueError):
            return None, None
        else:
            if prefix != self.name:
                return None, None
        return component, subcomponent

    def _do_traversal(self, mode, name, value=None):
        try:
            if mode == 'get':
                return super(Field, self).__getattr__(name)
            elif mode == 'set':
                super(Field, self).__setattr__(name, value)
            else:
                super(Field, self).__delattr__(name)
        except ChildNotFound:
            component, subcomponent = self._get_traversal_children(name)
            if component is None:
                raise ChildNotFound(name)

            if is_base_datatype(self.datatype, self.version):
                if subcomponent is not None or component != 1:
                    raise ChildNotFound(name)
                component_name = self.datatype
            else:
                component_name = '{0}_{1}'.format(self.datatype, component)
            if subcomponent is None:
                if mode == 'get':
                    return getattr(self, component_name)
                elif mode == 'set':
                    setattr(self, component_name, value)
                else:
                    delattr(self, component_name)
            else:
                component = getattr(self, component_name)
                component_ref = self.structure_by_name[component_name]['ref']
                component_datatype = component_ref[6] if component_ref[0] == 'mp' else component_ref[1]
                subcomponent_name = '{0}_{1}'.format(component_datatype, subcomponent)
                try:
                    if mode == 'get':
                        return getattr(component, subcomponent_name)
                    elif mode == 'set':
                        setattr(component, subcomponent_name, value)
                    else:
                        delattr(component, subcomponent_name)
                except ChildNotFound:
                    raise ChildNotFound(name)

    def __getattr__(self, name):
        return self._do_traversal('get', name)

    def __setattr__(self, name, value):
        self._do_traversal('set', name, value)

    def __delattr__(self, name):
        self._do_traversal('del', name)


class Segment(Element):
    """
    Class representing an HL7 segment.

    :type name: ``str``
    :param name: the HL7 name of the segment (e.g. PID)

    :type parent: an instance of :class:`Message <hl7apy.core.Message>`, :class:`Group <hl7apy.core.Group>`
        or None
    :param parent: the parent

    :param reference: the reference structure (see :func:`load_reference <hl7apy.load_reference>`)

    :type version: ``str``
    :param version: the HL7 version (e.g. "2.5"), or ``None`` to use the default
        (see :func:`get_default_version <hl7apy.get_default_version>`)

    :param validation_level: the validation level. Possible values are those defined in
        :class:`VALIDATION_LEVEL <hl7apy.consts.VALIDATION_LEVEL>` or ``None`` to use the default validation
        level (see :func:`get_default_validation_level <hl7apy.get_default_validation_level>`)

    :type traversal_parent: an instance of :class:`hl7apy.core.Message`, :class:`hl7apy.core.Group` or None
    :param traversal_parent: the temporary parent used during traversal
    """
    child_classes = (Field,)
    child_parser = ('parse_field', 'parse_fields')
    cls_attrs = Element.cls_attrs + ['allow_infinite_children', '_last_allowed_child_index',
                                     '_last_child_index']

    def __init__(self, name=None, parent=None, reference=None, version=None,
                 validation_level=None, traversal_parent=None):

        if name is None:
            raise OperationNotAllowed("Cannot instantiate an unknown Segment")

        if _valid_z_segment_name(name):
            if reference is None:
                reference = ('sequence', ())

            super(Segment, self).__init__(name, parent, reference, version,
                                          validation_level, traversal_parent)
            self.allow_infinite_children = True
            self._last_allowed_child_index = 0
            self._last_child_index = 0
        else:
            super(Segment, self).__init__(name, parent, reference, version,
                                          validation_level, traversal_parent)

            last_field = self.ordered_children[-1]
            last_field_structure = self.structure_by_name[last_field]
            self.allow_infinite_children = last_field_structure['ref'][1] == 'varies'
            self._last_allowed_child_index = int(last_field_structure['name'][4:])
            self._last_child_index = self._last_allowed_child_index

    def add(self, obj):
        super(Segment, self).add(obj)
        # updates the index of the last children not allowed
        if obj.name and self.allow_infinite_children:
            field_index = int(obj.name[4:])
            if field_index > self._last_child_index:
                self._last_child_index = field_index

    def add_field(self, name):
        """
        Create an instance of :class:`Field <hl7apy.core.Field>` having the given name

        :param name: the name of the field to be created (e.g. PID_1)
        :return: an instance of :class:`Field <hl7apy.core.Field>`

        >>> s = Segment('PID')
        >>> print(s.add_field('PID_1'))
        <Field PID_1 (SET_ID_PID) of type SI>
        """
        return self.children.create_element(name)

    def find_child_reference(self, name):
        """
        Override the corresponding :class`Element <hl7apy.core.Element>`'s method. This is done for segments
        that allow children other than the ones expected in the HL7 structure: the ones with the last known
        field of type `varies` and the Z-Segments.
        The :class:`Field <hl7apy.core.Field>` will be created although it is not found in the HL7 structures,
        but only if its match the pattern `<SegmentName>_<index>`.
        In this case the method returns a reference for a :class:`Field <hl7apy.core.Field>` of type `None`
        in case of Z-Segment and `varies` otherwise.

        An example of a segment with the last field of type ``varies`` is the `QPD` in the version 2.5,
        whose last field is QPD_3.
        That means that it allows fields with name QPD_4, QPD_5,...QPD_n.
        """
        name = name.upper()
        element = self.structure_by_name.get(name, None) or self.structure_by_longname.get(name, None)

        if element is None:  # not found in self.structure
            if self.allow_infinite_children and _valid_child_name(name, self.name):
                if _valid_z_field_name(name):
                    datatype = 'ST'
                else:
                    datatype = 'varies'

                element = {'cls': Field, 'name': name, 'ref': ('leaf', datatype, None, None)}
            else:
                element = find_reference(name, self.child_classes, self.version)
                if element:
                    raise ChildNotValid(name, self)
                else:
                    raise ChildNotFound(name)
        return element

    def parse_child(self, text, child_name=None, reference=None):
        kwargs = {'encoding_chars': self.encoding_chars,
                  'reference': reference, 'name': child_name,
                  'force_varies': self.allow_infinite_children}
        return super(Segment, self).parse_child(text, **kwargs)

    def parse_children(self, text, **kwargs):
        segment_name = text[:3].upper()
        if segment_name != self.name:
            raise OperationNotAllowed('Cannot assign a segment with a different name')
        text = text[4:] if segment_name != 'MSH' else text[3:]
        kwargs = {'name_prefix': self.name,
                  'references': self.structure_by_name,
                  'force_varies': self.allow_infinite_children}
        return super(Segment, self).parse_children(text, **kwargs)

    def to_er7(self, encoding_chars=None, trailing_children=False):
        """
        Return the ER7-encoded string

        :type encoding_chars: ``dict``
        :param encoding_chars: a dictionary containing the encoding chars or None to use the default
            (see :func:`get_default_encoding_chars <hl7apy.get_default_encoding_chars>`)

        :type trailing_children: ``bool``
        :param trailing_children: if ``True``, trailing children will be added even if their value is None

        :return: the ER7-encoded string

        >>> pid = Segment("PID")
        >>> pid.pid_1 = '1'
        >>> pid.pid_5 = "EVERYMAN^ADAM"
        >>> print(pid.to_er7())
        PID|1||||EVERYMAN^ADAM
        """
        if encoding_chars is None:
            encoding_chars = self.encoding_chars

        separator = encoding_chars.get('FIELD')
        repetition = encoding_chars.get('REPETITION')
        s = [self.name]
        for child in self._get_children(trailing_children):
            if child is not None:
                s.append(repetition.join(item.to_er7(encoding_chars, trailing_children) for item in child))
            else:
                try:
                    s.append(self._handle_empty_children(encoding_chars))
                except NotImplementedError:
                    pass

        if self.name == 'MSH' and len(s) > 1:
            s.pop(1)

        return separator.join(s)

    def is_z_element(self):
        return _valid_z_segment_name(self.name)

    def _is_valid_child(self, child):
        # cannot add an unknown child with strict validation
        if child.name is None and Validator.is_strict(self.validation_level):
            return False
        valid = super(Segment, self)._is_valid_child(child)
        if valid:
            if child.name is not None:
                # cannot add a child with a name that differs from the segment name
                # (e.g. cannot add a PID_1 field to an SPM segment)
                if not child.name.upper().startswith(self.name.upper()):
                    return False
                if self.allow_infinite_children and _valid_child_name(child.name, self.name):
                    return True
        return valid

    def _get_children(self, trailing=False):
        children = self.children.get_ordered_children()
        if self.allow_infinite_children:
            for i in xrange(self._last_allowed_child_index + 1, self._last_child_index + 1):
                children.append(self.children.indexes.get('{}_{}'.format(self.name, i), None))
        children.extend([c for c in self.children.get_children() if c[0].name in (None, 'ST')])
        if not trailing:
            children = _remove_trailing(children)
        return children

    def _handle_empty_children(self, encoding_chars=None):
        return ''


class Group(Element):
    """
    Class representing an HL7 segment group

    :type name: ``str``
    :param name: the HL7 name of the message (e.g. RSP_K21_QUERY_RESPONSE)

    :type parent: an instance of :class:`Message <hl7apy.core.Message>`, :class:`Group <hl7apy.core.Group>`
        or None
    :param parent: the parent

    :param reference: the reference structure (see :func:`load_reference <hl7apy.load_reference>`)

    :type version: ``str``
    :param version: the HL7 version (e.g. "2.5"), or ``None`` to use the default
        (see :func:`get_default_version <hl7apy.get_default_version>`)

    :param validation_level: the validation level. Possible values are those defined in
        :class:`VALIDATION_LEVEL <hl7apy.consts.VALIDATION_LEVEL>` or ``None`` to use the default validation
        level (see :func:`get_default_validation_level <hl7apy.get_default_validation_level>`)
    """
    child_parser = ('parse_segment', 'parse_segments')

    def __init__(self, name=None, parent=None, reference=None, version=None,
                 validation_level=None, traversal_parent=None):

        self.child_classes = (Segment, Group)
        super(Group, self).__init__(name, parent, reference, version, validation_level, traversal_parent)
        if self.name is None and Validator.is_strict(self.validation_level):
            raise OperationNotAllowed("Cannot instantiate an unknown Element with strict validation")

    def add_segment(self, name):
        """
        Create an instance of :class:`Segment <hl7apy.core.Segment>` having the given name

        :param name: the name of the segment to be created (e.g. PID)
        :return: an instance of :class:`Segment <hl7apy.core.Segment>`

        >>> m = Message('QBP_Q11')
        >>> qpd = m.add_segment('QPD')
        >>> print(qpd)
        <Segment QPD>
        >>> print(qpd in m.children)
        True
        """
        return self.children.create_element(name)

    def add_group(self, name):
        """
        Create an instance of :class:`Group <hl7apy.core.Group>` having the given name

        :param name: the name of the group to be created (e.g. OML_O33_PATIENT)
        :return: an instance of :class:`Group <hl7apy.core.Group>`

        >>> m = Message('OML_O33')
        >>> patient = m.add_group('OML_O33_PATIENT')
        >>> print(patient)
        <Group OML_O33_PATIENT>
        >>> print(patient in m.children)
        True
        """

        return self.children.create_element(name)

    def find_child_reference(self, name):
        name = name.upper()
        if isinstance(self.structure_by_name, collections.MutableMapping):
            element = self.structure_by_name.get(name) or self.structure_by_longname.get(name)
        else:
            element = None
        if element is None:  # not found in self.structure
            if _valid_z_segment_name(name):
                element = {'cls': Segment, 'name': name, 'ref': ('sequence', ())}
            else:
                element = find_reference(name, self.child_classes, self.version)
                if Validator.is_strict(self.validation_level):  # cannot be created if validation is strict
                    raise ChildNotValid(name, self)
        return element

    def parse_child(self, text, child_name=None, reference=None):
        ref = self.find_child_reference(child_name)
        if ref['cls'] == Group:
            g = Group(child_name, validation_level=self.validation_level, version=self.version,
                      reference=ref['ref'])
            g.value = text
            return g
        else:
            # Check that the value starts with the correct name of the segment.
            # If it doesn't, it sets the reference to None to force the initializer to search again for the
            # segment reference. # This is done to avoid situation like m.zip = 'PAP|||asb|' which results in
            # this call to parse childparse_child(self, 'PAP|||asb|', 'zip', ('sequence', ()))
            if text[:3] != child_name:
                reference = None
            kwargs = {'encoding_chars': self.encoding_chars, 'reference': reference}
            return Element.parse_child(self, text, **kwargs)

    def parse_children(self, text, find_groups=True, **kwargs):
        from bika.lims.exportimport.instruments.genexpert.hl7apy.parser import create_groups
        kwargs = {'references': self.structure_by_name}
        children = super(Group, self).parse_children(text, **kwargs)
        if self.name and find_groups:
            self.children = []
            create_groups(self, children, validation_level=self.validation_level)
        else:
            self.children = children

    def _set_value(self, value):
        self.parse_children(value)

    def _get_value(self):
        return self.to_er7()

    value = property(_get_value, _set_value)

    def _is_valid_child(self, child):
        if child.name is None and Validator.is_strict(self.validation_level):
            return False
        return Element._is_valid_child(self, child)

    def _get_children(self, trailing=False):
        if Validator.is_strict(self.validation_level):
            children = self.children.get_ordered_children()
        else:
            children = self.children.get_children()
        if not trailing:
            children = _remove_trailing(children)
        return children


class Message(Group):
    """
    Class representing an HL7 message

    :type name: ``str``
    :param name: the HL7 name of the message (e.g. OML_O33)

    :type name: ``str``
    :param name: the HL7 name of the segment (e.g. PID)

    :type encoding_chars: ``dict``
    :param encoding_chars: a dictionary containing the encoding chars or None to use the default
        (see :func:`get_default_encoding_chars <hl7apy.get_default_encoding_chars>`)
    """
    def __init__(self, name=None, reference=None, version=None, validation_level=None, encoding_chars=None):

        if reference is not None:
            try:
                reference = reference[name]
            except KeyError:
                raise MessageProfileNotFound()
            except TypeError:
                pass
        try:
            super(Message, self).__init__(name, None, reference, version,
                                          validation_level)
        except InvalidName:
            if _valid_z_message_name(name):
                reference = ('sequence', ())
                super(Message, self).__init__(name, None, reference, version,
                                              validation_level)
            else:
                raise

        if encoding_chars is None:
            encoding_chars = get_default_encoding_chars()

        # TODO: Change it to support message profiles
        self.msh = Segment('MSH', version=self.version, validation_level=self.validation_level)
        self.encoding_chars = encoding_chars
        self.msh.msh_7 = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        self.msh.msh_12 = self.version

    def find_child_reference(self, name):
        name = name.upper()
        if isinstance(self.structure_by_name, collections.MutableMapping):
            element = self.structure_by_name.get(name) or self.structure_by_longname.get(name)
        else:
            element = None
        if element is None:  # not found in self.structure
            if _valid_z_segment_name(name):
                element = {'cls': Segment, 'name': name, 'ref': ('sequence', ())}
            else:
                element = find_reference(name, self.child_classes, self.version)
                if not self.is_z_element() and Validator.is_strict(self.validation_level):
                    raise ChildNotValid(name, self)
        return element

    def parse_children(self, text, find_groups=True, **kwargs):
        from bika.lims.exportimport.instruments.genexpert.hl7apy.parser import get_message_info

        encoding_chars, message_structure, version = get_message_info(text)

        if not self.is_unknown() and self.name != message_structure:
            raise OperationNotAllowed('Cannot assign a message with a different name')
        elif self.is_unknown():  # the message become a known message
            self.name = message_structure
            self._find_structure()
        if self.version != version:
            raise OperationNotAllowed('Cannot assign a message with a different version')
        elif self.encoding_chars != encoding_chars:
            raise OperationNotAllowed('Cannot assign a message with different encoding chars')

        super(Message, self).parse_children(text, find_groups, **kwargs)

    def to_mllp(self, encoding_chars=None, trailing_children=False):
        """
        Returns the er7 representation of the message wrapped with mllp encoding characters

        :type encoding_chars: ``dict``
        :param encoding_chars: a dictionary containing the encoding chars or None to use the default
            (see :func:`get_default_encoding_chars <hl7apy.get_default_encoding_chars>`)

        :type trailing_children: ``bool``
        :param trailing_children: if ``True``, trailing children will be added even if their value is ``None``

        :return: the ER7-encoded string wrapped with the mllp encoding characters
        """
        if encoding_chars is None:
            encoding_chars = self.encoding_chars

        return "{0}{1}{2}{3}{2}".format(MLLP_ENCODING_CHARS.SB,
                                        self.to_er7(encoding_chars, trailing_children),
                                        MLLP_ENCODING_CHARS.CR,
                                        MLLP_ENCODING_CHARS.EB)

    def is_z_element(self):
        return _valid_z_message_name(self.name)

    def _get_encoding_chars(self):
        msh_2 = self.msh.msh_2.msh_2_1.children[0].value.value
        return {
            'FIELD': self.msh.msh_1.msh_1_1.children[0].value.value,
            'COMPONENT': msh_2[0],
            'REPETITION': msh_2[1],
            'ESCAPE': msh_2[2],
            'SUBCOMPONENT': msh_2[3],
            'GROUP': '\r',
            'SEGMENT': '\r',
        }

    def _set_encoding_chars(self, encoding_chars):
        check_encoding_chars(encoding_chars)
        msh_1 = Field('MSH_1', validation_level=self.validation_level, version=self.version)
        msh_2 = Field('MSH_2', validation_level=self.validation_level, version=self.version)
        msh_1.st = encoding_chars['FIELD']
        value = '{0}{1}{2}{3}'.format(encoding_chars['COMPONENT'],
                                      encoding_chars['REPETITION'],
                                      encoding_chars['ESCAPE'],
                                      encoding_chars['SUBCOMPONENT'])
        s = SubComponent(datatype='ST', value=value,
                         validation_level=self.validation_level, version=self.version)
        c = Component(datatype='ST', validation_level=self.validation_level,
                      version=self.version)
        c.add(s)
        msh_2.st = c
        self.msh.msh_1 = msh_1
        self.msh.msh_2 = msh_2

    encoding_chars = property(_get_encoding_chars, _set_encoding_chars)


if __name__ == '__main__':

    import doctest
    doctest.testmod()
