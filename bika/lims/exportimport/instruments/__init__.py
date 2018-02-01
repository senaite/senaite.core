# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import sys
import inspect

# from generic import xml
from agilent.masshunter import quantitative, masshunter
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
from lifetechnologies.qubit import qubit
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

__all__ = ['abaxis.vetscan.vs2',
           'abbott.m2000rt.m2000rt',
           'agilent.masshunter.masshunter',
           'agilent.masshunter.quantitative',
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
           'lifetechnologies.qubit.qubit',
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
           ]

# Parsers are for auto-import. If empty, then auto-import won't wun for that
# interface
PARSERS = [
           ['abaxis.vetscan.vs2', 'AbaxisVetScanCSVVS2Parser'],
           ['abbott.m2000rt.m2000rt', 'Abbottm2000rtTSVParser'],
           ['agilent.masshunter.masshunter', 'AgilentMasshunterParser'],
           ['agilent.masshunter.quantitative', 'MasshunterQuantCSVParser'],
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
           ['rigaku.supermini.wxrf', 'RigakuSuperminiWXRFCSVParser'],
           ['rochecobas.taqman.model48', 'RocheCobasTaqmanRSFParser'],
           ['rochecobas.taqman.model96', 'RocheCobasTaqmanRSFParser'],
           ['thermoscientific.arena.xt20', 'ThermoArena20XTRPRCSVParser'],
           ['thermoscientific.gallery.Ts9861x', 'ThermoGallery9861xTSVParser'],
           ['panalytical.omnia.axios_xrf', 'AxiosXrfCSVParser'],
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
