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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

from types import ClassType
from types import DictType
from types import FileType
from types import IntType
from types import ListType
from types import StringType
from types import StringTypes
from types import TupleType
from types import UnicodeType

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from DateTime import DateTime
from Products.Archetypes.atapi import DisplayList
from Products.Archetypes.debug import log
from Products.Archetypes.Field import ObjectField
from Products.Archetypes.Field import decode
from Products.Archetypes.Field import encode
from Products.Archetypes.Registry import registerField
from Products.Archetypes.Registry import registerPropertyType
from Products.CMFCore.Expression import Expression
from Products.CMFCore.Expression import createExprContext
from Products.CMFCore.utils import getToolByName
from Products.PythonScripts.standard import html_quote
from senaite.core.browser.fields.utils import getDisplayList
from senaite.core.browser.widgets.recordwidget import RecordWidget

# we have to define our own validation handling
try:
    from Products.validation import ValidationChain
    from Products.validation import UnknowValidatorError
    from Products.validation import FalseValidatorError
    from Products.validation.interfaces.IValidator \
         import IValidator, IValidationChain
    HAS_VALIDATION_CHAIN = 1
except ImportError:
    HAS_VALIDATION_CHAIN = 0


def providedBy(interface, obj):
    if getattr(interface, 'providedBy', None):
        return interface.providedBy(obj)
    return interface.isImplementedBy(obj)


class RecordField(ObjectField):
    """A field that stores a "record" (dictionary-like) construct"""
    _properties = ObjectField._properties.copy()
    _properties.update({
        "type": "record",
        "default": {},
        "subfields": (),
        "subfield_types": {},
        "subfield_vocabularies": {},
        "subfield_labels": {},
        "subfield_sizes": {},
        "subfield_maxlength": {},
        "required_subfields": (),
        "subfield_validators": {},
        "subfield_conditions": {},
        "subfield_descriptions": {},
        "innerJoin": ", ",
        "outerJoin": ", ",
        "widget": RecordWidget,
        })

    security = ClassSecurityInfo()

    security.declarePublic('getSubfields')
    def getSubfields(self):
        """the tuple of sub-fields"""
        return self.subfields

    security.declarePublic('getSubfieldType')
    def getSubfieldType(self, subfield):
        """
        optional type declaration
        default: string
        """
        return self.subfield_types.get(subfield, 'string')

    security.declarePublic('getSubfieldLabel')
    def getSubfieldLabel(self, subfield):
        """
        optional custom label for the subfield
        default: the id of the subfield
        """
        return self.subfield_labels.get(subfield, subfield.capitalize())

    security.declarePublic('getSubfieldDescription')
    def getSubfieldDescription(self, subfield):
        """
        optional custom description for the subfield
        """
        return self.subfield_descriptions.get(subfield)

    def getSubfieldSize(self, subfield, default=40):
        """
        optional custom size for the subfield
        default: 40
        only effective for string type subfields
        """
        return self.subfield_sizes.get(subfield, default)

    def getSubfieldMaxlength(self, subfield):
        """
        otional custom maxlength size for the subfield
        only effective for string type subfields
        """
        return self.subfield_maxlength.get(subfield, 40)

    def isRequired(self,subfield):
        """
        looks whether subfield is included in the list of required subfields
        """
        return subfield in self.required_subfields

    def isSelection(self,subfield):
        """select box needed?"""

        return self.subfield_vocabularies.has_key(subfield)

    security.declarePublic('testSubfieldCondition')
    def testSubfieldCondition(self, subfield, folder, portal, object):
        """Test the subfield condition."""
        try:
            condition = self.subfield_conditions.get(subfield, None)
            if condition is not None:
                __traceback_info__ = (folder, portal, object, condition)
                ec = createExprContext(folder, portal, object)
                return Expression(condition)(ec)
            else:
                return True
        except AttributeError:
            return True

    def getVocabularyFor(self, subfield, instance=None):
        """the vocabulary (DisplayList) for the subfield"""
        ## XXX rr: couldn't we just rely on the field's
        ## Vocabulary method here?
        value = None
        vocab = self.subfield_vocabularies.get(subfield, None)
        if not vocab:
            raise AttributeError("No vocabulary found for {}".format(subfield))

        if isinstance(vocab, DisplayList):
            return vocab

        if type(vocab) in StringTypes:
            value = None
            method = getattr(self, vocab, None)
            if method and callable(method):
                value = method(instance)
            else:
                if instance is not None:
                    method = getattr(instance, vocab, None)
                    if method and callable(method):
                        value = method()
            if not isinstance(value, DisplayList):
                msg = "{} is not a DisplayList {}".format(value, subfield)
                raise TypeError(msg)
            return value

        msg = "{} is not a string or DisplayList for {}".format(vocab, subfield)
        raise TypeError(msg)

    def getViewFor(self, instance, subfield, joinWith=', '):
        """
        formatted value of the subfield for display
        """
        raw = self.getRaw(instance).get(subfield,'')
        if type(raw) in (type(()), type([])):
            raw = joinWith.join(raw)
        # Prevent XSS attacks by quoting all user input
        raw = html_quote(str(raw))
        # this is now very specific
        if subfield == 'email':
            return self.hideEmail(raw,instance)
        if subfield == 'phone':
            return self.labelPhone(raw)
        if subfield == 'fax':
            return self.labelFax(raw)
        if subfield == 'homepage':
            return '<a href="%s">%s</a>' % (raw, raw)
        return raw

    def getSubfieldViews(self,instance,joinWith=', '):
        """
        list of subfield views for non-empty subfields
        """
        result = []
        for subfield in self.getSubfields():
            view = self.getViewFor(instance,subfield,joinWith)
            if view:
                result.append(view)
        return result

    # this is really special purpose and in no ways generic
    def hideEmail(self,email='',instance=None):
	masked = 'email: ' + \
                 email.replace('@', ' (at) ').replace('.', ' (dot) ')
	membertool = getToolByName(instance,'portal_membership',None)
	if membertool is None or membertool.isAnonymousUser():
	    return masked
	return "<a href='mailto:%s'>%s</a>" % (email,email)

    def labelPhone(self,phone=''):
        return 'phone: ' + phone

    def labelFax(self,fax=''):
        return 'fax: ' + fax

    # enable also a string representation of a dictionary
    # to be passed in (external edit may need this)
    # store string values as unicode

    def set(self, instance, value, **kwargs):
        if type(value) in StringTypes:
            try:
                value = eval(value)
                # more checks to add?
            except: # what to catch here?
                pass
        value = self._to_dict(value)
        value = self._decode_strings(value, instance, **kwargs)
        ObjectField.set(self, instance, value, **kwargs)

    def _to_dict(self, value):
        if type(value) != type({}) and hasattr(value, 'keys'):
            new_value = {}
            new_value.update(value)
            return new_value
        return value

    def _decode_strings(self, value, instance, **kwargs):
        new_value = value
        for k, v in value.items():
            if type(v) is type(''):
                nv =  decode(v, instance, **kwargs)
                try:
                    new_value[k] = nv
                except AttributeError: # Records don't provide __setitem__
                    setattr(new_value, k , nv)

            # convert datetimes
            if self.subfield_types.get(k, None) == 'datetime':
                try:
                    val = DateTime(v)
                except:
                    val = None

                new_value[k] = val

        return new_value

    # Return strings using the site's encoding

    def get(self, instance, **kwargs):
        value = ObjectField.get(self, instance, **kwargs)
        return self._encode_strings(value, instance, **kwargs)

    def _encode_strings(self, value, instance, **kwargs):
        new_value = value
        for k, v in value.items():
            if type(v) is type(u''):
                nv = encode(v, instance, **kwargs)
                try:
                    new_value[k] = nv
                except AttributeError: # Records don't provide __setitem__
                    setattr(new_value, k , nv)
        return new_value

    if HAS_VALIDATION_CHAIN:
        def _validationLayer(self):
            """
            Resolve that each validator is in the service. If validator is
            not, log a warning.

            We could replace strings with class refs and keep things impl
            the ivalidator in the list.

            Note: XXX this is not compat with aq_ things like scripts with __call__
            """
            for subfield in self.getSubfields():
                self.subfield_validators[subfield] = self._subfieldValidationLayer(subfield)

        def _subfieldValidationLayer(self, subfield):
            """
            for the individual subfields
            """
            chainname = 'Validator_%s_%s' % (self.getName(), subfield)
            current_validators = self.subfield_validators.get(subfield, ())

            if type(current_validators) is DictType:
                msg = "Please use the new syntax with validation chains"
                raise NotImplementedError(msg)
            elif IValidationChain.providedBy(current_validators):
                validators = current_validators
            elif IValidator.providedBy(current_validators):
                validators = ValidationChain(chainname, validators=current_validators)
            elif type(current_validators) in (TupleType, ListType, StringType):
                if len(current_validators):
                    # got a non empty list or string - create a chain
                    try:
                        validators = ValidationChain(chainname, validators=current_validators)
                    except (UnknowValidatorError, FalseValidatorError) as msg:
                        log("WARNING: Disabling validation for %s/%s: %s" % (self.getName(), subfield, msg))
                        validators = ()
                else:
                    validators = ()
            else:
                log('WARNING: Unknow validation %s. Disabling!' % current_validators)
                validators = ()

            if not subfield in self.required_subfields:
                if validators == ():
                    validators = ValidationChain(chainname)
                if len(validators):
                    # insert isEmpty validator at position 0 if first validator
                    # is not isEmpty
                    if not validators[0][0].name == 'isEmpty':
                        validators.insertSufficient('isEmpty')
                else:
                    validators.insertSufficient('isEmpty')

            return validators

        security.declarePublic('validate')
        def validate(self, value, instance, errors={}, **kwargs):
            """
            Validate passed-in value using all subfield validators.
            Return None if all validations pass; otherwise, return failed
            result returned by validator
            """
            name = self.getName()
            if errors and errors.has_key(name):
                return True

            if self.required_subfields:
                for subfield in self.required_subfields:
                    sub_value = value.get(subfield, None)
                    res = self.validate_required(instance, sub_value, errors)
                    if res is not None:
                        return res

            # not touched yet
            if self.enforceVocabulary:
                res = self.validate_vocabulary(instance, value, errors)
                if res is not None:
                    return res

            # can this part stay like it is?
            res = instance.validate_field(name, value, errors)
            if res is not None:
                return res

            # this should work
            if self.subfield_validators:
                res = self.validate_validators(value, instance, errors, **kwargs)
                if res is not True:
                    return res

            # all ok
            return None

        def validate_validators(self, value, instance, errors, **kwargs):
            result = True
            total = ''
            for subfield in self.getSubfields():
                subfield_validators = self.subfield_validators.get(subfield, None)
                if subfield_validators:
                    result = subfield_validators(value.get(subfield),
                                                 instance=instance,
                                                 errors=errors,
                                                 field=self,
                                                 **kwargs
                                                 )
                if result is not True:
                    total += result
            return total or result


InitializeClass(RecordField)


registerField(RecordField, title="Record", description="")

registerPropertyType('subfields', 'lines', RecordField)
registerPropertyType('required_subfields', 'lines', RecordField)
registerPropertyType('subfield_validators', 'mapping', RecordField)
registerPropertyType('subfield_types', 'mapping', RecordField)
registerPropertyType('subfield_vocabularies', 'mapping', RecordField)
registerPropertyType('subfield_labels', 'mapping', RecordField)
registerPropertyType('subfield_sizes', 'mapping', RecordField)
registerPropertyType('subfield_maxlength', 'mapping', RecordField)
registerPropertyType('innerJoin', 'string', RecordField)
registerPropertyType('outerJoin', 'string', RecordField)
