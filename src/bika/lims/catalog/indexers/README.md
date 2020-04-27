# Indexes

## Generic indexes

- `is_active`: Whether the object is neither cancelled nor invalid
- `listing_searchable_text`: Wildcard searches in listings
- `sortable_title`: Default case-insensitive sorting

## Catalog-specific

### bika_setup_catalog

- `category_uid`: Searches by analysis category
- `department_title`: Sorting of Analyses Categories listing
- `instrument_title`: Sorting of Worksheet Templates listing by Instrument
- `instrumenttype_title`: Sorting of Instruments listing
- `method_available_uid`: Filtering of services in Worksheet's Add Analyses
View for when the Worksheet Template being used has a Method assigned
- `point_of_capture`: To split analyses services listing in Add Sample Form
- `price`: Sorting of Lab Products listing
- `price_total`: Sorting of Lab Products listing
- `sampletype_title`: Used for sorting of listings (Sample Points,
Specifications and Templates)
- `sample_type_uid`: Used in Add Sample form to filter Sample Points,
Specifications and Templates when a Sample Type is selected.

## Content-specific

### AnalysisCategory

- `sortable_title`: Case-insensitive + sortkey for default sorting

### AnalysisRequest

- `assigned_state`: Whether all analyses have been assigned or not
- `getAncestorsUIDs`: Partitions' analyses masking in searches
- `is_received`: Whether the Analysis Request has been received
- `listing_searchable_text`: Wildcard searches, including partitions

### BaseAnalysis

- `sortable_title`: Case-insensitive + sortkey for default sorting

### IContact (LabContact, Contact)

- `sortable_title`: Case-insensitive contact's fullname for default sorting

### IOrganisation (Supplier, Manufacturer, Client, etc.)

- `title`: Organisation-like objects don't use the default attribute `title`
provided by AT. Rather, they keep this attribute empty and the schema field
`Name` is used (`Title` acts as a shortcut to `getName`). We need to handle this
behavior to simulate default behavior of `title` index
