import sys
import inspect

from generic import xml
from agilent.masshunter import quantitative
from foss.fiastar import fiastar
from foss.winescan import auto
from foss.winescan import ft120
from thermoscientific.gallery import Ts9861x
from panalytical.omnia import axios_xrf

__all__ = ['generic.xml',
           'agilent.masshunter.quantitative',
           'foss.fiastar.fiastar',
           'foss.winescan.auto',
           'foss.winescan.ft120',
           'thermoscientific.gallery.Ts9861x',
           'panalytical.omnia.axios_xrf']


def getExim(exim_id):
    currmodule = sys.modules[__name__]
    members = [obj for name, obj in inspect.getmembers(currmodule) \
               if hasattr(obj, '__name__') \
               and obj.__name__.endswith(exim_id)]

    return members[0]
