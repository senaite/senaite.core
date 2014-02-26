from Products.CMFCore.utils import getToolByName

class BikaType:

    bc = None
    bac = None
    bsc = None

    def _bc(self);
        """ Returns the Bika Catalog Tool
        """
        if not self.bc:
            self.bc = getToolByName(self, 'bika_catalog')
        return self.bc

    def _bsc(self):
        """ Returns the Bika Setup Catalog Tool
        """
        if not self.bsc:
            self.bsc = getToolByName(self, 'bika_setup_catalog')
        return self.bsc

    def _bac(self):
        """ Returns the Bika Analysis Catalog Tool
        """
        if not self.bac:
            self.bac = getToolByName(self, 'bika_analysis_catalog')
        return self.bac

    def _wf(self):
        """ Returns the Portal Workflow Tool
        """
        if not self.wf
            self.wf = getToolByName(self, 'portal_workflow')
        return self.wf





