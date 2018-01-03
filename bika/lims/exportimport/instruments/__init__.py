# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import sys
import inspect

# from generic import xml
from agilent.masshunter import quantitative
from abbott.m2000rt import m2000rt
from foss.fiastar import fiastar
from foss.winescan import auto
from foss.winescan import ft120
from thermoscientific.gallery import Ts9861x
from thermoscientific.arena import xt20
from thermoscientific.multiskan import go
from panalytical.omnia import axios_xrf
from alere.pima import beads, cd4
from lifetechnologies.qubit import qubit
from biodrop.ulite import ulite
from tescan.tima import tima
from sysmex.xs import i500, i1000
from beckmancoulter.access import model2
from rochecobas.taqman import model48
from rochecobas.taqman import model96
from sealanalytical.aq2 import aq2
from horiba.jobinyvon import icp
from abaxis.vetscan import vs2
from scilvet.abc import plus
from eltra.cs import cs2000
from rigaku.supermini import wxrf
from myself import myinstrument
from nuclisens import easyq
from genexpert import genexpert

__all__ = ['abaxis.vetscan.vs2',
           'abbott.m2000rt.m2000rt',
           'agilent.masshunter.quantitative',
           'alere.pima.beads',
           'alere.pima.cd4',
           'beckmancoulter.access.model2',
           'biodrop.ulite.ulite',
           'eltra.cs.cs2000',
           'foss.fiastar.fiastar',
           'foss.winescan.auto',
           'foss.winescan.ft120',
           # 'generic.xml',
           'horiba.jobinyvon.icp',
           'rigaku.supermini.wxrf',
           'rochecobas.taqman.model48',
           'rochecobas.taqman.model96',
           'thermoscientific.arena.xt20',
           'thermoscientific.gallery.Ts9861x',
           'panalytical.omnia.axios_xrf',
           'lifetechnologies.qubit.qubit',
           'sysmex.xs.i500',
           'sysmex.xs.i1000',
           'scilvet.abc.plus',
           'sealanalytical.aq2.aq2',
           'tescan.tima.tima',
           'thermoscientific.multiskan.go',
           'myself.myinstrument',
           'nuclisens.easyq',
           'genexpert.genexpert'
           ]

# Parsers are for auto-import. If empty, then auto-import won't wun for that
# interface
PARSERS = [
           ['abaxis.vetscan.vs2', 'AbaxisVetScanCSVVS2Parser'],
           ['abbott.m2000rt.m2000rt', 'Abbottm2000rtTSVParser'],
           ['agilent.masshunter.quantitative', 'MasshunterQuantCSVParser'],
           ['alere.pima.beads', 'AlerePimaSLKParser'],
           ['alere.pima.cd4', 'AlerePimacd4SLKParser'],
           ['beckmancoulter.access.model2', 'BeckmancoulterAccess2CSVParser'],
           ['biodrop.ulite.ulite', 'BioDropCSVParser'],
           ['eltra.cs.cs2000', 'EltraCS2000CSVParser'],
           ['foss.fiastar.fiastar', 'FOSSFIAStarCSVParser'],
           ['foss.winescan.auto', 'WinescanAutoCSVParser'],
           ['foss.winescan.ft120', 'WinescanFT120CSVParser'],
           # ['generic.xml', ''],
           ['horiba.jobinyvon.icp', 'HoribaJobinYvonCSVParser'],
           ['rigaku.supermini.wxrf', 'RigakuSuperminiWXRFCSVParser'],
           ['rochecobas.taqman.model48', 'RocheCobasTaqmanRSFParser'],
           ['rochecobas.taqman.model96', 'RocheCobasTaqmanRSFParser'],
           ['thermoscientific.arena.xt20', 'ThermoArena20XTRPRCSVParser'],
           ['thermoscientific.gallery.Ts9861x', 'ThermoGallery9861xTSVParser'],
           ['panalytical.omnia.axios_xrf', 'AxiosXrfCSVParser'],
           ['lifetechnologies.qubit.qubit', 'QuBitCSVParser'],
           ['sysmex.xs.i500', 'SysmexXS500iCSVParser'],
           ['sysmex.xs.i1000', 'SysmexXS500iCSVParser'],
           ['scilvet.abc.plus', 'AbaxisVetScanCSVVS2Parser'],
           ['sealanalytical.aq2.aq2', 'SealAnalyticsAQ2CSVParser'],
           ['tescan.tima.tima', 'TimaCSVParser'],
           ['thermoscientific.multiskan.go', 'ThermoScientificMultiskanGOCSVParser'],
           ['myself.myinstrument', 'MyInstrumentCSVParser'],
           ['nuclisens.easyq', 'EasyQXMLParser'],
           ['genexpert.genexpert', 'GeneXpertParser'],
           ]


def getExim(exim_id):
    currmodule = sys.modules[__name__]
    members = [obj for name, obj in inspect.getmembers(currmodule)
               if hasattr(obj, '__name__')
               and obj.__name__.endswith(exim_id)]
    return members[0] if len(members) > 0 else None


def getParserName(exim_id):
    for pair in PARSERS:
        if pair[0] == exim_id:
            return pair[1]
    return None
