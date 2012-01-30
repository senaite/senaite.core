3.0 dev
=======

2012-01-23
----------

#### Changes

 - Made Bika compatible with Plone 4.1
 - Sampler and Preserver roles, users and permissions
 - Sampling and Preservation workflows
 - Inactive and Cancellation Workflows
 - Pre-preserved Containers
 - Automatic versioning for some bika_setup types
 - Analyst and Instrument on Worksheet templates
 - XLSX setup data loader
 - Sample disposal date based on date sampled, not date received.
 - Internal ID Server by default
 - user defined calculations and interim fields
 - Dry Matter results option does not appear until enabled in Site Setup
 - Accreditation portlet disabled until enabled in Site Setup
 - BikaListingView
 - New icons
 - (mostly) usable at 800x600
 - Column display toggles
 - Future dated samples and ARs
 - Accreditation template: i18n in locales/manual.pot/accreditation_*
 - intermediate workflow state for analyses requiring attachments
 - Labmanager has Site Administrator role (not Manager)
 - 'Indeterminate' results
 - use portal_factory everywhere
 - working test suite
 - static resource directories
 - Merged BikaMembers types
 - CoordinateField/Widget
 - DurationField/Widget
 - CustomRecordsWidget

2.3.3 Bug fix release
=====================

#### Bugs fixed

 - Inclusion of BikaMembers 0.0.3. No changes to bika code, version bumped
   to facilitate release of new BikaMembers version.

2.3
===

#### Changes

 - Analysis categories introduced
 - Analysis service result restrictions - specification of possible results
 - Allow site and client specification of email and fax subject line content
 - Additional instrument/export formats:
   WinescanFT120, WinescanAuto, FIAStar and Bartelt's data-collector
 - Export worksheet analyses to instruments
 - PDF as a result output option
 - SMS result output option
 - Result publication options synchronized and signatures added to emails
 - Email batching of query results conforms to result mailing
 - IDServer batching of unique id request
 - Optmization of worksheet searching on selection criteria
 - Extract tab added with extract for analysis services or profiles
 - Batch update of analysis service prices
 - German translation module added
 - Added a light query form which excludes analysis category and service
 - Batch size setting in analysis request lists
 - BikaMembers replaces UpfrontContacts
 - ATSchemaEditor removed
 - Significant performance improvements

#### Bugs fixed

 - Resolve client action conflicts
 - Sampled date validation
 - Drymatter formatting on output corrected
 - Correct default none workflows
 - Review portlet optimization
 - Pricelist prints blank for analysis service with price not defined

2.2
===

#### Changes

 - Attachments permitted on analysis requests and analyses
 - Worksheet resequencing, and sort order for worksheet analysis selection
 - Worksheet deletion only available for open worksheets
 - Portlet to provide export of analysis services and analysis profiles
 - Requirement for unique analysis service names, analysis service keywords,
 - instrument import keywords and analysis profile keywords enforced.
 - Report headings and formats standardized accross different reports
 - AR import alternative layout provided with selection, including profiles
 - Progress bar introduced for long running processes

2.1.1
=====

#### Changes

 - Disposal Date for Samples and Retention Period per Sample Type added.
 - Various new search criteria added.
 - Standard Manufacturers introduced.
 - Labels for Standard Samples introduced.
 - "Print" and "Email" facilities introduced for lists of Standard Samples and Standard Stocks.
 - "Duplicate" facility for Analysis Services introduced.
 - Addresses added to top of emailed query results.
 - Labels for Samples and Analysis Requests changed.
 - Analysis Services can have multiple Methods.
 - Change log introduced for Methods.
 - Methods added to left navigation bar.
 - List of Methods included in pop-up for Analyses.
 - Documents may be uploaded for Methods.

2.1
===

#### Changes

 - Sample object and workflow introduced
 - Results specifications, lab and per client
 - Analysis profiles
 - Worksheet template engine
 - Interface to Bika Calendar
 - Import of analysisrequests from csv file
 -  Export of results to csv file
 - Print as publication option
 - Lab Departments, lab contacts, and department manager introduced
 - Quality Control calculations. Control, blank and duplicate analyses.
 - QC graphs, normal distribution, trends and duplicate variation
 - Various analysis calculations allowed. Described by Calculation Type
 - Dependant Calcs introduced. Where an analysis result is calculated from
 -  other analyses: e.g. AnalysisX = AnalysisY - Analysis Z
 - Dry matter result reporting. Results are reported on sample as received,
 -  and also as dry matter result on dried sample
 - Re-publication, Pre publication of individual results and per Client
 - Many reports including Turn around, analyses repeated and out of spec

1.2.1
=====

#### Bugs fixed

 - Removed invoice line item descriptions from core code to allow skin
   integration
 - Create dummy titration values for analyses imported from instrument
 - More language translations

1.2.0
=====

#### Changes

 - Statements renamed to Invoices
 - Jobcards renamed to Worksheets
 - New identification fields added to analysis request
 - Client Reference, Sample Type and Sample Point
 - Welcome page introduced
 - Late analyses list linked from late analyses portlet
 - Icon changes
 - Accreditation body logo and details added to laboratory info
 - Accreditation logo, disclaimers added throughout web site
 - Laboratory confidence level value data driven from laboratory info
 - Analyses methods provided as pop-up where analyses are listed
 - Titration factors and titration volumes added to analyses and worksheets
 - Measure of uncertainties introduced per analysis and intercept
 - Two new specialist roles created - verifier and publisher
 - Sample test data load script - load_sample_data.py
 - Implement generic instrument data import tool
 - Login portlet added
 - Modifications required to support interlab
   Permit analysis parent (sample) to be in 'released' state.
   Reference SampleID on AnalysisRequest-

#### Bugs fixed

 - 1566324: Logged in page redirected to welcome page.
 - 1573299: LiveSearch - Added permissions to InvoiceLineItem.
 - 1573083: Status Drop Down - Invoicing
 - 1551957: Contacts not visible to other contacts. Correct local owner role
 - 1566334: position of 'add new ar' button changed to conform to other forms
 - 1532008: query results sort order most recent first
 - 1532770: Order default listing correction
 - 1558458: Member discount data driven in messages on AR forms
 - 1538354: SubTotal and VAT calculation on edit AR
 - 1532796: AR edit - allow change of contact

1.1.3
=====

 This is a bug fix release. Migration from older versions has also
 been improved greatly.

 Please note that AnalysisRequest now has a custom mutator that
 expects the title of the Cultivar, not the UID. This will impact
 anybode that customised the *analysisrequed_add.cpy* controller
 script and the *validate_analysisrequest_add_form.vpy* validation
 script.

#### Bugs fixed

 - 1423182: IndexError on surfing to LIMS pages without being logged on
 - 1423238: Orders - Dispatch date
 - 1429992: AR edit tab - Cultivar uneditable
 - 1429996: Cultivar names to allow numbers
 - 1429999: Late analysis alert - 'More...' URL
 - 1430002: Sample due alerts - 'More...' URL
 - 1433787: Security - Clients
 - 1434100: Search - Index & Attribute errors
 - 1418473: Updated start-id-server.bat for Win2K & Win XP

1.1.2
=====

#### Features added

 - 1423205: Show logs to labmanager set-up
 - 1291750: Added default ID prefixes for Order and Statement

#### Bugs fixed

 - 1424589: Late analysis alert to be calulated on date received

1.1.1
=====

#### Changes

 - Updated portlets with Plone 2.1 style definition list markup

#### Bugs fixed:

 - 1423179: Clients must not see JobCard links on Analysis Requests
 - 1423182: IndexError on surfing to LIMS pages without being logged on
 - 1423188: Site map - Clients should not have access to ...
 - 1423191: Link rot - 'logged in' page
 - 1423193: Groups folder should not be shown
 - 1423194: No 'More...' if there are less than 5
 - 1423204: AR view - Missing tabs and status drop down
 - 1423209: Schema Editor - Drop Down List Issue (Select)
 - 1423234: Late Analysis alert shows for anonymous visitors
 - 1423363: Report Analysis Totals
 - 1423386: Email publication error

1.1.0
=====

#### Changes
 - Made Bika compatibable with Plone 2.1
 - Added Spanish translation contributed by Luis Espinoza
 - Added Italian translation contributed by Pierpaolo Baldan
 - Added Dutch translation contributed by Joris Goudriaan
 - Added Portugese translation contributed by Nuno R. Pinhão
 - The schemas of Client, Contact, AnalysisRequest and Order can be
   edited in the through-the-web schema editor, ATSchemaEditorNG.
 - The maximum time allowed for the publication of results can now be
   set per analysis service. The portlet
   'skins/bika/portlet_late_analysis.pt' has been added to alert lab
   users when analyses are late.
 - Analyses on an AnalysisRequest have a reference to a Jobcard,
   rendered as a hyperlink on the AnalysisRequest view.
 - A bug has been fixed where 'not_requested' analyses were checked
   on the AnalysisRequest edit form.
 - Enabled 'changed_state' folder button globally and disabled on
   AnalysisRequest and Jobcard.

1.0.1
=====

#### Changes

 - Updated 'skins/bika/date_components_support.py' with latest
   version of script in Plone 2.0.5
 - Modified access to transitions in workflow scripts, normal
   attribute access seems to guarded since Zope 2.7.5.
 - Added CHANGES.txt and README.txt
 - Added windows batch script for ID server
   (scripts/start-id-server.bat)

