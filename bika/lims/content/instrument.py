from AccessControl import ClassSecurityInfo
from Products.ATExtensions.ateapi import RecordsField
from DateTime import DateTime
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget
from Products.Archetypes.public import *
from Products.CMFCore.permissions import View, ModifyPortalContent
from bika.lims import bikaMessageFactory as _
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import PROJECTNAME
from bika.lims.browser.widgets import RecordsWidget
from zope.interface import implements

schema = BikaSchema.copy() + Schema((
    StringField('Type',
        widget = StringWidget(
            label = _("Instrument type"),
        )
    ),
    StringField('Brand',
        widget = StringWidget(
            label = _("Brand"),
            description = _("The commercial 'make' of the instrument"),
        )
    ),
    StringField('Model',
        widget = StringWidget(
            label = _("Model"),
            description = _("The instrument's model number"),
        )
    ),
    StringField('SerialNo',
        widget = StringWidget(
            label = _("Serial No"),
            description = _("The serial number that uniquely identifies the instrument"),
        )
    ),
    StringField('CalibrationCertificate',
        widget = StringWidget(
            label = _("Calibration Certificate"),
            description = _("The instrument's calibration certificate and number"),
        )
    ),
    DateTimeField('CalibrationExpiryDate',
        with_time = 0,
        with_date = 1,
        widget = DateTimeWidget(
            label = _("Calibration Expiry Date"),
            description = _("Due Date for next calibration"),
        ),
    ),
    StringField('DataInterface',
        vocabulary = "getDataInterfacesList",
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = _("Data Interface"),
            description = _("Select an Import/Export interface for this instrument."),
        ),
    ),
    RecordsField('DataInterfaceOptions',
        type = 'interfaceoptions',
        subfields = ('Key','Value'),
        required_subfields = ('Key','Value'),
        subfield_labels = {'OptionValue': _('Key'),
                           'OptionText': _('Value'),},
        widget = RecordsWidget(
            label = _("Data Interface Options"),
            description = _("Use this field to pass arbitrary parameters to the export/import "
                            "modules."),
        ),
    ),
))
schema['description'].widget.visible = True
schema['description'].schemata = 'default'

def getDataInterfaces(context):
    """ Return the current list of data interfaces
    """
    from bika.lims.exportimport import instruments
    exims = [('',context.translate(_('None')))]
    for exim_id in instruments.__all__:
        exim = getattr(instruments, exim_id)
        exims.append((exim_id, exim.title))
    return DisplayList(exims)

class Instrument(BaseContent):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getDataInterfacesList(self):
        return getDataInterfaces(self)

registerType(Instrument, PROJECTNAME)
