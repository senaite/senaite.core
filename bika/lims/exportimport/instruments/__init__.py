import sys
import inspect

from generic import xml
from agilent.masshunter import quantitative
from foss.fiastar import fiastar
from foss.winescan import auto
from foss.winescan import ft120
from thermoscientific.gallery import Ts9861x
from thermoscientific.arena import xt20
from panalytical.omnia import axios_xrf
from alere.pima import beads, cd4
from lifetechnologies.qubit import qubit
from biodrop.ulite import ulite
from tescan.tima import tima
from sysmex.xs import i500

__all__ = ['generic.xml',
           'agilent.masshunter.quantitative',
           'foss.fiastar.fiastar',
           'foss.winescan.auto',
           'foss.winescan.ft120',
           'thermoscientific.gallery.Ts9861x',
           'thermoscientific.arena.xt20',
           'panalytical.omnia.axios_xrf',
           'alere.pima.beads',
           'alere.pima.cd4',
           'lifetechnologies.qubit.qubit',
           'biodrop.ulite.ulite',
           'tescan.tima.tima',
           'sysmex.xs.i500'
           ]


def getExim(exim_id):
    currmodule = sys.modules[__name__]
    members = [obj for name, obj in inspect.getmembers(currmodule) \
               if hasattr(obj, '__name__') \
               and obj.__name__.endswith(exim_id)]

    return members[0]
