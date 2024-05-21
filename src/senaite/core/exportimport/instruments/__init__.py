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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

import inspect
import sys

from abaxis.vetscan import vs2  # noqa: 401
from abbott.m2000rt import m2000rt  # noqa: 401
from alere.pima import beads  # noqa: 401
from alere.pima import cd4  # noqa: 401
from beckmancoulter.access import model2  # noqa: 401
from bika.lims import api
from biodrop.ulite import ulite  # noqa: 401
from cobasintegra.model_400_plus import model_400_plus  # noqa: 401
from eltra.cs import cs2000  # noqa: 401
from facscalibur.calibur import model_e9750  # noqa: 401
from foss.fiastar import fiastar  # noqa: 401
from foss.winescan import auto  # noqa: 401
from foss.winescan import ft120  # noqa: 401
from generic import two_dimension  # noqa: 401
from genexpert import genexpert  # noqa: 401
from horiba.jobinyvon import icp  # noqa: 401
from lachat import quickchem  # noqa: 401
from lifetechnologies.qubit import qubit  # noqa: 401
from metler.toledo import dl55  # noqa: 401
from nuclisens import easyq  # noqa: 401
from panalytical.omnia import axios_xrf  # noqa: 401
from rigaku.supermini import wxrf  # noqa: 401
from rochecobas.taqman import model48  # noqa: 401
from rochecobas.taqman import model96  # noqa: 401
from scilvet.abc import plus  # noqa: 401
from sealanalytical.aq2 import aq2  # noqa: 401
from senaite.core.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter
from shimadzu.gcms import qp2010se  # noqa: 401
from shimadzu.gcms import tq8030  # noqa: 401
from shimadzu.icpe import multitype  # noqa: 401
from shimadzu.nexera import LC2040C  # noqa: 401
from shimadzu.nexera import LCMS8050  # noqa: 401
from sysmex.xs import i500  # noqa: 401
from sysmex.xs import i1000  # noqa: 401
from sysmex.xt import i1800  # noqa: 401
from sysmex.xt import i4000  # noqa: 401
from tescan.tima import tima  # noqa: 401
from thermoscientific.arena import xt20  # noqa: 401
from thermoscientific.gallery import Ts9861x  # noqa: 401
from thermoscientific.multiskan import go  # noqa: 401
from varian.vistapro import icp as icp_2  # noqa: 401
from zope.component import getAdapters
from zope.interface import Interface


class IInstrumentInterface(Interface):
    """Marker interface for instrument results import/export interfaces
    """


class IInstrumentExportInterface(IInstrumentInterface):
    """Marker interface for instrument results export interfaces
    """


class IInstrumentImportInterface(IInstrumentInterface):
    """Marker interface for instrument results import interfaces
    """


class IInstrumentAutoImportInterface(IInstrumentInterface):
    """Marker interface for instrument results import interfaces that are
    capable of auto importing results with only a file as the input
    """


# TODO Remove this once classic instrument interface migrated
__all__ = [
    "abaxis.vetscan.vs2",
    "abbott.m2000rt.m2000rt",
    "alere.pima.beads",
    "alere.pima.cd4",
    "beckmancoulter.access.model2",
    "biodrop.ulite.ulite",
    "eltra.cs.cs2000",
    "foss.fiastar.fiastar",
    "foss.winescan.auto",
    "foss.winescan.ft120",
    "generic.two_dimension",
    "genexpert.genexpert",
    "horiba.jobinyvon.icp",
    "lachat.quickchem",
    "lifetechnologies.qubit.qubit",
    "metler.toledo.dl55",
    "nuclisens.easyq",
    "panalytical.omnia.axios_xrf",
    "rigaku.supermini.wxrf",
    "rochecobas.taqman.model48",
    "rochecobas.taqman.model96",
    "scilvet.abc.plus",
    "sealanalytical.aq2.aq2",
    "shimadzu.gcms.qp2010se",
    "shimadzu.gcms.tq8030",
    "shimadzu.icpe.multitype",
    "shimadzu.nexera.LC2040C",
    "shimadzu.nexera.LCMS8050",
    "sysmex.xs.i1000",
    "sysmex.xs.i500",
    "sysmex.xt.i1800",
    "sysmex.xt.i4000",
    "tescan.tima.tima",
    "thermoscientific.arena.xt20",
    "thermoscientific.gallery.Ts9861x",
    "thermoscientific.multiskan.go",
    "varian.vistapro.icp",
    "cobasintegra.model_400_plus.model_400_plus",
    "facscalibur.calibur.model_e9750",
]

# Parsers are for auto-import. If empty, then auto-import won't wun for that
# interface
# TODO Remove this once classic instrument interface migrated
PARSERS = [
    ["abaxis.vetscan.vs2", "AbaxisVetScanCSVVS2Parser"],
    ["abbott.m2000rt.m2000rt", "Abbottm2000rtTSVParser"],
    ["alere.pima.beads", "AlerePimaSLKParser"],
    ["alere.pima.cd4", "AlerePimacd4SLKParser"],
    ["beckmancoulter.access.model2", "BeckmancoulterAccess2CSVParser"],
    ["biodrop.ulite.ulite", "BioDropCSVParser"],
    ["eltra.cs.cs2000", "EltraCS2000CSVParser"],
    ["foss.fiastar.fiastar", "FOSSFIAStarCSVParser"],
    ["foss.winescan.auto", "WinescanAutoCSVParser"],
    ["foss.winescan.ft120", "WinescanFT120CSVParser"],
    ["generic.two_dimension", "TwoDimensionCSVParser"],
    ["horiba.jobinyvon.icp", "HoribaJobinYvonCSVParser"],
    ["metler.toledo.dl55", "MetlerToledoDL55Parser"],
    ["rigaku.supermini.wxrf", "RigakuSuperminiWXRFCSVParser"],
    ["rochecobas.taqman.model48", "RocheCobasTaqmanParser"],
    ["rochecobas.taqman.model96", "RocheCobasTaqmanRSFParser"],
    ["thermoscientific.arena.xt20", "ThermoArena20XTRPRCSVParser"],
    ["thermoscientific.gallery.Ts9861x", "ThermoGallery9861xTSVParser"],
    ["panalytical.omnia.axios_xrf", "AxiosXrfCSVParser"],
    ["lachat.quickchem", "LaChatQuickCheckFIAParser"],
    ["lifetechnologies.qubit.qubit", "QuBitCSVParser"],
    ["sysmex.xs.i500", "SysmexXS500iCSVParser"],
    ["sysmex.xs.i1000", "SysmexXS500iCSVParser"],
    ["shimadzu.icpe.multitype", "ICPEMultitypeCSVParser"],
    ["shimadzu.gcms.qp2010se", "GCMSQP2010SECSVParser"],
    ["shimadzu.gcms.tq8030", "GCMSTQ8030GCMSMSCSVParser"],
    ["shimadzu.nexera.LC2040C", "TSVParser"],
    ["shimadzu.nexera.LCMS8050", "TSVParser"],
    ["sysmex.xt.i1800", "SysmexXT1800iParser"],
    ["sysmex.xt.i4000", "SysmexXT1800iParser"],
    ["scilvet.abc.plus", "AbaxisVetScanCSVVS2Parser"],
    ["sealanalytical.aq2.aq2", "SealAnalyticsAQ2CSVParser"],
    ["tescan.tima.tima", "TimaCSVParser"],
    ["thermoscientific.multiskan.go", "ThermoScientificMultiskanGOCSVParser"],
    ["nuclisens.easyq", "EasyQXMLParser"],
    ["genexpert.genexpert", "GeneXpertParser"],
    ["varian.vistapro.icp", "VistaPROICPParser"],
    ["cobasintegra.model_400_plus.model_400_plus", "CobasIntegra400plus2CSVParser"],
    ["facscalibur.calibur.model_e9750", "FacsCalibur2CSVParser"],
]


def get_instrument_interfaces():
    """Returns all available instrument interfaces as a list of tuples. Each
    tuple is (id_interface, adapter)
    """
    interfaces = list()
    portal = api.get_portal()
    for name, adapter in getAdapters((portal, ), IInstrumentInterface):
        # We need a unique identifier for this instrument interface
        id = "{}.{}".format(adapter.__module__, adapter.__class__.__name__)
        interfaces.append((id, adapter))

    # TODO Remove the following code once clasic instrument interfaces migrated
    # Now grab the information (the old way)
    curr_module = sys.modules[__name__]
    for name, obj in inspect.getmembers(curr_module):
        if hasattr(obj, '__name__'):
            obj_name = obj.__name__.replace(__name__, "")
            obj_name = obj_name and obj_name[1:] or ""
            if obj_name in __all__:
                interfaces.append((obj_name, obj))
    return interfaces


def is_import_interface(instrument_interface):
    """Returns whether the instrument interface passed in is for results import
    """
    if IInstrumentImportInterface.providedBy(instrument_interface):
        return True

    # TODO Remove this once classic instrument interface migrated
    if hasattr(instrument_interface, '__name__'):
        obj_name = instrument_interface.__name__.replace(__name__, "")
        if obj_name[1:] in __all__ and hasattr(instrument_interface, "Import"):
            return True
    return False


def is_export_interface(instrument_interface):
    """Returns whether the instrument interface passed in is for results export
    """
    if IInstrumentExportInterface.providedBy(instrument_interface):
        return True

    # TODO Remove this once classic instrument interface migrated
    if hasattr(instrument_interface, '__name__'):
        obj_name = instrument_interface.__name__.replace(__name__, "")
        if obj_name[1:] in __all__ and hasattr(instrument_interface, "Export"):
            return True
    return False


def get_instrument_import_interfaces():
    """Returns all available instrument results import interfaces as a list of
    tuples (id_interface, adapter)
    """
    return filter(lambda i: is_import_interface(i[1]),
                  get_instrument_interfaces())


def get_instrument_export_interfaces():
    """Returns all available instrument results expot interfaces as a list of
    tuples (id_interface, adapter)
    """
    return filter(lambda i: is_export_interface(i[1]),
                  get_instrument_interfaces())


def getExim(exim_id):
    """Returns the instrument interface for the exim_id passed in
    """
    interfaces = filter(lambda i: i[0] == exim_id, get_instrument_interfaces())
    return interfaces and interfaces[0][1] or None


def get_automatic_importer(exim_id, instrument, parser):
    """Returns the importer to be used
    """
    adapter = getExim(exim_id)

    if IInstrumentAutoImportInterface.providedBy(adapter):
        try:
            return adapter.get_automatic_importer(
                parser, instrument, exim_id=exim_id)
        except (NotImplementedError, AttributeError, TypeError, ValueError):
            # BBB: Fallback to default analysis results importer
            pass

    # return the default Analysis Results Importer
    return AnalysisResultsImporter(
        parser=parser,
        context=api.get_portal(),
        override=[False, False],
        instrument_uid=api.get_uid(instrument))


def get_automatic_parser(exim_id, infile):
    """Returns the parser to be used by default for the instrument id interface
    and results file passed in.
    """
    adapter = getExim(exim_id)
    if IInstrumentAutoImportInterface.providedBy(adapter):
        try:
            return adapter.get_automatic_parser(infile)
        except (NotImplementedError, AttributeError, TypeError, ValueError):
            # BBB: Fallback to default analysis results importer
            pass

    # TODO Remove this once classic instrument interface migrated
    parser_func = filter(lambda i: i[0] == exim_id, PARSERS)
    parser_func = parser_func and parser_func[0][1] or None
    if not parser_func or not hasattr(adapter, parser_func):
        return None
    parser_func = getattr(adapter, parser_func)
    return parser_func(infile)
