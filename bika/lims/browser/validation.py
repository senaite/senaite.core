from Products.Archetypes.browser.validation import InlineValidationView as _IVV
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
import json


SKIP_VALIDATION_FIELDTYPES = ('image', 'file', 'datetime', 'reference')

class InlineValidationView(_IVV):

    def __call__(self, uid, fname, value):
        '''Validate a given field. Return any error messages.
        '''
        res = {'errmsg': ''}

        rc = getToolByName(aq_inner(self.context), 'reference_catalog')
        instance = rc.lookupObject(uid)
        # make sure this works for portal_factory items
        if instance is None:
            instance = self.context

        field = instance.getField(fname)
        if field and field.type not in SKIP_VALIDATION_FIELDTYPES:
            return super(InlineValidationView, self).__call__(uid, fname, value)

        self.request.response.setHeader('Content-Type', 'application/json')
        return json.dumps(res)
