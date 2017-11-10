Instruments
===========

Bika LIMS supports the integration of instruments.

Some convenience imports for testing::

    >>> from bika.lims.interfaces import IInstrument
    >>> from bika.lims.interfaces import IInstrumentCertification

Instruments can only live inside the `bika_instruments` folder within the `bika_setup`.
We create one for testing and assing the location and domain::

    >>> instruments = self.portal.bika_setup.bika_instruments
    >>> _ = instruments.invokeFactory("Instrument", id="tempId", title="Test Instrument 1")
    >>> instrument = instruments.get(_)

We need to call `processForm` on the new created objects to notify the event handlers.
Bika LIMS will also rename the `id` of the contents in this step.

    >>> instrument.processForm()
    >>> instrument
    <Instrument at /plone/bika_setup/bika_instruments/instrument-1>

Instruments implement the `IInstrument` interface::

    >>> IInstrument.providedBy(instrument)
    True


Instrument Certification
------------------------

Instruments can contain certifications::

    >>> _ = instrument.invokeFactory("InstrumentCertification", id="tempId", title="Test Certification 1")
    >>> instrument_certification = instrument.get(_)
    >>> instrument_certification.processForm()
    >>> instrument_certification
    <InstrumentCertification at /plone/bika_setup/bika_instruments/instrument-1/instrumentcertification-1>

Certifications implement the `IInstrumentCertification` interface::

    >>> IInstrumentCertification.providedBy(instrument_certification)
    True
