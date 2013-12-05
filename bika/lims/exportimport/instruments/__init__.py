import sys
import inspect

from generic import xml
from agilent import masshunter_quant
from fiastar import fiastar
from foss import winescan_auto
from foss import winescan_ft120

__all__ = ['generic.xml',
           'fiastar.fiastar',
           'agilent.masshunter_quant',
           'foss.winescan_auto',
           'foss.winescan_ft120']


def getExim(exim_id):
    currmodule = sys.modules[__name__]
    members = [obj for name, obj in inspect.getmembers(currmodule) \
               if hasattr(obj, '__name__') \
               and obj.__name__.endswith(exim_id)]

    return members[0]
