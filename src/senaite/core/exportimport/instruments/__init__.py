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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

import sys
import inspect

# from generic import xml
from abbott.m2000rt import m2000rt
from foss.fiastar import fiastar
from foss.winescan import auto
from foss.winescan import ft120
from generic import two_dimension
from thermoscientific.gallery import Ts9861x
from thermoscientific.arena import xt20
from thermoscientific.multiskan import go
from panalytical.omnia import axios_xrf
from alere.pima import beads, cd4
from lachat import quickchem
from lifetechnologies.qubit import qubit
from metler.toledo import dl55
from biodrop.ulite import ulite
from tescan.tima import tima
from sysmex.xs import i500, i1000
from sysmex.xt import i1800, i4000
from beckmancoulter.access import model2
from rochecobas.taqman import model48
from rochecobas.taqman import model96
from sealanalytical.aq2 import aq2
from shimadzu.gcms import qp2010se, tq8030
from shimadzu.icpe import multitype
from shimadzu.nexera import LC2040C, LCMS8050
from horiba.jobinyvon import icp
from abaxis.vetscan import vs2
from scilvet.abc import plus
from eltra.cs import cs2000
from rigaku.supermini import wxrf
from myself import myinstrument
from nuclisens import easyq
from genexpert import genexpert
from varian.vistapro import icp
from cobasintegra.model_400_plus import model_400_plus
from facscalibur.calibur import model_e9750

from bika.lims import api
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
__all__ = ['abaxis.vetscan.vs2',
           'abbott.m2000rt.m2000rt',
           'alere.pima.beads',
           'alere.pima.cd4',
           'beckmancoulter.access.model2',
           'biodrop.ulite.ulite',
           'eltra.cs.cs2000',
           'foss.fiastar.fiastar',
           'foss.winescan.auto',
           'foss.winescan.ft120',
           'generic.two_dimension',
           # 'generic.xml',
           'genexpert.genexpert',
           'horiba.jobinyvon.icp',
           'lachat.quickchem',
           'lifetechnologies.qubit.qubit',
           'metler.toledo.dl55',
           'myself.myinstrument',
           'nuclisens.easyq',
           'panalytical.omnia.axios_xrf',
           'rigaku.supermini.wxrf',
           'rochecobas.taqman.model48',
           'rochecobas.taqman.model96',
           'scilvet.abc.plus',
           'sealanalytical.aq2.aq2',
           'shimadzu.gcms.qp2010se',
           'shimadzu.gcms.tq8030',
           'shimadzu.icpe.multitype',
           'shimadzu.nexera.LC2040C',
           'shimadzu.nexera.LCMS8050',
           'sysmex.xs.i1000',
           'sysmex.xs.i500',
           'sysmex.xt.i1800',
           'sysmex.xt.i4000',
           'tescan.tima.tima',
           'thermoscientific.arena.xt20',
           'thermoscientific.gallery.Ts9861x',
           'thermoscientific.multiskan.go',
           'varian.vistapro.icp',
           'cobasintegra.model_400_plus.model_400_plus',
           'facscalibur.calibur.model_e9750'
           ]

# Parsers are for auto-import. If empty, then auto-import won't wun for that
# interface
# TODO Remove this once classic instrument interface migrated
PARSERS = [
           ['abaxis.vetscan.vs2', 'AbaxisVetScanCSVVS2Parser'],
           ['abbott.m2000rt.m2000rt', 'Abbottm2000rtTSVParser'],
           ['alere.pima.beads', 'AlerePimaSLKParser'],
           ['alere.pima.cd4', 'AlerePimacd4SLKParser'],
           ['beckmancoulter.access.model2', 'BeckmancoulterAccess2CSVParser'],
           ['biodrop.ulite.ulite', 'BioDropCSVParser'],
           ['eltra.cs.cs2000', 'EltraCS2000CSVParser'],
           ['foss.fiastar.fiastar', 'FOSSFIAStarCSVParser'],
           ['foss.winescan.auto', 'WinescanAutoCSVParser'],
           ['foss.winescan.ft120', 'WinescanFT120CSVParser'],
           ['generic.two_dimension', 'TwoDimensionCSVParser'],
           # ['generic.xml', ''],
           ['horiba.jobinyvon.icp', 'HoribaJobinYvonCSVParser'],
           ['metler.toledo.dl55', 'MetlerToledoDL55Parser'],
           ['rigaku.supermini.wxrf', 'RigakuSuperminiWXRFCSVParser'],
           ['rochecobas.taqman.model48', 'RocheCobasTaqmanParser'],
           ['rochecobas.taqman.model96', 'RocheCobasTaqmanRSFParser'],
           ['thermoscientific.arena.xt20', 'ThermoArena20XTRPRCSVParser'],
           ['thermoscientific.gallery.Ts9861x', 'ThermoGallery9861xTSVParser'],
           ['panalytical.omnia.axios_xrf', 'AxiosXrfCSVParser'],
           ['lachat.quickchem', 'LaChatQuickCheckFIAParser'],
           ['lifetechnologies.qubit.qubit', 'QuBitCSVParser'],
           ['sysmex.xs.i500', 'SysmexXS500iCSVParser'],
           ['sysmex.xs.i1000', 'SysmexXS500iCSVParser'],
           ['shimadzu.icpe.multitype', 'ICPEMultitypeCSVParser'],
           ['shimadzu.gcms.qp2010se', 'GCMSQP2010SECSVParser'],
           ['shimadzu.gcms.tq8030', 'GCMSTQ8030GCMSMSCSVParser'],
           ['shimadzu.nexera.LC2040C', 'TSVParser'],
           ['shimadzu.nexera.LCMS8050', 'TSVParser'],
           ['sysmex.xt.i1800', 'SysmexXT1800iParser'],
           ['sysmex.xt.i4000', 'SysmexXT1800iParser'],
           ['scilvet.abc.plus', 'AbaxisVetScanCSVVS2Parser'],
           ['sealanalytical.aq2.aq2', 'SealAnalyticsAQ2CSVParser'],
           ['tescan.tima.tima', 'TimaCSVParser'],
           ['thermoscientific.multiskan.go', 'ThermoScientificMultiskanGOCSVParser'],
           ['myself.myinstrument', 'MyInstrumentCSVParser'],
           ['nuclisens.easyq', 'EasyQXMLParser'],
           ['genexpert.genexpert', 'GeneXpertParser'],
           ['varian.vistapro.icp', 'VistaPROICPParser'],
           ['cobasintegra.model_400_plus.model_400_plus','CobasIntegra400plus2CSVParser'],
           ['facscalibur.calibur.model_e9750', 'FacsCalibur2CSVParser'],
           ]


def get_instrument_interfaces():
    """Returns all available instrument interfaces as a list of tuples. Each
    tuple is (id_interface, adapter)
    """
    interfaces = list()
    for name, adapter in getAdapters((api.get_portal(),), IInstrumentInterface):
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
    interfaces = filter(lambda i: i[0]==exim_id, get_instrument_interfaces())
    return interfaces and interfaces[0][1] or None


def get_automatic_parser(exim_id, infile):
    """Returns the parser to be used by default for the instrument id interface
    and results file passed in.
    """
    adapter = getExim(exim_id)
    if IInstrumentAutoImportInterface.providedBy(adapter):
        return adapter.get_automatic_parser(infile)

    # TODO Remove this once classic instrument interface migrated
    parser_func = filter(lambda i: i[0] == exim_id, PARSERS)
    parser_func = parser_func and parser_func[0][1] or None
    if not parser_func or not hasattr(adapter, parser_func):
        return None
    parser_func = getattr(adapter, parser_func)
    return parser_func(infile)
  
