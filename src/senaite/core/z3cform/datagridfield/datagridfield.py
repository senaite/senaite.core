# -*- coding: utf-8 -*-
#
# Vendored from collective.z3cform.datagridfield 1.5.3.
# See senaite/core/z3cform/datagridfield/__init__.py for details.
"""
    Implementation of the widget
"""
from Acquisition import aq_parent
from senaite.core.z3cform.datagridfield.autoform import AutoExtensibleSubForm
from senaite.core.z3cform.datagridfield.autoform import AutoExtensibleSubformAdapter  # noqa: E501
from senaite.core.z3cform.datagridfield.interfaces import IDataGridField
from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.app.z3cform.utils import closest_content
from plone.autoform.interfaces import MODES_KEY
from plone import api
from z3c.form import interfaces
from z3c.form.browser.multi import MultiWidget
from z3c.form.browser.object import ObjectWidget
from z3c.form.converter import BaseDataConverter
from z3c.form.converter import FormatterValidationError
from z3c.form.error import MultipleErrors
from z3c.form.field import Fields
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import INPUT_MODE
from z3c.form.interfaces import IValidator
from z3c.form.validator import SimpleFieldValidator
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface
from zope.schema import getFieldNames
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import IField
from zope.schema.interfaces import IList
from zope.schema.interfaces import IObject
from zope.schema.interfaces import ValidationError
from . import _

import logging
import lxml
import pkg_resources


try:
    pkg_resources.get_distribution('z3c.relationfield')
    from z3c.relationfield.schema import RelationChoice
    HAS_REL_FIELD = True
except pkg_resources.DistributionNotFound:
    HAS_REL_FIELD = False

logger = logging.getLogger(__name__)


@implementer(IDataGridField)
class DataGridField(MultiWidget):
    """This grid should be applied to an schema.List item which has
    schema.Object and an interface"""

    allow_insert = True
    allow_delete = True
    allow_reorder = False
    auto_append = True
    display_table_css_class = "datagridwidget-table-view"

    klass = "datagridfield"

    # You can give data-extra attribute
    # for the widget to allow there some custom
    # JSON payload concerning all rows
    extra = None

    # Define all possible template backends

    @property
    def field(self):
        return self._field

    @field.setter
    def field(self, value):
        """
            The field information is passed to the widget after it is
            initialised.  Use this call to initialise the column
            definitions.
        """
        self._field = value
        schema = self._field.value_type.schema

        fieldmodes = {}
        if MODES_KEY:
            try:
                modes_tags = schema.getTaggedValue(MODES_KEY)
            except KeyError:
                pass
            else:
                for __, fieldname, mode in modes_tags:
                    fieldmodes[fieldname] = mode

        self.columns = []
        for name, field in getFieldsInOrder(schema):
            col = {
                'name': name,
                'label': field.title,
                'description': field.description,
                'required': field.required,
                'mode': fieldmodes.get(name, None),
            }
            self.columns.append(col)

    def createObjectWidget(self, idx):
        """
        Create the widget which handles individual rows.

        Allow row-widget overriding for more specific use cases.
        """

        valueType = self.field.value_type

        if IObject.providedBy(valueType):
            widget = DataGridFieldObjectFactory(valueType, self.request)
            widget.setErrors = idx not in ['TT', 'AA']
        else:
            widget = getMultiAdapter(
                (valueType, self.request),
                interfaces.IFieldWidget
            )

        return widget

    def getWidget(self, idx):
        """Create the object widget. This is used to avoid looking up
        the widget.
        """

        widget = self.createObjectWidget(idx)

        # widgets.line1 -> form-widgets-address-0-widgets-line1
        self.setName(widget, idx)

        widget.__parent__ = self

        widget.mode = self.mode
        widget.klass = 'datagridwidget-row'
        # set widget.form (objectwidget needs this)
        if interfaces.IFormAware.providedBy(self):
            widget.form = self.form
            alsoProvides(
                widget,
                interfaces.IFormAware
            )
        widget.update()
        return widget

    def name_prefix(self):
        return self.prefix

    def id_prefix(self):
        return self.prefix.replace('.', '-')

    def updateWidgets(self):

        if self.mode == INPUT_MODE:
            # filter out any auto append or template rows
            # these are not "real" elements of the MultiWidget
            # and confuse updateWidgets method if len(self.widgets) changes
            # This is relevant for nested datagridfields.
            self.widgets = [
                w for w in self.widgets
                if not (w.id.endswith('AA') or w.id.endswith('TT'))
            ]

        # if the field has configuration data set - copy it
        super(DataGridField, self).updateWidgets()

        if self.mode == INPUT_MODE:
            if self.auto_append:
                # If we are doing 'auto-append', then a blank row
                # needs to be added
                widget = self.getWidget('AA')
                widget.klass = 'datagridwidget-row auto-append'
                self.widgets.append(widget)

            if self.auto_append or self.allow_insert:
                # If we can add rows, we need a template row
                template = self.getWidget('TT')
                template.klass = 'datagridwidget-row datagridwidget-empty-row'
                self.widgets.append(template)

    def setName(self, widget, idx):
        """This version facilitates inserting non-numerics"""
        widget.name = '%s.%s' % (self.name, idx)
        widget.id = '%s-%s' % (self.id, idx)

    @property
    def counterMarker(self):
        # Override this to exclude template line and auto append line
        counter = len(self.widgets)
        if self.auto_append:
            counter -= 1
        if self.auto_append or self.allow_insert:
            counter -= 1
        return '<input type="hidden" name="%s" value="%d" />' % (
            self.counterName, counter)

    def _includeRow(self, name):
        if self.mode == INPUT_MODE:
            if not name.endswith('AA') and not name.endswith('TT'):
                return True
            if name.endswith('AA'):
                return self.auto_append
            if name.endswith('TT'):
                return self.auto_append or self.allow_insert
        else:
            return not name.endswith('AA') and not name.endswith('TT')

    def portal_url(self):
        return api.portal.get_tool('portal_url')()


@adapter(IField, IFormLayer)
@implementer(interfaces.IFieldWidget)
def DataGridFieldFactory(field, request):
    """IFieldWidget factory for DataGridField."""
    return FieldWidget(field, DataGridField(request))


@adapter(IList, IDataGridField)
class GridDataConverter(BaseDataConverter):
    """Convert between the context and the widget"""

    def toWidgetValue(self, value):
        """Simply pass the data through with no change"""
        return value

    def toFieldValue(self, value):
        return value


# ------------[ Support for each line ]---------------------------------------

def datagrid_field_get(self):
    # value (get) cannot raise an exception, then we return
    # insane values
    try:
        return self.extract()
    except MultipleErrors:
        value = {}
        active_names = self.subform.fields.keys()
        for name in getFieldNames(self.field.schema):
            if name not in active_names:
                continue
            widget = self.subform.widgets[name]
            widget_value = widget.value
            try:
                converter = interfaces.IDataConverter(widget)
                value[name] = converter.toFieldValue(widget_value)
            except (FormatterValidationError, ValidationError, ValueError):
                value[name] = widget_value
    return value


def datagrid_field_set(self, value):
    self._value = value
    self.updateWidgets()

    # ensure that we apply our new values to the widgets
    if value is not interfaces.NO_VALUE:
        active_names = self.subform.fields.keys()
        for name in getFieldNames(self.field.schema):
            fieldset_field = self.field.schema[name]
            if fieldset_field.readonly:
                continue

            if name in active_names:
                if isinstance(value, dict):
                    v = value.get(name, interfaces.NO_VALUE)
                else:
                    v = getattr(value, name, interfaces.NO_VALUE)
                # probably there is a more generic way to do this ...
                if HAS_REL_FIELD and \
                        isinstance(fieldset_field, RelationChoice) \
                        and v == interfaces.NO_VALUE:
                    v = ''
                self.applyValue(self.subform.widgets[name], v)


PAT_XPATH = "//*[contains(concat(' ', normalize-space(@class), ' '), ' pat-')]"


class DataGridFieldObject(ObjectWidget):

    def isInsertEnabled(self):
        return self.__parent__.allow_insert

    def isDeleteEnabled(self):
        return self.__parent__.allow_delete

    def isReorderEnabled(self):
        return self.__parent__.allow_reorder

    def portal_url(self):
        return self.__parent__.context.portal_url()

    @property
    def value(self):
        return datagrid_field_get(self)

    @value.setter
    def value(self, value):
        return datagrid_field_set(self, value)

    def updateWidgets(self, *args, **kwargs):
        super(DataGridFieldObject, self).updateWidgets(*args, **kwargs)

        # Tell the "cell"-widget the "mode" of it's column,
        # so that plone.autoform.directives.mode works on the cell.
        for column_info in aq_parent(self).columns:
            if column_info['mode'] is None:
                continue
            self.subform.widgets[
                column_info['name']
            ].mode = column_info['mode']

    def render(self):
        """See z3c.form.interfaces.IWidget."""
        html = super(DataGridFieldObject, self).render()
        if (
            'datagridwidget-empty-row' in self.klass or
            'auto-append' in self.klass
        ):
            # deactivate patterns
            fragments = lxml.html.fragments_fromstring(html)
            html = ''
            for tree in fragments:
                for el in tree.xpath(PAT_XPATH):
                    if '.TT.' in el.attrib.get('name', ''):
                        el.attrib['class'] = el.attrib['class'].replace(
                            'pat-',
                            'dgw-disabled-pat-'
                        )
                html += lxml.html.tostring(tree, encoding='unicode') + '\n'
        return html

    def label_add_record(self):
        return _(
            'add_record_label',
            default='Add ${type}',
            mapping={'type': self.field.title}
        )


@adapter(IField, interfaces.IFormLayer)
@implementer(interfaces.IFieldWidget)
def DataGridFieldObjectFactory(field, request):
    """IFieldWidget factory for DataGridField."""
    return FieldWidget(field, DataGridFieldObject(request))


# ------------[ Form to draw the line ]---------------------------------------


class DataGridFieldObjectSubForm(AutoExtensibleSubForm):
    """Local class of subform - this is intended to all configuration
    information to be passed all the way down to the subform.

    All the parent and form nesting can be confusing, especially so
    when you throw fieldsets (groups) into the mix.  So some notes.

    When the datagrid object is part of a standard form without a
    fieldset, these are the objects:

    - self.__parent__ is a DataGridFieldObject

    - self.parentForm is self.__parent__.form is the main edit/add
      form or the view.

    - self.__parent__.__parent__ is the DataGridField

    - self.parentForm.__parent__ is the content item.

    When the datagrid object is part of a fieldset, these are the
    objects:

    - self.__parent__ is a DataGridFieldObject

    - self.parentForm is self.__parent__.form is the fieldset

    - self.parentForm.__parent__ is self.parentForm.parentForm is the
      main edit/add form or the view

    - self.__parent__.__parent__ is the DataGridField

    - self.parentForm.parentForm.__parent__ is the content item.

    """
    def __init__(self, context, request, parentWidget):
        # copied from z3c.form 3.2.10
        self.context = context
        self.request = request
        self.__parent__ = parentWidget
        self.parentForm = parentWidget.form
        self.ignoreContext = self.__parent__.ignoreContext
        self.ignoreRequest = self.__parent__.ignoreRequest
        if interfaces.IFormAware.providedBy(self.__parent__):
            self.ignoreReadonly = self.parentForm.ignoreReadonly
        self.prefix = self.__parent__.name

    def _validate(self):
        # copied from z3c.form 3.2.10
        for widget in self.widgets.values():
            try:
                # convert widget value to field value
                converter = interfaces.IDataConverter(widget)
                value = converter.toFieldValue(widget.value)
                # validate field value
                getMultiAdapter(
                    (self.context,
                     self.request,
                     self.parentForm,
                     getattr(widget, 'field', None),
                     widget),
                    interfaces.IValidator).validate(value, force=True)
            except (ValidationError, ValueError) as error:
                # on exception, setup the widget error message
                view = getMultiAdapter(
                    (error, self.request, widget, widget.field,
                     self.parentForm, self.context),
                    interfaces.IErrorViewSnippet)
                view.update()
                widget.error = view

    def update(self):
        # copied from z3c.form 3.2.10
        if self.__parent__.field is None:
            raise ValueError(
                "%r .field is None, that's a blocking point" % self.__parent__
            )
        # update stuff from parent to be sure
        self.mode = self.__parent__.mode
        self.setupFields()
        super(DataGridFieldObjectSubForm, self).update()

    def getContent(self):
        # copied from z3c.form 3.2.10
        return self.__parent__._value

    def updateWidgets(self):
        rv = super(DataGridFieldObjectSubForm, self).updateWidgets()
        if hasattr(self.parentForm, 'datagridUpdateWidgets'):
            self.parentForm.datagridUpdateWidgets(
                self,
                self.widgets,
                self.__parent__.__parent__
            )
        elif hasattr(self.parentForm.__parent__, 'datagridUpdateWidgets'):
            self.parentForm.__parent__.datagridUpdateWidgets(
                self,
                self.widgets,
                self.__parent__.__parent__
            )
        return rv

    def setupFields(self):
        # copied from z3c.form 3.2.10
        rv = Fields(self.__parent__.field.schema)

        # own code:
        if hasattr(self.parentForm, 'datagridInitialise'):
            self.parentForm.datagridInitialise(
                self,
                self.__parent__.__parent__
            )
        elif hasattr(self.parentForm.__parent__, 'datagridInitialise'):
            self.parentForm.__parent__.datagridInitialise(
                self,
                self.__parent__.__parent__
            )
        return rv

    def get_closest_content(self):
        """Return the closest persistent context to this form.
        The right context of this form is the object created by:
        z3c.form.object.registerFactoryAdapter
        """
        return closest_content(self.context)


@adapter(
    Interface,  # widget value
    IPloneFormLayer,           # request
    Interface,  # widget context
    Interface,  # form
    DataGridFieldObject,       # widget
    Interface,  # field
    Interface,  # field.schema
)
@implementer(interfaces.ISubformFactory)
class DataGridFieldSubformAdapter(AutoExtensibleSubformAdapter):
    """Give it my local class of subform, rather than the default"""

    factory = DataGridFieldObjectSubForm

    def __init__(self, context, request, widgetContext, form,
                 widget, field, schema):
        # copied from z3c.form 3.2.10
        self.context = context
        self.request = request
        self.widgetContext = widgetContext
        self.form = form
        self.widget = widget
        self.field = field
        self.schema = schema

    def __call__(self):
        # copied from z3c.form 3.2.10
        obj = self.factory(self.context, self.request, self.widget)
        return obj


@implementer(IValidator)
@adapter(
    Interface,
    Interface,
    Interface,  # Form
    IList,                     # field
    DataGridField,             # widgets
)
class DataGridValidator(SimpleFieldValidator):
    """
        I am crippling this validator - I return a list of
        dictionaries. If I don't cripple this it will fail because the
        return type is not of the correct object type. For stronger
        typing replace both this and the converter
    """

    def validate(self, value, force=False):
        """
            Don't validate the table - however, if there is a cell
            error, make sure that the table widget shows it.
        """
        for subform in [widget.subform for widget in self.widget.widgets]:
            for widget in subform.widgets.values():
                if hasattr(widget, 'error') and widget.error:
                    raise ValueError(widget.label)
        return None
