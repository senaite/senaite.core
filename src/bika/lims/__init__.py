from senaite.core import *  # noqa
# Inject modules into the textindexng namespace so old imports still work. This
# is necessary for old database instances loading indexes from here.
import sys
for name, module in sys.modules.items():
    if name.startswith('senaite.core'):
        name = name.replace('senaite.core', 'bika.lims', 1)
        sys.modules[name] = module
