def contentmenu_factories_available(self):
    """These types will have their Add New... factories dropdown menu removed.
    """
    if hasattr(self._addContext(), 'portal_type') \
    and self._addContext().portal_type in [
        'ARImport',
        'Batch',
        'Client',
        'AnalysisRequest',
        'Worksheet',
        'Sample',
        'AnalysisCategory',
        'AnalysisProfile',
        'ARTemplate',
        'AnalysisService',
        'AnalysisSpec',
        'Attachment',
        'Calculation',
        'Instrument',
        'LabContact',
        'Laboratory',
        'Method',
        'Department',
        'ReferenceDefinition',
        'ReportFolder',
        'SampleType',
        'SamplePoint',
        'StorageLocation',
        'WorksheetTemplate',
        'LabProduct',
        'ReferenceSample',
        'Preservation'
    ]:
        return False
    else:
        itemsToAdd = self._itemsToAdd()
        showConstrainOptions = self._showConstrainOptions()
        if self._addingToParent() and not self.context_state.is_default_page():
            return False
        return (len(itemsToAdd) > 0 or showConstrainOptions)
