# -*- coding: utf-8 -*-

from plone.app.textfield import RichText
from senaite.core.schema.fields import BaseField
from zope.interface import implementer
from senaite.core.schema.interfaces import IRichTextField


@implementer(IRichTextField)
class RichTextField(RichText, BaseField):
    """A field that handles markup texts
    """

    def set(self, object, value):
        """Set field value

        :param object: the instance of the field
        :param value: value to set
        """
        super(RichTextField, self).set(object, value)

    def get(self, object):
        """Get the field value

        :param object: the instance of the field
        :returns: field value
        """
        value = super(RichTextField, self).get(object)
        return value

    def _validate(self, value):
        """Validator when called from form submission
        """
        super(RichTextField, self)._validate(value)
