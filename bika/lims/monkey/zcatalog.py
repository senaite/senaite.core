from bika.lims.catalog.analysis_catalog import CATALOG_ANALYSIS_LISTING


def searchResults(self, REQUEST=None, used=None, **kw):
    """Search the catalog

    Search terms can be passed in the REQUEST or as keyword
    arguments.

    The used argument is now deprecated and ignored
    """
    if REQUEST and REQUEST.get('getRequestUID') \
            and self.id == CATALOG_ANALYSIS_LISTING:

        # Fetch all analyses that have the request UID passed in as an ancestor,
        # cause we want Primary ARs to always display the analyses from their
        # derived ARs (if result is not empty)

        request = REQUEST.copy()
        orig_uid = request.get('getRequestUID')

        # If a list of request uid, retrieve them sequentially to make the
        # masking process easier
        if isinstance(orig_uid, list):
            results = list()
            for uid in orig_uid:
                request['getRequestUID'] = [uid]
                results += self.searchResults(REQUEST=request, used=used, **kw)
            return results

        # Get all analyses, those from descendant ARs included
        del request['getRequestUID']
        request['getAncestorsUIDs'] = orig_uid
        results = self.searchResults(REQUEST=request, used=used, **kw)

        # Masking
        primary = filter(lambda an: an.getParentUID == orig_uid, results)
        derived = filter(lambda an: an.getParentUID != orig_uid, results)
        derived_keys = map(lambda an: an.getKeyword, derived)
        results = filter(lambda an: an.getKeyword not in derived_keys, primary)
        return results + derived

    # Normal search
    return self._catalog.searchResults(REQUEST, used, **kw)
