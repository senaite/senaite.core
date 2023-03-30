API Label
---------

The label API provides a simple interface to manage object labels.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t API_label


Test Setup
..........

Needed Imports:

    >>> from senaite.core.api.label import *

    >>> from bika.lims import api
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD


Environment Setup
.................

Setup the testing environment:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = api.get_setup()
    >>> setRoles(portal, TEST_USER_ID, ['LabManager', ])
    >>> user = api.get_current_user()


List all Labels
...............

List all active global labels in the system:

    >>> list_labels()
    []


Create some Labels
..................

Create global labels:

    >>> new = map(create_label, ["Important", "Urgent", "Critical"])
    >>> list_labels(sort_on="title")
    ['Critical', 'Important', 'Urgent']

Duplicates are ignored per default:

    >>> new = create_label("Important")
    >>> list_labels(sort_on="title")
    ['Critical', 'Important', 'Urgent']


Label content objects
.....................

Basically all objects can be labeled, both AT or DX based.

Try first to label some AT based objects

    >>> client1 = api.create(portal.clients, "Client", Name="NARALABS", ClientID="NL")
    >>> client2 = api.create(portal.clients, "Client", Name="RIDINGBYTES", ClientID="RB")
    >>> client3 = api.create(portal.clients, "Client", Name="SENAITE", ClientID="SNT")

Add a string label:

    >>> add_obj_labels(client1, "Important")
    ('Important',)

Add multiple labels:

    >>> add_obj_labels(client1, ["Important", "Urgent", "SENAITE", "Label"])
    ('Important', 'Label', 'SENAITE', 'Urgent')

Labels are alway sorted before they are stored:

    >>> add_obj_labels(client1, ["A", "Z"])
    ('A', 'Important', 'Label', 'SENAITE', 'Urgent', 'Z')

Labels can be also removed:

    >>> del_obj_labels(client1, "A")
    ('Important', 'Label', 'SENAITE', 'Urgent', 'Z')

Non existing labels are simple ignored:

    >>> del_obj_labels(client1, "X")
    ('Important', 'Label', 'SENAITE', 'Urgent', 'Z')

Remove all labels:

    >>> del_obj_labels(client1, get_obj_labels(client1))
    ()


Schema extension
................

Objects with labels are automatically schema extended to allow to add/remove
labels over the user interface.

The schema extension is controlled over the `ICanHaveLabels` interface:

    >>> from senaite.core.interfaces import ICanHaveLabels
    >>> from senaite.core.config.fields import AT_LABEL_FIELD

    >>> client4 = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH")

    >>> ICanHaveLabels.providedBy(client4)
    False

    >>> AT_LABEL_FIELD in api.get_fields(client4)
    False

    >>> add_obj_labels(client4, "Demo")
    ('Demo',)

    >>> ICanHaveLabels.providedBy(client4)
    True

    >>> AT_LABEL_FIELD in api.get_fields(client4)
    True

Schema extension for dexterity types works via behaviors:

    >>> from senaite.core.config.fields import DX_LABEL_FIELD

    >>> container1 = api.create(setup.sample_containers, "SampleContainer", title="Glass Bottle", Capacity="500ml")

    >>> ICanHaveLabels.providedBy(container1)
    False

    >>> DX_LABEL_FIELD in api.get_fields(container1)
    False

    >>> add_obj_labels(container1, "Bottles")
    ('Bottles',)

    >>> ICanHaveLabels.providedBy(container1)
    True

    >>> DX_LABEL_FIELD in api.get_fields(container1)
    True

Enable labels for **all** objects of a certain AT type:

    >>> enable_labels_for_type("Client")

    >>> at_type = api.create(portal.clients, "Client", Name="New Client", ClientID="C1")

    >>> ICanHaveLabels.providedBy(at_type)
    True

Disable labels for **all** objects of a certain AT type:

    >>> disable_labels_for_type("Client")

    >>> at_type = api.create(portal.clients, "Client", Name="New Client", ClientID="C2")

    >>> ICanHaveLabels.providedBy(at_type)
    False


Enable labels for **all** objects of a certain DX type:

    >>> enable_labels_for_type("InterpretationTemplate")

    >>> dx_type = api.create(setup.interpretation_templates, "InterpretationTemplate", title="New Interpretation Template")

    >>> ICanHaveLabels.providedBy(dx_type)
    True

Disable labels for **all** objects of a certain DX type:

    >>> disable_labels_for_type("InterpretationTemplate")

    >>> dx_type = api.create(setup.interpretation_templates, "InterpretationTemplate", title="New Interpretation Template")

    >>> ICanHaveLabels.providedBy(dx_type)
    False


Search Labels
.............

Labels can be searched via the API and return all labeled objects:

    >>> l1 = add_obj_labels(client1, ["SENAITE", "Barcelona", "Spain"])
    >>> l2 = add_obj_labels(client2, ["SENAITE", "Fürth", "Germany"])
    >>> l3 = add_obj_labels(client3, ["SENAITE", "LIMS"])

    >>> results = search_objects_by_label("Spain")
    >>> len(results) == 1
    True
    >>> api.get_object(results[0]) == client1
    True

    >>> results = search_objects_by_label("Fürth")
    >>> len(results) == 1
    True
    >>> api.get_object(results[0]) == client2
    True

    >>> results = search_objects_by_label("Fürth")
    >>> len(results) == 1
    True
    >>> api.get_object(results[0]) == client2
    True

    >>> results = search_objects_by_label(["SENAITE"])
    >>> len(results) == 3
    True
