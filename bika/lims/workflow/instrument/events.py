# -*- coding: utf-8 -*-

from bika.lims import api


def after_deactivate(instrument):
    """Function triggered after a 'deactivate' transition for the instrument
    passed in is performed.
    """

    # remove the deactivated instrument from all assigned methods
    for method in instrument.getMethods():
        instruments = method.getInstruments()
        instruments.remove(instrument)
        instrument_uids = map(api.get_uid, instruments)
        method.setInstruments(instrument_uids)
        method.reindexObject()
