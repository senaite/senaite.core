# -*- coding: utf-8 -*-

from senaite.core.browser.listing.actions import BaseActionView


class ActionView(BaseActionView):
    """Action View for Analyses
    """

    def recalculate(self):
        """Recalculate the results
        """
        calc = self.context.getCalculation()
        if not calc:
            return self.message("No calculation found", False)
        success = self.context.calculateResult(override=True)
        if not success:
            return self.message("Failed to recalculate result", False)

        return self.message("Result recalucated", True)
