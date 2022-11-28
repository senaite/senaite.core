# SENAITE Widgets

This package contains widgets for Dexterity fields.

A widget is redered as HTML element for input, display and hidden modes.
It is not bound to a sepecific field and needs just a request to be created.

However, in SENAITE we often define a specific field for a widget and provide
only for this field a factory function.

## When is is useful to have an explicit field

Some attributes make more sense to keep them on field level, e.g. in the
`UIDReferenceField` we like to define if it is multi-valued or in the `IntField`
we define the min/max values.

One of the reasons is that the field setter is called without the widget
involved when values are set over the JSON API.

NOTE: All SENAITE widgets always use the field setter/getter and do not write
      the value directly to the attribute!

## Data Manager

A specific data manager is defined in the `datamanagers` module to adapt any
context to a SENAITE field.

Instead of setting the value directly, it uses the `set` method of the field
instead.  Of course, this can be bypassed with a more specific adapter.

See `z3c/form/datamanager.txt` for a more detailed explanation.


## Widget

A widget is a simple class that inherits from the `WidgetLayoutSupport` and the
`Widget` base classes:

    from zope.interface import implementer_only
    from senaite.core.z3cform.interfaces import IQuerySelectWidget
    from z3c.form.browser import widget
    from z3c.form.widget import Widget

    @implementer_only(IQuerySelectWidget)
    class QuerySelectWidget(widget.HTMLInputWidget, Widget):
        """A widget to select one or more items from catalog search
        """
        klass = u"queryselect-widget"


The base class `widget.HTMLInputWidget` is a *layout* mixin, that basically only
defines some attributes, e.g. `readonly`, `disabled`, `title`, `style` etc.

The second base class `Widget` provides the logic to render, extract and updat
the widget value(s).


A widget factory is the actual adapter for a specific field and request:


    @adapter(IField, ISenaiteFormLayer)
    @implementer(IFieldWidget)
    def QuerySelectWidgetFactory(field, request):
        """Widget factory
        """
        return FieldWidget(field, QuerySelectWidget(request))
        

This factory adapter is registered in ZCML:

    <configure
        xmlns="http://namespaces.zope.org/zope"
        xmlns:z3c="http://namespaces.zope.org/z3c"
        xmlns:browser="http://namespaces.zope.org/browser">

    <!-- permission -->
    <class class=".widget.QuerySelectWidget">
        <require
            permission="zope.Public"
            interface="senaite.core.z3cform.interfaces.IQuerySelectWidget" />
    </class>

    <!-- Widget factory (the first interface for the field! Maybe use lines field here?) -->
    <adapter factory=".widget.QuerySelectWidgetFactory" />
            
Note the `IField` matches any field interface!

Finally, the widget templates need to be registered for the widget:

    <configure
        xmlns="http://namespaces.zope.org/zope"
        xmlns:z3c="http://namespaces.zope.org/z3c"
        xmlns:browser="http://namespaces.zope.org/browser">

    <!-- INPUT template -->
    <z3c:widgetTemplate
        mode="input"
        widget="senaite.core.z3cform.interfaces.IQuerySelectWidget"
        layer="senaite.core.interfaces.ISenaiteFormLayer"
        template="input.pt"
        />

    <!-- DISPLAY template -->
    <z3c:widgetTemplate
        mode="display"
        widget="senaite.core.z3cform.interfaces.IQuerySelectWidget"
        layer="senaite.core.interfaces.ISenaiteFormLayer"
        template="display.pt"
        />

    <!-- HIDDEN template -->
    <z3c:widgetTemplate
        mode="hidden"
        widget="senaite.core.z3cform.interfaces.IQuerySelectWidget"
        layer="senaite.core.interfaces.ISenaiteFormLayer"
        template="hidden.pt"
        />

    </configure>
    
HINT: You can use in the templates all of the defined attributes from the
     *layout* mixin class!
