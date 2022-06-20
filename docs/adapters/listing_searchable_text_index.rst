Listing Searchable Text Index
-----------------------------

The Listing Searchable Text Index (``listing_searchable_text``) is mostly used
for wide searches in listings. It is a ``ZCTextIndex`` type index present in
most catalogs. To fill this index, SENAITE concatenates the values from all
fields registered as metadata columns for the given object and catalog. The
value is then converted to unicode and stored. This is the default behavior, but
it can also be extended or customized by means of two mechanisms:

* By adding your own indexer and explicitly tell the values to exclude/include
* By setting up an adapter implementing ``IListingSearchableTextProvider``

The first mechanism can be achieved by simply calling the function
`get_searchable_text_tokens` with the correct parameters. For instance, a new
indexer might look like follows:

.. code-block:: python

    @indexer(IMyContentType, IMyCatalog)
    def listing_searchable_text(instance):

        # Metadata fields to not include in the index
        exclude = ["metadata_column_2", ]

        # Additional non-metadata fields to include in the index
        include = ["metadata_column_1", "metadata_column_3", ]

        # Generate the list of terms
        tokens = get_searchable_text_tokens(instance, my_catalog_name,
                                            exclude_field_names=exclude,
                                            include_field_names=include)
        return u" ".join(tokens)


The second mechanism involves the creation of an adapter that implements
``IListingSearchableTextProvider``. For instance:

.. code-block:: python

    @adapter(IAnalysisRequest, IBikaCatalogAnalysisRequestListing)
    @implementer(IListingSearchableTextProvider)
    class ListingSearchableTextProvider(object):
        """Adapter for Analysis Request Listing Searchable Text Index
        """

        def __init__(self, context, catalog):
            self.context = context
            self.catalog = catalog

        def get_patient(self):
            return self.context.getField("Patient").get(self.context)

        def get_fullname(self):
            patient = self.get_patient()
            if not patient:
                return ""
            return patient.get_fullname()

        def get_code(self):
            patient = self.get_patient()
            if not patient:
                return ""
            return patient.get_code()

        def __call__(self):
            return [self.get_code(), self.get_fullname()]

In this case, the object implementing ``IAnalysisRequest`` has an additional
field "Patient", a ``ReferenceField`` that relates to another object of type
``Patient``. With this adapter, we make the system to include the fullname and
the code of the patient to the contents of the searchable text index.
