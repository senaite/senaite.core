# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from bika.lims.browser import BrowserView
from time import strptime
import json
from bika.lims.utils import get_date_format


class AJAXValidateDate(BrowserView):
    """
    Validates entered date/datetime string according to formats defined in Bika Setup.
    """
    def __call__(self):
        if 'date_format' in self.request.keys() and 'string_value' in self.request.keys():
            f = str(self.request.get('date_format', None))
            v = str(self.request.get('string_value', None))
            fmtstr = get_date_format(f)
            try:
                strptime(v, fmtstr)
                ret = {'success': True}
            except ValueError:
                ret = {'error': True,
                       'message': "Please enter a valid date in '{}' format".format(fmtstr)}

            return json.dumps(ret)
