# -*- coding: utf-8 -*-

from senaite.core.browser.listing.actions import BaseActionView


class ActionView(BaseActionView):
    """Action View for Analyses
    """

    def recalculate(self):
        """Recalculate the results
        """
        title = self.context.Title()
        calc = self.context.getCalculation()
        if not calc:
            return self.message("No calculation found", False, title=title)
        success = self.context.calculateResult(override=True)
        if not success:
            return self.message(
                "Failed to recalculate result", False, title=title)

        return self.message("Result recalucated", True, title=title)
