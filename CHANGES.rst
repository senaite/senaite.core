Changelog
=========

1.3.5 (unreleased)
------------------

**Fixed**

- #1673 Fix Samples not sorted in natural order when Worksheet Template is used
- #1656 Fix Maximum length of Choices subfield (interim) is set to 40
- #1651 Fix Error when invalidating a sample with contained retests
- #1633 Fix report section displays date pickers in Chinese
- #1639 Fix very rare AttributeError on Worksheet Template assignment
- #1629 Fix Published results tab is not displayed to Client contacts
- #1628 Fix instrument import for analyses with result options
- #1625 Fix assignment of analyses via worksheet template when Worksheet is full
- #1617 Fix writing methods on read when reindexing services


1.3.4 (2020-08-11)
------------------

**Added**

- #1612 Add Client sample ID to worksheet template printview
- #1609 Support result options entry for interim values
- #1598 Added "modified" index in Sample's (AnalysisRequest) catalog
- #1596 Allow to hide actions menu by using new marker interface IHideActionsMenu
- #1588 Dynamic Analysis Specs: Lookup dynamic spec only when the specification is set
- #1586 Allow to configure the variables for IDServer with an Adapter
- #1584 Date (yymmdd) support in IDs generation
- #1582 Allow to retest analyses without the need of retraction
- #1573 Append the type name of the current record in breadcrumbs (Client)
- #1573 Add link "My Organization" under top-right user selection list

**Changed**

- #1607 Allow to set instruments from method edit view
- #1588 Dynamic Analysis Specs: Hide compliance viewlets
- #1579 Remove classic mode in folderitems
- #1577 Do not force available workflow transitions in batches listing
- #1573 Do not display top-level "Clients" folder to non-lab users

**Fixed**

- #1606 Fix Traceback on Dynamic Analysis Specs Edit
- #1605 Fix Retests are not displayed in Worksheet's print view
- #1604 Fix Analyses from partitions do not show up when using Worksheet Template
- #1602 Fix Report "Analysis per Service" is always creating the same PDF file
- #1601 Fix Wrong url in client's sample templates listing
- #1594 Fix System does not validate values from Results Options to be different
- #1596 Fix Reports page shows the Display/State/Add menu
- #1595 Fix Wrong url in client's analyses profiles listing
- #1593 Fix Out-of-range alert icon is shown to users w/o "View Results" privileges
- #1592 Fix Publisher user cannot publish samples
- #1591 Fix User can assign a contact from another client while creating a Sample
- #1585 Fix wrong label and description for `ShowPartitions` setting from setup
- #1583 Fix traceback in services listing in ARTemplate view
- #1581 Fix Some values are not properly rendered in services listing
- #1580 Fix Analysts are not displayed once created in worksheets listing
- #1575 Fix Uncertainties are displayed although result is below Detection Limit
- #1572 Fix Unable to get the previous status when duplicated in review history
- #1570 Fix Date time picker does not translates well to current language
- #1571 Fix Cannot reject Sample when contact has no email set
- #1568 Fix Traceback when rendering sticker `Code_39_2ix1i`
- #1567 Fix missing CCContact after adding a new Sample
- #1566 Fix column sorting in Worksheet listing
- #1563 Fix Client Contacts can create Samples without Contact


1.3.3.1 (2020-03-04)
--------------------

**Fixed**

- #1560 Fix missing Add Dynamic Analysis Specifications Button for Lab Managers


1.3.3 (2020-03-03)
------------------

**Added**

- #1553 Allow to modify the email template for rejection notification
- #1549 Added registry profile for jQuery UI settings
- #1544 Progress indicator for Batch listing
- #1536 Integrated Setup and Profiles from senaite.lims
- #1534 Integrate browser resources from senaite.lims
- #1529 Moved contentmenu provider into core
- #1523 Moved Installation Screens into core
- #1520 JavaScripts/CSS Integration and Cleanup
- #1517 Integrate senaite.core.spotlight
- #1516 Consider analyses with result options or string in duplicate valid range
- #1515 Moved Setup View into Core
- #1506 Specification non-compliant viewlet in Sample
- #1506 Sample results ranges out-of-date viewlet in Sample
- #1506 Warn icon in analyses when range is not compliant with Specification
- #1492 Dynamic Analysis Specifications
- #1507 Support for semi-colon character separator in CCEmails field
- #1499 Moved navigation portlet into core 
- #1498 Moved all viewlets from senaite.lims to senaite.core
- #1505 Display partition link in analyses listing
- #1491 Enable Audit-logging for Dexterity Contents
- #1489 Support Multiple Catalogs for Dexterity Contents
- #1481 Filter Templates field when Sample Type is selected in Sample Add form
- #1483 Added Accredited symbol in Analyses listings
- #1466 Support for "readonly" and "hidden" visibility modes in ReferenceWidget

**Changed**

- #1555 List all multi-reports for samples, where the current sample is contained
- #1543 Sort navigation child-nodes alphabetically
- #1539 Avoid unnecessary Price recalculations in Sample Add Form
- #1532 Updated jQuery Barcode to version 2.2.0
- #1513 Better Ajax Loader for Sample Add Form
- #1508 Do not try to render InstrumentQCFailuresViewlet to non-lab personnel
- #1495 Better Remarks handling and display
- #1502 Improved DateTime Widget
- #1490 Support Dexterity Behavior Fields in API
- #1488 Support Dexterity Contents in Catalog Indexers
- #1486 Clean-up of indexes and metadata from `setup_catalog`

**Removed**

- #1531 Remove sampling rounds from core
- #1551 Removed dependency to plone.app.iterate
- #1530 Removed ARImport
- #1530 Removed stale type registrations
- #1541 Remove add/edit options of ReferenceWidget
- #1535 Remove `zcatalog` monkey (and `getRequestUID` index)
- #1518 Removed stale indexes from `analysis_catalog`
- #1516 Removed getResultsRange metadata from analysis_catalog
- #1487 Dexterity Compatible Catalog Base Class
- #1482 Remove `senaite.instruments` dependency for instrument import form
- #1478 Remove AcquireFieldDefaults (was used for CCEmails field only)

**Fixed**

- #1556 Fix TypeError when retracting analyses with ExtendedField
- #1552 Rejection on registration is neither generating rejection pdf nor email
- #1550 Fix Uncaught TypeError in combogrid
- #1542 Fix sporadical errors when contacts do not have a valid email address
- #1540 Fix flushing CCEmail fields in Sample Add Form
- #1533 Fix traceback from log when rendering stickers preview
- #1525 Fix error when creating partitions with analyst user
- #1522 Fix sporadical timeout issue when adding new samples/remarks
- #1506 Changes via manage results don't get applied to partitions
- #1506 Fix recursion error when getting dependencies through Calculation
- #1506 setter from ARAnalysisField does no longer return values
- #1512 QC Analyses listing appears empty in Sample view
- #1510 Error when viewing a Sample w/o Batch as client contact
- #1511 Links to partitions for Internal Use are displayed in partitions viewlet
- #1505 Manage Analyses Form re-applies partitioned Analyses back to the Root
- #1503 Avoid duplicate CSS IDs in multi-column Add form
- #1501 Fix Attribute Error in Reference Sample Popup
- #1493 jsonapi.read omits `include_methods` when a single parameter is used
- #1494 Fix KeyError in Sample Type Listing
- #1477 Sample edit form - some selection widgets empty
- #1478 Clients default CC E-Mails missing in Add Sample
- #1479 Fixed too many redirects error: Labclerks viewing verified worksheets
- #1480 Worksheet removal results in 404
- #1475 User with "Analyst" role cannot submit analyses from worksheet
- #1474 Adding Control Reference to Worksheet causes print fail
- #1473 Hidden settings of analysis services lost on Sample creation
- #1472 Secondary samples - removal of analysis profile not possible
- #1469 Fix Site Properties Generic Setup Export Step
- #1467 Cannot override behavior of Batch folder when using `before_render`


1.3.2 (2019-10-30)
------------------

**Added**

- #1463 Structure Export/Import Handlers for Generic Setup
- #1462 Allow to extend the behavior of fields from AddSample view with adapters
- #1455 Added support for adapters in guard handler
- #1436 Setting in setup for auto-reception of samples upon creation
- #1433 Added Submitter column in Sample's analyses listing
- #1441 Added Auto ID Behavior for Dexterity Contents
- #1422 Notify user with failing addresses when emailing of results reports
- #1420 Allow to detach a partition from its primary sample
- #1410 Email API


**Changed**

- #1451 Render Analysis Remarks in Listings as HTML
- #1445 Allow formatted HTML in the other rejection reasons
- #1428 Publish verified partitions
- #1429 Add2: Do not set template values on already filled fields
- #1427 Improved performance of Sample header table rendering
- #1417 Cache allowed transitions for analyses on the request
- #1413 Improved Email Publication


**Removed**

- #1449 Removed InheritedObjects (Inherited from) field from Batch
- #1430 Removed Identifier Types


**Fixed**

- #1462 Autofill Client Contact in Sample Add form when current user is a client
- #1461 Allow unassign transition for cancelled/rejected/retracted analyses
- #1449 sort_limit was not considered in ReferenceWidget searches
- #1449 Fix Clients were unable to add batches
- #1453 Fix initial IDs not starting with 1
- #1454 Fix occasional error when labeling samples w/o report as printed
- #1452 Fix missing error percentage calculation for reference samples
- #1447 New Client contact has access to last client's Sample only
- #1446 Parameter `group` in `contact._addUserToGroup` was not considered
- #1444 Fixed Worksheet autofill of wide Iterims
- #1443 Fix non-saving checkbox values for manual Interims in Analysis Services
- #1439 Fix global Auditlog when Analyses/Attachments were removed
- #1426 Render HTML Texts in Info Popups correctly
- #1423 Use the value set for ui_item property when displaying ReferenceWidget
- #1425 Fix adapter priority for widget visibility
- #1421 Fix Search Query for Batches Listing
- #1418 Subscriber adapters not supported in clients listing
- #1419 Mixed permissions for transitions in client workflow
- #1414 Occasional "OSError: [Errno 24] Too many open files" in frontpage


1.3.1 (2019-07-01)
------------------

**Added**

- #1401 Allow capture of text results
- #1391 Samples for internal use (lab personnel) only
- #1384 Added missing Html Field to ARReport
- #1369 Add getter to access the title of the sample condition directly
- #1347 Consider laboratory workdays only for the late analyses calculation
- #1324 Audit Log

**Changed**

- #1392 Hide partitions to clients when "Show Partitions" is not selected
- #1371 Allow sample publication without sending Email
- #1355 Make api.getId to also consider id metadata column (not only getId)
- #1352 Make timeit to not display args by default
- #1330 Make guards to not rely on review history
- #1339 Make Forumula a required field on Calculation

**Removed**

- #1359 Remove stale Sample/Partition objects from ZODB
- #1362 Remove unnecessary code from worksheet listing (bad performance)
- #1346 Remove Searchable Text Overrides
- #1328 Remove transition filtering in Worksheet listings

**Fixed**

- #1404 Avoid conflict errors during email publication
- #1403 Also consider the detached states as cancellable
- #1397 Fix Worksheet does not show the contained analyses
- #1395 Make Action Handler Pool Thread-Safe
- #1389 Analysts and Labclerks cannot create worksheets
- #1386 No auto-rejection of Sample when rejection reasons are set in Add form
- #1382 Fix double publication of the same sample when using multi-reports
- #1368 Fix WF state propagation on partition verification
- #1367 Clients can see interim values of analyses not yet verified
- #1361 Fix leap sample ID sequence after secondary sample
- #1344 Handle inline images in Results Interpretation
- #1336 Fix result capture date inconsistency
- #1334 Number of analyses are not updated after modifying analyses in a Sample
- #1319 Make api.get_review_history to always return a list
- #1317 Fix Analysis Service URL in Info Popup
- #1316 Barcodes view does not render all labels once Samples are registered
- #1341 Moved Agilent instruments from core to senaite.instruments
- #1356 Fixed selection on Analysis Spec on AR
- #1353 Fixed saving of PublicationSpecification on AR
- #1376 Fixed ft120.py to properly import winescan ft120 CSV files


1.3.0 (2019-03-30)
------------------

**Added**

- #1310 Support for radio copy in Sample Add view
- #1309 Added Samples rejection view
- #1291 "Remove" transition for empty Worksheets
- #1259 Added Facscalibur instrument import interface
- #1244 Added "Body for Sample Invalidation email" field in setup
- #1231 Add Client ID Column in Batch Listing
- #1230 Add Client ID Column in Sample Listing
- #1222 Added User and Security API
- #1217 Added filtering buttons in Analyses listings (Valid, Invalid, All)
- #1193 Added viewlets for partition and primary ARs
- #1180 Analysis Request field-specific permissions managed in `ar_workflow`
- #1154 Default to "Active" Worksheets in listing
- #1153 Progress bar in Worksheet listing
- #1120 Listing: Confirm before transition
- #1077 Creation of retests for blanks and controls via retraction
- #1077 Creation of retests for duplicates via retraction
- #1077 Auto-retraction of dependents on retract transitions
- #1077 The removal of a routine analysis causes the removal of its duplicates
- #1077 Added `rollback_to_received` transition in `ar_workflow`
- #1077 Added `rollback_to_open` transition in `worksheet_workflow`
- #1077 Battery of doctests for `referenceanalysis_workflow`
- #1077 Battery of doctests for `duplicateanalysis_workflow`
- #1077 Battery of doctests for `analysis_workflow`
- #1066 Enhanced partitioning system (partition magic)

**Changed**

- #873 Generalize the assignment of values into fields for Setup on import
- #1257 Fix Traceback for MultiSelectionWidgets in View Mode for UIDReferenceFields
- #1249 Render attachments in report in worksheets too
- #1243 ID Server Suffix Support for Retested ARs
- #1240 Support action-specific `workflow_action` requests with named adapters
- #1215 Do not copy CaptureDate and Result in retest analyses when created
- #1215 Do not modify the ID of analysis on retraction
- #1207 Make use of adapters for instrument auto-import
- #1206 Make use of adapters for instrument import/export interfaces
- #1203 Remove explicit definition of transitions in AR listing
- #1192 Integrate Container and Preservation in Partition Magic
- #1180 Analysis Request default ID Format becomes {sampleType}-{seq:04d}
- #1180 `visibility` attr behavior (AR fields) in favour of field-specific perms
- #1180 Sanitized `ar_workflow` regarding to guards, transitions and permissions
- #1180 Sample content type discarded in favour of Analysis Request
- #1182 Allow open min/max values in analysis specifications
- #1000 Refactor service calculation dependency/dependants functionality to API
- #1176 Unbind `cancellation_workflow` from AnalysisRequest content type
- #1173 Improve Resultsinterpretation Form
- #1161 Listing: Transposed worksheet improvements
- #1150 Completeness of not yet published Analysis Requests is not 100%
- #1147 Set empty option selected by default in result options
- #1148 Add "All" filter in Analysis Requests listings
- #1148 Make "Active" filter to display ongoing Analysis Requests only
- #1136 Skip objects w/o transitions in allowed transitions calculation
- #1135 Listing: Separate Remarks Toggle-Handle
- #1128 Listing: Removed non-conform handling of disabled fields
- #1123 Listing: Handle visibility of selected rows
- #1117 Removed `attachment_due` state and transition from analysis workflow
- #1114 Listing integration for Worksheet Templates
- #1109 Unassignment of an analysis causes the removal of its duplicates
- #1077 Rejection of an analysis causes the removal of its duplicates
- #1077 Don't allow to cancel Analysis Requests with assigned/submitted analyses
- #1077 Decouple `cancellation_workflow` from Analysis content type
- #1077 Refactored `referenceanalysis_workflow` + after transitions and guards
- #1077 Refactored `duplicateanalysis_workflow` + after transitions and guards
- #1077 Refactored `analysis_workflow` + after transitions and guards
- #1095 New worksheet results listing
- #1091 New Worksheet blank/control/duplicate listings
- #1093 Listing integration for Analysis Specification Widget
- #1092 Listing integration for Profile Analyses Widget
- #1081 API functions improved
- #1076 Instrument QC Viewlet Availability
- #1071 Reinvented Listing Tables
- #1066 Set default page size for listings to 50
- #1063 Permission for ar_add changed to "AddAnalysisRequest"
- #1064 Python 2.x is not supported by WeasyPrint v43. Pinned version: 0.42.3

**Removed**

- #1308 Remove install screen
- #1224 Replace publication engine with SENAITE IMPRESS
- #1207 Remove results auto-import interval from Setup: no limitations to cron
- #1180 Remove AdHoc field from Analysis Request
- #1180 Remove support for "sampleId" and "sample" keywords in ID Formatting
- #1180 Remove Sample views and accesses to Sample content types
- #1180 Remove Sample Partitions classic functionality
- #1167 Remove filtering by department
- #1149 Remove "Unpublished" filter from Analysis Requests listing
- #1132 Remove "Submitted by current user" icon from AR listing (performance)
- #1125 Remove Sample views, listings and links to Sample(s) from everywhere
- #1118 Removed all legacy Bika Listing / Advanced Filtering from Codebase
- #1077 Remove Sample-specific states from analysis workflow
- #1077 Remove `worksheetanalysis_workflow`
- #1059 Remove updates alert viewlet
- #1060 Remove classic portlets
- #1058 Remove gpw dependency
- #1058 Remove broken Quality Control reports
- #1057 Remove z3c.unconfigure dependency
- #1056 Remove collective.taskqueue dependency
- #808 Remove old AR Add code


**Fixed**

- #1109 Linking LabContacts to LDAP-user not possible
- #1283 Retracting a calculated Analysis leads to an inconsistent state
- #1281 Adding Analyses to an existing Worksheet fails
- #1269 Render analysis remarks conditionally
- #1277 Traceback in Manage Analyses
- #1245 Not all clients are shown in clients drop menu for Productivity Reports
- #1239 Fix and Improve Stickers
- #1214 Disallow entry of analysis results if the sample is not yet received
- #1213 Fix instrument notification display in Manage Results View
- #1212 Fix typo in SamplingFieldsVisibility
- #1191 Some worksheets pre-1.3 with published analyses remain in open/to_be_verified state
- #1190 Fixed evolution chart for reference analyses
- #1183 Fix results calculation of dependent calculations
- #1175 Fixed Version Display of SENAITE CORE Add-on in the Quickinstaller Tool
- #1142 Fix instrument QC Analyses Table
- #1137 Fixed and refactored log view
- #1124 Traceback when invalidating an Analysis Request with retracted analyses
- #1090 Primary AR does not recognize created Partitions
- #1089 Deepcopy Service Interims to Analyses
- #1082 Worksheet folder listing fixtures for direct analyst assignment
- #1080 Improve searchability of Client and Multifile fields
- #1072 Calculations with dependents do not work after 1.2.9 update
- #1070 Cannot get the allowed transitions (guard_sample_prep_transition)
- #1065 Creation of reflex rules does not work with senaite.lims add-on


**Security**

- #896 Users without privileges can create reports
- #1258 Fix widget permissions for Specs/Profiles/Templates Widgets
- #1237 Global Permission and Role Mappings refactoring
- #1077 Transitions and states strongly bound to DC Workflow + guards security


1.2.9 (2018-10-08)
------------------

**Added**

- #1051 Show the Due date in late's image tooltip in Analysis Requests listings
- #1048 Allow to set the pagesize in listings and show total number of results
- #1031 Added profiling and timing decorators
- #1001 Option to show Interim fields on results reports
- #1024 Function to get the Verifiers from an Analysis Request
- #1019 Support for min and max warns in range charts
- #1003 Alphanumeric numbering in sequential IDs generator

**Changed**

- #1050 Added Late filter button to analysisrequests listing
- #1046 Show "Date Registered" instead of "Date Created" in Analysis Requests listings
- #1044 State of analyses in retests is set to `received` by default (was `to_be_verified`)
- #1042 Function api.get_object() supports UID as input param
- #1036 Manage Analyses: Check permission of the AR to decide if it is frozen
- #764 Code cleanup and redux of 2-Dimensional-CSV instrument interface
- #1032 Refactored and fixed inconsistencies with Analysis TAT logic
- #1027 Refactored relationship between invalidated ARs and retests
- #1027 Rename `retract_ar` transition to `invalidate`
- #1012 Refactored Contacts listing
- #1010 Increased max length of Results options to 255 chars (was 40)
- #899 Sample's Date Received editable only when `received` analyses exist

**Removed**

- #1232 Remove `uniquefieldvalidator` for Client Names
- #1026 Removed auto-digest of results reports on verify transitions
- #1005 Removed databasesanitize package
- #992 Removed "Attach" report option for Attachments

**Fixed**

- #1216 Allow manual entry (if granted) of results if instrument is invalid
- #1051 Analyses Requests w/o submitted results always appear as not late
- #1047 Fix translate utility function
- #1049 Secondary Analysis Request changes received date of Sample
- #1041 Reject transition is available to Client once AR/Sample is received
- #1043 Invalid AR Retested informative message is not prominent enough
- #1039 Detection limit criteria from retracted analysis is preserved
- #1037 Display supplier view instead of reference samples per default
- #1030 Earliness of analysis is not expressed as minutes
- #1029 TAT in Analysis TAT over time report does not display days
- #1029 TAT in Analysis TAT over time report with decimals
- #1029 Need to always choose an analyst in productivity reports
- #1034 Attachments assigned to Analyses break and get orphaned when the referenced Analysis was removed
- #1028 Numbers for productivity report "Analyses by client" are all zero
- #1022 Date Received saved as UTC time
- #1018 Fix AR Add cleanup after template removal
- #1014 ReferenceWidget does not handle searches with null/None
- #1008 Previous results from same batch are always displayed in reports
- #1013 ARs and Samples from other clients are listed when logged in as contact
- #991 New client contacts do not have access to their own AR Templates
- #996 Hide checkbox labels on category expansion
- #990 Fix client analysisspecs view
- #888 Order of Interim Fields not maintained on ARs


1.2.8 (2018-08-11)
------------------

**Added**

- #965 Added operators for max and min values in Specifications
- #947 Instrument import interface: Cobas Integra 400plus
- #924 Added ExtProxyField for its use in SchemaExtender

**Changed**

- #971 Refactored Client's Analysis Requests, Samples and Batches listings
- #945 Show AR Remarks in Worksheet ManageResults views
- #953 Refactored Analysis Categories Listing
- #956 Refactored LabContacts Listing
- #955 Refactored Departments Listing
- #954 Refactored Attachment Types Listing
- #944 Remarks style in Manage Results/Analyses
- #943 AnalysisRequest View Remarks Field Style
- #938 Refactored Analysis Profiles Widget
- #937 Refactored Analysis Specifications Widget
- #936 Refactored AR Templates Listing
- #933 Refactored SampleConditions Listing
- #932 Refactored Calculation Listing
- #931 Refactored AnalysisSpecs Listing
- #935 Refactored SamplingDeviations Listing
- #926 Refactored Analysis Services Listing
- #916 Refactored Instruments Listing
- #919 Refactored Profiles Listing
- #915 Refactored SamplePoints Listing
- #914 Refactored Sampletypes Listing
- #913 Refactored Methods Listing View

**Removed**

- #972 Remove "Linked Sample" from Sample
- #912 Remove "Default AR Specifications" Selection from Setup
- #901 Remove explicit permission settings for clients
- #900 Removed basic handling of custom Sample Preparation Workflows

**Fixed**

- #983 Traceback in Client's Analysis Specs view
- #986 Result input fields are not read-only for analyst after submission
- #985 Do not display content actions in listings from inside Client
- #966 Traceback in Analyses listings when analysis unit is a numeric value
- #959 Time not displayed for Date Created in Analysis Requests listings
- #949 Retain AR Spec if Analyses were added/removed
- #948 Inactive Sample Types shown in Analysis Specifications
- #940 Label "Date Received" appears twice in Analysis Request view
- #917 Localization of date and time strings in listings
- #902 Attribute error when updating QC results using an import interface
- #456 Date Published appears two times on the header table of AR view
- #898 Cannot view/edit Supplier. Tabs for different views now visible.
- #905 Users created through LabContact's Login Details view are added to "Clients" group
- #906 DateTime Widget does not display the Time
- #909 List of clients cannot sort by Client ID
- #921 Missing interim fields in worksheet/analyses_transposed view
- #920 Refactored Remarks and created RemarksField and RemarksWidget
- #958 Traceback on batch book view
- #960 Traceback on AnalysisSpec Log
- #962 Calculated results not marked for submission if zero
- #964 Dormant Analysis Services displayed in AR Templates
- #967 Avoid deepcopy, "Can't pickle acquisition wrappers"


1.2.7 (2018-07-10)
------------------

**Added**

- #836 Allow (Multi-)Attachment upload available in AR Add
- #846 Transifex integration
- #848 Show icon on the Supply Order View
- #844 Missing interface for AR Report added
- #858 Only Lab Managers sees rejected analysis requests

**Changed**

- #891 Better default styles for listing tables
- #887 New icon set
- #879 Upgrade lxml version from 2.3.6 to 3.6.0 and  Plone from 4.3.15 to 4.3.17
- #873 Sample Type field editable in AR and Sample edit views before receive
- #868 AR Add Form: Refactoring and Styling
- #817 Make warn message clearer if transition rejection is due to missing sampler

**Fixed**

- #892 Display only active Analyses for new Profiles
- #889 Fix override order of message catalogs
- #864 Sort order in setup of analysis services wrong
- #881 Fixed JS i18n catalog names
- #880 Fix message factory
- #878 Fix AR Header Table Styles and Ajax Failures
- #877 Worksheet's attachments column is empty after results import from file
- #857 "other" reasons are not listed on AR rejection notifications (e-mail and attached pdf)
- #875 Fix Batch AR View
- #872 Date format appears wrong in Users history administrative report
- #855 Dashboard is displayed to Lab clerks after login only
- #871 Fix OpenTagError for i18ndude
- #865 AR VAT Amount when using Profiles is not calculated correctly
- #851 Fix worksheet verification with retracted results


1.2.6 (2018-06-08)
------------------

**Changed**

- #838 Unpinned WeasyPrint to allow Addon to use newer version
- #820 Always allow interim fields to be added to Analysis Services
- #826 Display signatures of verifiers instead of dept managers in results report
- #814 Change naming from Bika LIMS Configuration to LIMS Configuration in the Site Setup page
- #814 Change naming from Bika Setup to Setup in the LIMS Configuration section found in the Site Setup page

**Fixed**

- #842 Re-compiled Coffee-Scripts with version 1.12.7
- #824 Instrument Listing Views Fixes and Refactoring
- #840 Fix date range filter for "Data entry day book" report
- #828 Traceback when removing a retracted analysis through Manage Analyses view
- #832 Set new calculation Interims to dependant services
- #833 Fix sort order of interims in Calculations and Analysis Services
- #834 Fix Duplication Action for Analysis Services
- #835 List only published ARs when "Published" Filter is active
- #825 Error when exporting Worksheets list with `senaite.exporter`
- #821 Cannot retract single analysis services


1.2.5 (2018-05-05)
------------------

**Added**

- #777 Delay option for searches in reference widget combos
- #806 Include Client ID when setting up ARReport on the IDServer

**Changed**

- #815 Change description and title of the invalidation notification option

**Removed**

- #811 Remove senaite.api import in printform
- #807 Remove "queued_ars" JS call to avoid 404
- #800 Remove Dry Matter from tests
- #779 Remove Dry Matter functionality

**Fixed**

- #813 Saving AR results gives TypeError: can only compare to a set
- #799 On AR Listing, edit for Date Sampled not working when Sampler has a value
- #776 Analyses submission in Worksheet is slow
- #726 404 Error raised when clicking Print Samples Sheets from within a client
- #802 Remove Dry Matter remainders
- #781 Delete Permission on ARs for Lab Managers
- #784 Fix workflow state filter not kept when expanding categories in AS listing
- #786 Fix inactive services listed in AR "Manage Analyses" forms
- #775 Analyses on Analysis Requests are hyperlinked to their Worksheets
- #769 Traceback when submitting duplicate when Duplicate Variation is not set
- #771 Slow Searches in Listing Views
- #774 When retracting an Analysis Requests its analyses are also retracted
- #772 Improved UID check in API


1.2.4 (2018-04-06)
------------------

**Added**

- #741 CSV Importer for 'Cobas Taqman 48' Instrument Interface
- #737 Added Instrument: Metler Toledo DL55
- #730 Added Instrument: LaChat QuickChem FIA
- #729 Added Instrument: Varian Vista-PRO ICP
- #694 Added "Warn Min" and "Warn Max" subfields in Analysis Specifications
- #710 Added more builtin functions for Calculations

**Changed**

- #765 Department Filtering Improvements
- #746 StringField to UIDReferenceField for Default Department of Lab Contact
- #744 Updated WeasyPrint to 0.42.2
- #694 Out of range/shoulders logic redux, ported to `api.analysis`
- #694 Make getResultRange functions from Analysis-types consistent
- #694 Out of range/shoulders icons are rendered in AnalysesView

**Removed**

- #694 Removal of "Permitted % Error" subfield in Analysis Specifications
- #694 Removal of Adapters for out of range icons

**Fixed**

- #763 Datetime conversion error in CSV Importer of Taqman 48
- #761 Dormant Reference Definitions were listed for selection on WS Templates
- #735 Interim fields not created for QC Analyses on WSs
- #752 Published Date field of Analyses is never set
- #760 Default to empty the Title field when creating a new Analysis Specification
- #759 Date error in invoice batch creation although End date is after Start date
- #743 Traceback when accessing the view of a Statement
- #734 Chameleon parse error in productivity reports
- #750 Wrong redirect after Batch Label edit or creation
- #721 Fix filter functionality of Worksheets after sort/pagination
- #738 Traceback when Invalidating Analysis Requests
- #694 Bad calculation of min and max in ReferenceResults on negative result
- #694 Instrument validity not updated in accordance with latest QC tests
- #694 Result range shoulders computed badly on full/partial negative specs
- #725 Late Analyses are not filtered by Department
- #723 Solve Traceback on Print Samples Sheet
- #724 Department Filtering Portlet appears only for the manager with 'admin' username
- #720 Make automatic sticker printing work with 'registered' option activated
- #719 Fix interim fields result and calculation updating on the 2-Dimensional-CSV instrument
- #716 Samples from inside Batch are not filtered correctly
- #707 AR Add: Set default contact on client change
- #700 Fix filtering by review state in aggregated list of analyses
- #715 AR Rejection Fails when e-mail Notification is enabled
- #709 Fix removal not possible of last non-verified Analysis in Manage Analysis View
- #706 Filtering by Department is not working
- #712 Dates in date picker are visible again
- #703 Containers of Duplicated Analyses are not found
- #698 Fix Publish Actions for Batches
- #696 Worksheet count in dashboard is wrong in when filtered by department


1.2.3 (2018-02-23)
------------------

**Added**

- #666 Added Unpublished filter in Analysis Requests list

**Changed**

- #690 Refactored and improved client folder listing view
- #689 Allow to hide Analyses in any AR state
- #685 Display the stacked bars in evo charts sorted by number of occurrences
- #685 Small changes in colours palette for evo charts from Dashboard
- #684 Aggregated lists of analyses set to read-only mode
- #674 Dashboard with slightly better performance
- #621 AnalysesView code refactoring
- #668 AR Add: Debounce expensive XHR calls
- #660 Better style for reference widgets
- #627 Unassigned filter on Analysis Requests view does not work
- #659 Display the Unit in Profile Analyses Listing
- #636 Do not display "Advanced..." item in object's workflow actions menu
- #652 Added Sample Type, Partition ID and Date Sampled in Code_128_1x48mm sticker
- #655 Updated German Translations
- #647 Refactored bika.lims.bikalisting.js + several functional fixtures
- #637 Deassociate Analysis Request portal type from `worksheetanalysis_workflow`

**Fixed**

- #688 A traceback was appearing when navigating to rejected samples
- #686 Balloon button for adding Remarks is displayed while disabled in Setup
- #681 Invalidated Analysis Requests do not appear on Dashboard's evo chart
- #680 Fix Traceback with periodicity in DashboardView
- #679 Analysis could not set to "Hidden" in results view
- #677 Fix category toggling when the category name contains spaces
- #672 Traceback on automatic sticker printing in batch context
- #673 QC Analyses and Samples not totaled correctly in Worksheets list
- #670 Listings: Fix sort_on change on Show More click
- #653 Points in QC Charts are not displayed in accordance with capture date
- #662 Viewing Cancelled AR's fails
- #550 Wrong Listings of Analyses called from Dashboard
- #666 "Rejected" filter is displayed in AR lists regardless of Setup setting
- #666 "To be preserved" filter is displayed in AR lists regardless of Setup setting
- #666 "Scheduled sampling" is displayed in AR lists regardless of Setup setting
- #666 "To be sampled" filter is displayed in AR lists regardless of Setup setting
- #664 Improved async transition loading and workflow button rendering in listing tables
- #658 Worksheet listing view shows old- invalid Analysts
- #663 AR Report Listing shows all Reports
- #654 Default's Multi Analysis Request report gives a Traceback
- #649 Specification fields decimal-mark validator not working for new opened categories
- #637 Analysis Requests are never transitioned to assigned/unassigned
- #641 Broken Analyses list on ReferenceSample in Supplier
- #640 Broken Reference Sample Results view


1.2.2 (2018-02-09)
------------------

**Added**

- #594 Add button in Sample View for the createion of Analysis Requests
- #607 Ability to choose sticker template based on sample type
- #480 Sample panel in dashboard
- #617 Instrument import interface: 2-Dimensional-CSV
- #617 Instrument import interface: Agilent Masshunter
- #617 Instrument import interface: Shimadzu GCMS-QP2010 SE
- #617 Instrument import interface: Shimadzu GCMS-TQ8030 GC/MS/MS
- #617 Instrument import interface: Shimadzu ICPE-9000 Multitype
- #617 Instrument import interface: Shimadzu HPLC-PDA Nexera-I
- #617 Instrument import interface: Shimadzu LC MS/MS Nexera X2
- #537 Instrument import interface: Sysmex XT-4000i
- #536 Instrument import interface: Sysmex XT-1800i
- #607 Barcode and labelling depending on Sample Type
- #618 When previewing stickers the number of copies to print for each sticker can be modified.
- #618 The default number of sticker copies can be set and edited in the setup Sticker's tab.

**Changed**

- #619 Changed listing tables search logic to operate on catalog metadata
- #621 Change Errors to Warnings when importing instrument results

**Fixed**

- #639 Analysis Requests from inside Batch are not filtered correctly
- #591 Fixed workflow publish recursion error that reached max depth
- #634 Fix undefined Symbols in Sample Transition Guards
- #616 Fix character encodings in analysisservice duplication
- #624 TypeError: "Can't pickle objects in acquisition wrappers" (WorksheetTemplate)
- #530 Calculated results do not get updated when importing instrument results
- #614 Fix accreditation category titles
- #611 Advanced filter bar: filter Analysis Requests by Service name not working
- #622 (Re-)Installation always adds another identifier type
- #620 Client batch list is not filtered by state
- #628 Hide Department on lab contact inherited from Person
- #631 Traceback on stickers display


1.2.1 (2018-01-26)
------------------

**Added**

- #555 Don't allow the deactivation of Analysis Services with active dependencies
- #555 Don't allow the activation of Analysis Services with inactive dependents

**Changed**

- #569 Minimalistic dashboard indicators

**Fixed**

- #606 Handle unicode queries in Client ReferenceWidgetVocabulary
- #603 Out of range Icons are not displayed through all Analysis states
- #598 BadRequest error when changing Calculation on Analysis Service
- #593 Price/Spec/Interim not set in AR Manage Analyses
- #585 Empty value for Analysis Request column in aggregated list of analyses
- #578 Fix translation for review state titles in listings
- #580 Fix calculations using built-ins
- #563 Deactivated Analyses are added in new ARs when using Analysis Profiles/Template
- #562 Client Batch lists are empty
- #561 Sampler field is not displayed in Analysis Request Add form
- #559 Fix numeric field event handler in bika.lims.site.js
- #553 Fixed that images and barcodes were not printed in reports
- #551 Traceback in Worksheet Templates list when there are Instruments assigned
- #571 Added try/except around id-template format function to log key errors in ID generation


1.2.0 (2018-01-03)
------------------

**Added**

- #498 Added getPriorityText method to Analysis Request

**Changed**

- #519 #527 #528 bika.lims to senaite.core distribution

**Fixed**

- #522 Worksheets: Analyses listing does not show attached Analyses
- #514 Site Error when listing Dormant Worksheet Templates
- #517 Expired Reference Samples are displayed in Add Blank/Add Control views
- #517 Inactive services displayed for selection in Add Blank/Add Control views
- #516 List of Analyses Services is not properly filtered by state
- #516 Activate and Deactivate buttons do not appear in Analysis Services list
- #512 Duplicates transition to "Attachment due" after submit
- #499 Wrong slots when adding analyses manually in Worksheet with a WST assigned
- #499 When a Worksheet Template is used, slot positions are not applied correctly
- #499 Applying a WS template which references a Duplicate raises an Error
- #513 ShowPrices doctest is failing
- #488 JS Errors in bika.lims.analysisrequest.js


1.1.8 (2017-12-23)
------------------

**Added**

- #440 ITopLeft, ITopRight and ITopWide hooks (placeholders) in bikalisting
- #472 Dashboard panels visibility by roles
- #467 All/Mine filters in Dashboard panels
- #423 Instrument import interface for Abbott's m2000 Real Time

**Changed**

- #469 Remove unique field validator for Batch titles
- #459 PR-1942 Feature/instrument certification interval refactoring
- #431 Make ARAnalysesField setter to accept Analysis/Service objects

**Fixed**

- #494 Rejection reasons widget does not appear on rejection
- #492 Fix AR Add Form: CC Contacts not set on Contact Change
- #489 Worksheet Templates selection list is empty in Worksheets view
- #490 Fix AR Add Form: No specifications found if a sample type was set
- #475 Assigning Analyses to a WS raises AttributeError
- #466 UnicodeDecodeError if unicode characters are entered into the title field
- #453 Sample points do not show the referenced sample types in view
- #470 Sort order of Analyses in WS print view wrong
- #457 Calculation referring to additional python module not triggered
- #459 Traceback in Instruments list after adding a calibration certificate
- #454 Click on some analyses pops up a new page instead of object log
- #452 Traceback error when deleting attachment from Analysis Request
- #450 Traceback after clicking "Manage Results" in a WS w/o Analyses assigned
- #445 Fix AR Add Form: No sample points are found if a sample type was set


1.1.7 (2017-12-01)
------------------

**Added**

- #377 XML importer in Instrument Interface of Nuclisense EasyQ

**Removed**

- #417 Remove calls to deprecated function getService (from AbstractAnalysis)

**Fixed**

- #439 Cannot verify calculated analyses when retracted dependencies
- #432 Wrong indentation of services in Worksheet
- #436 Auto Import View has an Add Button displayed, but shouldn't
- #436 Clicking on the Add Button of Instrument Certifications opens an arbitrary Add form
- #433 Analyses not sorted by sortkey in Analysis Request' manage analyses view
- #428 AR Publication from Client Listing does not work
- #425 AR Listing View: Analysis profiles rendering error
- #429 Fix worksheet switch to transposed layout raises an Error
- #420 Searches by term with custom indexes do not work in clients folder view
- #410 Unable to select or deselect columns to be displayed in lists
- #409 In Add Analyses view, analyses id are displayed instead of Analysis Request IDs
- #378 Fix GeneXpert interface does not import results for multiple analyses
- #416 Fix inconsistencies with sorting criterias in lists
- #418 LabClerks don't have access to AR view after received and before verified
- #415 Referencefield JS UID check: Don't remove Profile UIDs
- #411 Analyses don't get selected when copying an Analysis Request without profiles


1.1.6 (2017-11-24)
------------------

**Changed**

- #390 Remove log verbosity of UIDReference.get when value is None or empty

**Fixed**

- #403 Calculations not triggered in manage results view
- #402 Sort Analysis Services correctly based on their Sortkey + Title (Again)
- #398 PR-2315 ID Server does not find the next correct sequence after flushing the number generator
- #399 PR-2318 AR Add fails silently if e.g. the ID of the AR was already taken
- #400 PR-2319 AR Add fails if an Analysis Category was disabled
- #401 PR-2321 AR Add Copy of multiple ARs from different clients raises a Traceback in the background
- #397 Fix Issue-396: AttributeError: uid_catalog on AR publication


1.1.5 (2017-11-20)
------------------

**Added**

- #386 PR-2297 Added seeding function to IDServer
- #372 Added build system to project root
- #345 'SearchableText' field and adapter in Batches
- #344 PR-2294 Allow year in any portal type's ID format string
- #344 PR-2210 ID Server and bika setup updates along with migation step
- #321 PR-2158 Multiple stickers printing in lists
- #319 PR-2112 Laboratory Supervisor
- #317 Enable backreferences associated to UIDReference fields
- #315 PR-1942 Instrument Certification Interval
- #292 PR-2125 Added descriptions for Analysis Requests
- #291 PR-1972 Landscape Layout for Reports
- #286 Added Github Issue/PR Template
- #281 PR-2269 Show the Unit in Manage Analyses View
- #279 Allow external Python library functions to be used in Calculation Formulas
- #279 Calculation formula test widgets
- #279 PR-2154 New ar add form

**Changed**

- #385 PR-2309 Unnecessary loops were done in instrument listing views
- #369 Let DateTimeField setter accept datetime.datetime objects and convert them
- #362 Add "Methods" column and hide unused columns in Analysis Services list
- #353 Remove deprecation warnings
- #338 Preserve Analysis Request order when adding into Worksheet
- #338 Analyses sorted by priority in Add Analyses view
- #333 Display analyses sorted by sortkey in results report
- #331 Sort analyses lists by sortkey as default
- #321 Sticker's autoprint generates PDF instead of browser's print dialog
- #312 Worksheet: "Print" does not display/print partial results
- #306 PR-2077 Better usability of Clients lists for sites with many users
- #298 PR-2246 Implemented ProxyField to fix data duplication between ARs and Samples

**Fixed**

- #419 'getLastVerificator' function of Abstract Analyses fails when there is no Verificator.
- #388 Unable to get the portal object when digesting/creating results report
- #387 ClientWorkflowAction object has no attribute 'portal_url' when publishing multiple ARs
- #386 PR-2313 UniqueFieldValidator: Encode value to utf-8 before passing it to the catalog
- #386 PR-2312 IDServer: Fixed default split length value
- #386 PR-2311 Fix ID Server to handle a flushed storage or existing IDs with the same prefix
- #385 PR-2309 Some objects were missed in instrument listing views
- #384 PR-2306 Do not use localized dates for control chart as it breaks the controlchart.js datetime parser
- #382 PR-2305 TypeError in Analysis Specification category expansion
- #380 PR-2303 UnicodeDecodeError if title field validator
- #379 Missing "Instrument-Import-Interface" relationship
- #375 Dependencies error in Manage Analyses view
- #371 Reflex rules don't have 'inactive_state' values set
- #365 LIMS installation fails during setting client permissions in bika_setup
- #364 Error on Manage Results view while adding new Analyses from different Category
- #363 PR-2293 Add CCEmails to recipients for Analysis Request publication reports
- #352 Traceback on listings where objects follow the bika_inactive_workflow
- #323 Allow IDServer to correctly allocate IDs for new attachments (add Attachment to portal_catalog)
- #344 PR-2273. Ensure no counters in the number generator before initialising id server
- #343 PR-2281 Fix publication preferences for CC Contacts
- #340 TypeError: "Can't pickle objects in acquisition wrappers" (Calculation)
- #339 Index not found warnings in bika listing
- #337 Error when adding reference analysis in a Worksheet
- #336 Accreditation Portlet renders an error message for anonymous users
- #335 The Lab Name is always set to "Laboratory" after reinstallation
- #334 TypeError (setRequestId, unexpected keyword argument) on AR Creation
- #330 Show action buttons when sorting by column in listings
- #318 PR-2205 Conditional Email Notification on Analysis Request retract
- #316 Small fixes related with i18n domain in Worksheet's print fixtures
- #314 'SamplingDate' and 'DateSampled' fields of AR and Sample objects don't behave properly
- #313 The PDF generated for stickers doesn't have the right page dimensions
- #311 PR-1931 Fixed Link User to Contact: LDAP Users not found
- #309 PR-2233 Infinite Recursion on Report Publication.
- #309 PR-2130 Copied ARs are created in random order.
- #308 Analysis Service' interim fields not shown
- #307 Fix sorting of Analysis Services list and disable manual sorting
- #304 PR-2081 Fixed multiple partition creation from ARTemplate
- #304 PR-2080 Batch Book raises an Error if the Batch inherits from 2 ARs
- #304 PR-2053 Computed Sample Field "SampleTypeUID" does not check if a SampleType is set
- #304 PR-2017 Fixed BatchID getter
- #304 PR-1946 Showing Verified Worksheets under all
- #299 PR-1931 Fixed Link User to Contact: LDAP Users not found
- #298 PR-1932 AttributeError: 'bika_setup' on login on a new Plone site w/o bika.lims installed
- #297 PR-2102 Inline rendered attachments are not displayed in rendered PDF
- #296 PR-2093 Sort order in Bika Setup Listings
- #294 PR-2016 Convert UDL and LDL values to string before copy
- #293 Fix analysis_workflow permissions for Field Analysis Results
- #284 PR-1917 Solved WF Translation issues and fixed WF Action Buttons in Bika Listings
- #283 PR-2252 Traceback if the title contains braces on content creation
- #282 PR-2266 Instrument Calibration Table fixes
- #280 PR-2271 Setting 2 or more CCContacts in AR view produces a Traceback on Save


1.0.0 (2017-10-13)
------------------

**Added**

- #269 Added IFrontPageAdapter, to make front page custom-redirections easier
- #250 Sanitize tool to fix wrong creation dates for old analyses

**Fixed**

- #272 Unknown sort_on index (getCategoryTitle) in Worksheet's Add Analyses view
- #270 ParseError in Reference Widget Search. Query contains only common words
- #266 Worksheet column appears blank in Aggregated List of Analyses
- #265 ValueError in productivity report
- #264 Fix permissions error on site install
- #262 DateSampled does not appear to users other than labman or administrator
- #261 Checking async processes fails due to Privileges of Client Contact
- #259 Error when saving and Analysis Request via the Save button
- #258 Sorting Analysis Requests by progress column does not work
- #257 AttributeError (getRequestUID) when submitting duplicate analyses
- #255 Client contacts cannot see Analysis Requests if department filtering is enabled
- #249 Unable to reinstate cancelled Analysis Requests

**Security**

- #256 Restrict the linkeage of client contacts to Plone users with Client role only
- #254 Anonymous users have access to restricted objects


3.2.0.1709-a900fe5 (2017-09-06)
-------------------------------

**Added**

- #244 Asynchronous creation of Analysis Requests
- #242 Visibility of automatically created analyses because of reflex rule actions
- #241 Fine-grained visibility of analyses in results reports and client views
- #237 Performance optimizations in Analysis Request creation
- #236 Progress bar column in Analysis Requests list and Analyses number
- #233 Background color change on mouse over for fields table from ARAdd view
- #232 Display Priority in Analyses Add View from Worksheet and allow to sort
- #229 Highlight rows in bikalisting on mouse over
- #157 Catalog for productivity/management reports to make them faster

**Changed**

- #218 Render barcodes as bitmap images by default
- #212 Allow direct verification of analyses with dependencies in manage results view
- #213 Sampling Date and Date Sampled fields refactoring to avoid confusions
- #228 Translations updated
- #224 Remove warnings and unuseful elses in Analysis Request setters
- #193 Render transition buttons only if 'show_workflow_action' in view is true
- #191 Code sanitize to make Analysis Specifications folder to load faster

**Fixed**

- #248 Search using Client not working in Add Analyses (Worksheet)
- #247 Sample Type missing in analysis view for rejected samples
- #246 ZeroDivisionError when calculating progress
- #245 Missing Lab Contacts tab in Departments View
- #240 Unable to modify Sample point field in Analysis Request view
- #235 Fix Jsi18n adapter conflict
- #239 Sort on column or index is not valid
- #231 Partition inconsistences on secondary Analysis Requests
- #230 Priority not showing on Analysis Request listing
- #227 Malformed messages and/or html make i18ndude to fail
- #226 Action buttons are not translated
- #225 State inconsistencies when adding an analysis into a previous Analysis Request
- #223 TypeError when Analysis Service's exponential format precision is None
- #221 Filters by Service, Category and Client do not work when adding Analyses into a Worksheet
- #220 Not all departments are displayed when creating a new Lab Contact
- #219 When a Sample Point is modified in AR view, it does not get printed in report
- #217 Setupdata import fixes
- #216 Results reports appear truncated
- #215 All Samples are displayed in Analysis Request Add form, regardless of client
- #214 Status inconsistences in Analyses in secondary Analysis Requests
- #211 Sorting by columns in batches is not working
- #210 In some cases, the sampler displayed in results reports is wrong
- #209 AttributeError: 'NoneType' object has no attribute 'getPrefix' in Analysis Request add view
- #208 Rendering of plone.abovecontent in bika.lims.instrument_qc_failures_viewlet fails
- #206 Unknown sort_on index (getClientTitle) in Add Analyses view from Worksheet
- #202 Once a result is set, the checkbox is automatically checked, but action buttons do not appear
- #201 Results interpretation field not updated after verification or prepublish
- #200 Dependent analyses don't get selected when analysis with dependents is choosen in AR Add view
- #199 AttributeError when adding a Blank in a Worksheet because of Service without category
- #198 The assignment of a Calculation to a Method doesn't get saved apparently, but does
- #196 Error invalidating a published test report (retract_ar action)
- #195 List of Analysis Request Templates appears empty after adding a Sampling Round Template
- #192 Date Sampled is not displayed in Analysis Request View
- #190 Bad time formatting on Analysis Request creation within a Sampling Round
- #189 Bad time formatting when creating a secondary Analysis Request
- #187 After verification, department managers are not updated in results report anymore
- #185 Analysis services list not sorted by name
- #183 Decimals rounding is not working as expected when uncertainties are set
- #181 Client contact fields are not populated in Sampling Round add form
- #179 Wrong values for "Sampling for" and "Sampler for scheduled sampling" fields after AR creation
- #178 Sampler information is wrong in results reports
- #175 Changes in "Manage Analyses" from "Analysis Request" have no effect
- #173 NameError (global name 'safe_unicode' is not defined) in Analysis Request Add view
- #171 Error printing contact address
- #170 Index error while creating an Analysis Request due to empty Profile
- #169 ValueError (Unterminated string) in Analysis Request Add view
- #168 AttributeError 'getBatch' after generating barcode
- #166 Analyses don't get saved when creating an Analysis Request Template
- #165 AttributeError in Bika Setup while getting Analysis Services vocabulary
- #164 AttributeError on Data Import: 'NoneType' object has no attribute 'Import'
- #161 TypeError from HistoryAwareReferenceField while displaying error message
- #159 Date published is missing on data pulled through API
- #158 Date of collection greater than date received on Sample rejection report
- #156 Calculation selection list in Analysis Service edit view doesn't get displayed
- #155 Error while rejecting an Analysis Request. Unsuccessful AJAX call


3.2.0.1706-315362b (2017-06-30)
-------------------------------

**Added**

- #146 Stickers to PDF and new sticker 2"x1" (50.8mm x 25.4mm) with barcode 3of9
- #152 Caching to make productivity/management reports to load faster

**Changed**

- #150 Dynamic loading of allowed transitions in lists
- #145 Workflow refactoring: prepublish
- #144 Workflow refactoring: publish

**Fixed**

- #154 AttributeError on upgrade step v1705: getDepartmentUID
- #151 State titles not displayed in listings
- #149 Decimal point not visible after edition
- #143 Fix AttributeError 'getProvince' and 'getDistrict' in Analysis Requests view
- #142 AttributeError on publish: 'getDigest'
- #141 AttributeError on upgrade.v3_2_0_1705: 'NoneType' object has no attribute 'aq_parent'


3.2.0.1706-baed368 (2017-06-21)
-------------------------------

**Added**

- #133 Multiple use of instrument control in Worksheets

**Fixed**

- #139 Reference migration fails in 1705 upgrade
- #138 Error on publishing when contact's full name is empty
- #137 IndexError while notifying rejection: list index out of range
- #136 Worksheets number not working in Dashboard
- #135 Fix string formatting error in UIDReferenceField
- #132 ValueError in worksheets list. No JSON object could be decoded
- #131 "Show more" is missing on verified worksheets listing
- #129 Unsupported operand type in Samples view


3.2.0.1706-afc4725 (2017-06-12)
-------------------------------

**Fixed**

- #128 TypeError in Analysis Request' manage results view: object of type 'Missing.Value' has no len()
- #127 AttributeError while copying Service: 'float' object has no attribute 'split'
- #126 AttributeError during results publish: getObject
- #123 Analysis Request state inconsistences after upgrade step v3.2.0.1705
- #122 ValueError on results file import


3.2.0.1706-f32494f (2017-06-08)
-------------------------------

**Added**

- #120 Add a field in Bika Setup to set the default Number of ARs to add
- #88 GeneXpert Results import interface
- #85 Sticker for batch
- #84 Sticker for worksheet
- #83 Adapter to make the generation of custom IDs easier
- #82 Added a method the get always the client in stickers
- #75 Wildcards on searching lists

**Changed**

- #106 Predigest publish data
- #103 Prevent the creation of multiple attachment objects on results import
- #101 Performance improvement. Remove Html Field from AR Report
- #100 Performance improvement. Replacement of FileField by BlobField
- #97 Performance improvement. Removal of versionable content types
- #95 Performance improvement. Analysis structure and relationship with Analysis Service refactored
- #58 Defaulting client contact in Analysis Request Add view

**Fixed**

- #118 Results import throwing an error
- #117 Results publishing not working
- #113 Biohazard symbol blocks the sticker making it impossible to be read
- #111 Fix error while submitting reference analyses
- #109 Remarks in analyses (manage results) are not displayed
- #105 System doesn't save AR when selected analyses are from a department to which current user has no privileges
- #104 ReferenceException while creating Analysis Request: invalid target UID
- #99 Instrument's getReferenceAnalyses. bika.lims.instrument_qc_failures_viewlet fails
- #94 Site Search no longer searching Analysis Requests
- #93 Analyses did not get reindexed after recalculating results during import
- #92 Analyses disappearing on sorting by date verified
- #91 KeyError on Samples view: 'getSamplingDate'
- #90 AttributeError on Analysis Request submission: 'NoneType' object has no attribute 'getDepartment'
- #89 Analysis to be verified not showing results
- #87 AttributeError in analyses list: 'getNumberOfVerifications'
- #82 JS error while checking for rejection reasons in client view
- #80 CatalogError: Unknown sort_on index (Priority)
- #79 ValueError in Bika's DateTimeWidget
- #78 CatalogError in Batch View. Unknown sort_on index (BatchID)
- #77 ValueError in AR Add: time data '2016-05-10' does not match format '%Y-%m-%d %H:%M'
- #76 AttributeError in Client ARs view: bika_catalog
- #74 AttributeError: 'NoneType' object has no attribute 'getCalculation'
- #73 Analyses disappearing on sorting by date verified
- #72 Cancelled analyses appearing in aggregated list of analyses
- #71 AttributeError on publish: 'getRequestID'
- #70 The number of pending verifications displayed in analyses list is wrong
- #69 Selecting a sticker template in AR's sticker preview does nothing
- #68 Error while listing analyses in Analysis Request details view
- #67 Show more button is not working in Analysis Services list
- #66 TypeError in Worksheets view. TypeError: 'list' object is not callable
- #65 Fix error when an object has no status defined while listing in WS
- #64 AttributeError: 'NoneType' object has no attribute 'getInstrumentEntryOfResults
- #63 If login failed, setDepartmentCookies throws an IndexError
- #61 Show more button is not working in Worksheet's Add Analyses view
- #60 Index Error in Analysis Request Add view
- #59 AttributeError (NoneType) in service.getInstruments()
- #57 Select all departments option is not working
- #56 Client and District not sortable in Analysis Requests listing
- #52 System throwing error on opening "Verified" folder


3.2.0.1703-0f28b48 (2017-03-30)
-------------------------------

**Added**

- #39 Performance improvement. Make use of brains in Worksheets lists
- #32 Performance improvement. Catalog for analyses and make use of brains

**Fixed**

- #48 Error on AR publish. Global name 'traceback' is not defined (getServiceUsingQuery)
- #47 Error in CloneAR during retraction. AttributeError: setRequestID
- #46 Error rejecting an Analysis Request
- #45 CatalogError in Dashboard. Unknown sort_on index (created) in view.get_sections()
- #44 AttributeError in worksheets view
- #43 Sort not working on all lists
- #41 No Service found for UID None
- #40 Client Sample ID is missing in Analysis Request Add view


3.2.0.1703-1c2913e (2017-03-20)
-------------------------------

**Added**

- #33 New Analysis Request Add form outside client

**Fixed**

- #37 Publish results throwing an error
- #36 System is not printing labels automatically
- #35 Equipment interface is not working
- #34 Results import submission error


3.2.0.1703-e596f2d (2017-03-08)
-------------------------------

**Added**

- #25 Instrument import without user intervention
- #22 Date Tested range filter on lists
- #20 Added filter bar in Aggregated list of analyses
- HEALTH-364: Added country/province/district columns to client listings
- Add buttons to export lists to csv and xml formats
- Additional "printed" workflow for analysis requests once published

**Changed**

- #12 Multi-method assignment and Virtual-Real Instrument correspondence
- #11 Restrictions in manual instrument import - Instruments and interfaces
- #10 Performance improvement. Catalog for Analysis Requests and use of brains

**Fixed**

- #26 Publishing bug due to SMTP Authentication
- #24 Condition rule being affected on duplicate samples
- #23 Date of Birth: crash if date is before 1900
- #21 Rejection option does not appear if only one column in AR Add form
- #19 Inconsistent status of Analysis in WS after AR rejection
- #13 Number of verifications no longer taking effect
- HEALTH-568: TaqMan 96 interface not working well
- HEALTH-567: Nuclisens interface not working well


3.2.0.1701-26f2c4b (2017-01-17)
-------------------------------

- LIMS-2477: Reference Analysis has no dependencies; remove guard that assumes it does
- LIMS-2465: Not possible to translate Bika Listing Table Workflow Action Buttons
- LIMS-1391: Add configurable identifier types (CAS# for AnalysisService)
- LIMS-2466: Central Instrument Location Management
- LIMS-2357: Custom Landing Page and Link to switch between the Front Page and Dashboard
- LIMS-2341: Cleanup and format default Multi-AR COA
- LIMS-2455: Contact/Login Linkage Behavior
- LIMS-2456: Restrict duplicate slots in worksheet templates to routine analyses only.
- LIMS-2447: getDatePublished index not indexed correctly at time of AR publication
- LIMS-2404: AR list in batches permitted sampling without Sampler and Sampling date provided
- LIMS-2380: ARs are created in correct order (order of columns in ar-create form)
- LIMS-2394: Calculation failure in worksheets. TDS Calc misfires again.
- LIMS-2391: Use source analysis's sample ID in duplicate analysis IDs
- LIMS-2351: Field analyses without results do not prevent Samples from being received
- LIMS-2366: Workflow. AR stays in Received state with all Analyses in To be Verifie
- LIMS-2384: ARImport: Workflow state of imported ARs and their Analyses not synchronised.
- LIMS-2369: Workflow. Sampler and Date Sampled should be compulsory
- LIMS-2355: Unable to view dormant/active filters in some bika_setup pages
- LIMS-2344: Fix some UI javascript failures when viewing ARs
- LIMS-2319: AR Add: Deleting a selected CC Contact corrupts the UID of reference widgets
- LIMS-2325: Allow SampleTypes to be linked with Client Sample Points
- LIMS-2324: WS export to the LaChat Quick Chem FIA
- LIMS-2298: Add filter in Clients list
- LIMS-2299: Add ui for editing ar_count in all analysisrequest lists
- LIMS-2268: Instrument Interface. Vista Pro Simultaneous ICP, bi-directional CSV
- LIMS-2261: Cannot create analysis request
- LIMS-1562: Using a Sample Round. Basic form and printed form
- LIMS-2266: Crating partitions through Add form, doesn't create partitions.
- HEALTH-394: Sample sticker layout. 2 new sticker layouts, 2 stickers per row
- LIMS-2032: AS Methods initialise with 1st available Instrument (loading setup data)
- LIMS-2014: I can only select a Default Method for an AS if Manual results capture is on
- LIMS-2181: An analysis is not stopped from using an invalid instrument
- HEALTH-310: Implemented Nuclisens EasyQ instrument importer
- HEALTH-319: Instrument. Roche Cobas Taqman 96
- LIMS-2091: Table Column Display options Everywhere
- LIMS-2207: Indentation in analysisrequests.py
- LIMS-2208: WinescanCSVParser class instance variable misspelling
- LIMS-1832: New Results Template, COA. Multiple ARs in columns
- LIMS-2148: Unable to sort Bika Listing tables
- LIMS-1774: Shiny graphs for result ranges
- Replacement of pagination by 'Show more' in tables makes the app faster
- Add Bika LIMS TAL report reference in reports preview
- Simplify instrument interface creation for basic CSV files
- Scheduled sampling functionality added
- LIMS-2257: Scheduled sampling
- LIMS-2255: Switch to Chameleon (five.pt) for rendering TAL templates
- System-wide filter by department
- Allow to assign a lab contact to more than one department
- Multi-verification of analyses, with different verification types
- Add option to allow multi-approval (multi-verification) of results
- Added Analyses section in the Dashboard
- Add option to allow labman to self-verify analysis results
- Replacement of pagination by 'Show more' in tables makes the app faster
- Add Bika LIMS TAL report reference in reports preview
- Simplify instrument interface creation for basic CSV files


3.1.13 (2016-12-28)
-------------------

- LIMS-2299: Add ui for editing ar_count in all analysisrequest lists
- Removed commented HTML that was causing Chameleon to choke when adding ARs.


3.1.12 (2016-12-15)
-------------------

- HEALTH-569 Bar code printing not working on sample registration
- Pinned CairoSVG to 1.0.20 (support for Python 2 removed in later versions)


3.1.11 (2016-04-22)
-------------------

- LIMS-2252: Partitions not submitted when creating AR if the form is submitted before partitions are calculated
- LIMS-2223: Saving a recordswidget as hidden fails
- LIMS-2225: Formatted results not displayed properly in Worksheet's transposed layout
- LIMS-2001: Duplicate for one analysis only
- LIMS-1809: Typos. Perdiod an missing spaces
- LIMS-2221: Decimal mark doesn't work in Sci Notation
- LIMS-2219: Using a SciNotation diferent from 'aE+b / aE-b' throws an error
- LIMS-2220: Raw display of exponential notations in results manage views
- LIMS-2216: Results below LDL are not displayed in reports
- LIMS-2217: Specifications are not set in analyses on Analysis Request creation
- LIMS-2218: Result is replaced by min or max specs when "<Min" or ">Max" fields are used
- LIMS-2215: Decimal mark not working
- LIMS-2203: 'Comma' as decimal mark doesnt work
- LIMS-2212: Sampling round- Sampling round templates show all system analysis request templates
- LIMS-2209: error in manage analyises
- LIMS-1917: Inconsistencies related to significant digits in uncertainties
- LIMS-2015: Column spacing on Client look-up
- LIMS-1807: Validation for Start Date - End date relationship while creating invoices and price lists
- LIMS-1991: Sort Order for Analysis Categories and Services
- LIMS-1521: Date verified column for AR lists
- LIMS-2194: Error when submitting a result
- LIMS-2169: Cannot start instance
- WINE-125: Client users receive unauthorized when viewing some published ARs


3.1.10 (2016-01-13)
-------------------

- Updated Plone to 4.3.7
- Dashboard: replace multi-bar charts by stacked-bar charts
- LIMS-2177: template_set error when no template has been selected
- HEALTH-410: AR Create. Auto-complete Contact field if only 1
- LIMS-2175: "NaN" is shown automatically for result fields that have AS with "LDL" enabled and then an error is shown after submitting a result
- LIMS-1917: Inconsistencies related to significant digits in uncertainties
- LIMS-2143: Statements vs Invoices
- LIMS-1989: Retracting a published AR fails if one or more ASs has been retracted before publishing
- LIMS-2071: Can't generate Invoice Batch/Monthly Statements
- WINE-71: Instrument. BBK WS export to FIA fails
- WINE-72: Instrument. BBK WineScan Auto Import fails
- WINE-58: Instrument. BBK FIAStar import fails
- WINE-76: WineScan FT120 Import warnings incorrect?
- LIMS-1906: Spaces should be stripped out of the keywords coming from the Instrument
- LIMS-2117: Analysis Categories don't expand on Analysis Specification creation
- LIMS-1933: Regression: Selecting secondary AR in client batches, fails.
- LIMS-2075: Ensure hiding of pricing information when disabled in site-setup
- LIMS-2081: AR Batch Import WorkflowException after edit
- LIMS-2106: Attribute error when creating AR inside batch with no client.
- LIMS-2080: Correctly interpret default (empty) values in ARImport CSV file
- LIMS-2115: Error rises when saving a Calculation
- LIMS-2116: JSONAPI throws an UnicodeDecodeError
- LIMS-2114: AR Import with Profiles, no Analyses are created
- LIMS-2132: Reference Analyses got the same ID
- LIMS-2133: Once in a while, specs var is going empty in results reports
- LIMS-2136: Site Error on AR Verification
- LIMS-2121: Fix possible Horiba ICP csv handling errors
- LIMS-2042: Improving Horiba ICP to avoid Element Symbols as keywords
- LIMS-2123: Analysis Categories don't expand in Worksheet Templates
- LIMS-1993: Existing Sample look-up for AR Create in Batch does not work
- LIMS-2124: QR missing on sticker preview
- LIMS-2147: Add ARImport schema fields when creating ARs
- LIMS-409: ShowPrices setting was getting ignored in some contexts
- LIMS-2062: Cancelled ARs no longer appear in analysisrequest folder listings
- LIMS-2076: Cancelled batches appear in listing views
- LIMS-2154: Hide inactive ARs from BatchBook view
- LIMS-2134: Inactive services appear in AR Create
- LIMS-2139: WS Blank and Control Selection renderes whole page
- LIMS-2156: Ignore blank index values when calculating ReferenceAnalysesGroupID
- LIMS-2157: Cancelled ARs appear in AR listing inside Batches
- LIMS-2042: Horiba ICP: Missing 'DefaultResult' for imported rows
- LIMS-2030: Assign ARs in alphabetical ID order to WS
- LIMS-2167: Cannot assign a QC analysis to an invalid instrument
- LIMS-2067: Prevent initial method/instrument query for each analysis
- WINE-82: Ignore invalid entry in Sample field during AR creation
- LIMS-1717: Workflow transitions in edit context do not take effect
- WINE-111: Do not attempt formatting of 'nan' analysis result values
- WINE-114: Some users cannot view published ARs (unauthorised)
- WINE-122: Transposed worksheet layout failed while rendering empty slots
- LIMS-2149: Missing analyses can cause error accessing worksheet
- LIMS-1521: Date verified column for AR lists
- LIMS-2015: Column spacing on Client look-up
- LIMS-1807: Validation for Start Date - End Date relationship


3.1.9 (2015-10-8)
-----------------

- LIMS-2068: LIMS-2068 Urgent. Analysis Catgories don't expand
- LIMS-1875: Able to deactivate instruments and reference samples without logging in
- LIMS-2049: Displaying lists doesn't work as expected in 319
- LIMS-1908: Navigation tree order
- LIMS-1543: Add "Security Seal Intact Y/N" checkbox for partition container
- LIMS-1544: Add "File attachment" field on Sample Point
- LIMS-1949: Enviromental conditions
- LIMS-1549: Sampling Round Templates privileges and permissions
- LIMS-1564: Cancelling a Sampling Round
- LIMS-2020: Add Sampling Round - Department not available for selection
- LIMS-1545: Add "Composite Y/N" checkbox on AR Template
- LIMS-1547: AR Templates tab inside Sampling Round Template
- LIMS-1561: Editing a Sampling Round
- LIMS-1558: Creating Sampling Rounds
- LIMS-1965: Modified default navtree order for new installations
- LIMS-1987: AR Invoice tab should not be shown if pricing is toggled off
- LIMS-1523: Site Error when transitioning AR from 'Manage Analyses' or 'Log' tab
- LIMS-1970: Analyses with AR Specifications not displayed properly in AR Add form
- LIMS-1969: AR Add error when "Categorise analysis services" is disabled
- LIMS-1397: Fix Client Title accessor to prevent catalog error when data is imported
- LIMS-1996: On new system with no instrument data is difficult to get going.
- LIMS-2005: Click on Validations tab of Instruments it give error
- LIMS-1806: Instrument Interface. AQ2. Seal Analytical - Error
- LIMS-2002: Error creating Analysis Requests from batch.
- LIMS-1996: On new system with no instrument data it is difficult to get going. The warnings could be confusing
- LIMS-1312: Transposed Worksheet view, ARs in columns
- LIMS-1760: Customised AR Import spreadsheets (refactored, support importing to Batch)
- LIMS-1548: Client-specific Sampling Round Templates
- LIMS-1546: Sampling Round Template Creation and Edit view
- LIMS-1944: Prevent concurrent form submissions from clobbering each other's results
- LIMS-1930: AssertionError: Having an orphan size, higher than batch size is undefined
- LIMS-1959: Not possible to create an AR
- LIMS-1956: Error upgrading to 319
- LIMS-1934: Hyperlinks in invoices
- LIMS-1943: Stickers preview and custom stickers templates support
- LIMS-1855: Small Sticker layout. QR-code capabilities
- LIMS-1627: Pricing per Analysis Profile
- HEALTH-279: AS IDs to be near top of page. Columns in AS list
- LIMS-1625: Instrument tab titles and headers do not correspond
- LIMS-1924: Instrument tab very miss-titled. Internal Calibration Tests
- LIMS-1922: Instrument out of date typo and improvement
- HEALTH-175: Supplier does not resolve on Instrument view page
- LIMS-1887: uniquefield validator doesn't work properly
- LIMS-1869: Not possible to create an Analysis Request
- LIMS-1867: Auto-header, auto-footer and auto-pagination in results reports
- LIMS-1743: Reports: ISO (A4) or ANSI (letter) pdf report size
- LIMS-1695: Invoice export function missing
- LIMS-1812: Use asynchronous requests for expanding categories in listings
- LIMS-1811: Refactor AR Add form Javascript, and related code.
- LIMS-1818: Instrument Interface. Eltra CS-2000
- LIMS-1817: Instrument Interface. Rigaku Supermini XRF
- New System Dashboard for LabManagers and Admins


3.1.8.3 (2015-10-01)
--------------------

- LIMS-1755: PDF writer should be using a world-writeable tmp location
- LIMS-2041: Resolve ${analysis_keyword) in instrument import alert.
- LIMS-2041: Resolve translation syntax error in instrument import alert
- LIMS-1933: Secondary Sample selection in Client Batches does not locate samples


3.1.8.2 (2015-09-27)
--------------------

- LIMS-1996: On new system with no instrument data is difficult to get going.
- LIMS-1760: Customised AR Import spreadsheets (refactored, support importing to Batch)
- LIMS-1930: AssertionError: Having an orphan size, higher than batch size is undefined
- LIMS-1818: Instrument Interface. Eltra CS-2000
- LIMS-1817: Instrument Interface. Rigaku Supermini XRF
- LIMS-2037: Gracefully anticipate missing analysis workflow history
- LIMS-2035: Prevent Weasyprint flooding due to asyncronous publish


3.1.8.1 (2015-06-23)
--------------------

- LIMS-1806: Instrument Interface. AQ2. Seal Analytical - Error
- LIMS-1760: Customised AR Import spreadsheets (refactored, support importing to Batch)
- Fix portlets.xml for Plone 4.3.6 compatibility


3.1.8 (2015-06-03)
------------------

- LIMS-1923: Typo InstrumentCalibration
- HEALTH-287: Hyperlink in Instrument messages
- LIMS-1929: Translation error on Instrument Document page
- LIMS-1928 Asset Number on Instruments' Certificate tab should use Instrument's default
- LIMS-1929: Translation error on Instrument Document page
- LIMS-1773: Instrument. Thermo Fisher ELISA Spectrophotometer
- LIMS-1697: Error updating bika.lims 317 to 318 via quickinstaller
- LIMS-1820: QC Graphs DateTime's X-Axis not well sorted
- LIMS-280 : System IDs starting from a specific value
- LIMS-1819: Bika LIMS in footer, not Bika Lab Systems
- LIMS-1808: Uncertainty calculation on DL
- LIMS-1522: Site Error adding display columns to sorted AR list
- LIMS-1705: Invoices. Currency unit overcooked
- LIMS-1806: Instrument Interface. AQ2. Seal Analytical
- LIMS-1770: FIAStar import 'no header'
- LIMS-1771: Instrument. Scil Vet abc Plus
- LIMS-1772: Instrument. VetScan VS2
- LIMS-1507: Bika must notify why is not possible to publish an AR
- LIMS-1805: Instrument Interface. Horiba JY ICP
- LIMS-1710: UnicodeEncode error while creating an Invoice from AR view
- WINE-44: Sample stickers uses Partition ID only if ShowPartitions option is enabled
- LIMS-1634: AR Import fields (ClientRef, ClientSid) not importing correctly
- LIMS-1474: Disposed date is not shown in Sample View
- LIMS-1779: Results report new fields and improvements
- LIMS-1775: Allow to select LDL or UDL defaults in results with readonly mode
- LIMS-1769: Allow to use LDL and UDL in calculations.
- LIMS-1700: Lower and Upper Detection Limits (LDL/UDL). Allow manual input
- LIMS-1379: Allow manual uncertainty value input
- LIMS-1324: Allow to hide analyses in results reports
- LIMS-1754: Easy install for LIMS' add-ons was not possible
- LIMS-1741: Fixed unwanted overlay when trying to save supply order
- LIMS-1748: Error in adding supply order when a product has no price
- LIMS-1745: Retracted analyses in duplicates
- LIMS-1629: Pdf reports should split analysis results in different pages according to the lab department
- Some new ID Generator's features, as the possibility of select the separator type
- LIMS-1738: Regression. 'NoneType' object has no attribute 'getResultsRangeDict'
- LIMS-1739: Error with results interpretation field of an AR lacking departments
- LIMS-1740: Error when trying to view any Sample
- LIMS-1724: Fixed missing start and end dates on reports
- LIMS-1628: There should be a results interpretation field per lab department
- LIMS-1737: Error when adding pricelists of lab products with no volume and unit
- LIMS-1696: Decimal mark conversion is not working with "<0,002" results type
- LIMS-1729: Analysis Specification Not applying to Sample when Selected
- LIMS-1507: Do not cause exception on SMTPServerDisconnect when publishing AR results.


3.1.7 (2015-02-26)
------------------

- LIMS-1693: Error trying to save a new AR
- LIMS-1570: Instrument interface: Roche Cobas Taqman 48
- LIMS-1520: Allow to invalidate verified ARs
- LIMS-1690: Typo. Instrument page
- LIMS-1688: After AR invalidation, ARs list throws an error
- LIMS-1569: Instrument interface: Beckman Coulter Access 2
- LIMS-1689: Error while creating a new invoice batch
- LIMS-1266: Sampling date format error
- LIMS-1365: Batch search parameters on Work sheets/Work sheets insides Batches
- LIMS-1428: After receiving a sample with Sampling Workflow enable is not possible to input results
- LIMS-1540: When accent characters are used in a "Sample Type" name, it is not possible to create a new AR
- LIMS-1617: Error with bin/test
- LIMS-1571: Instrument interface: Sysmex XS-1000i
- LIMS-1574: Fixed AR and Analysis attachments
- LIMS-1670: Fixed windows incompatibility in TAL (referencewidget.pt)
- LIMS-1594: Added option to select landing page for clients in configuration registry
- LIMS-1594: Re-ordered tabs on Client home page
- LIMS-1520: Allow to invalidate verified ARs
- LIMS-1539: Printable Worksheets. In both AR by row or column orientations
- LIMS-1199: Worksheet totals in WS lists
- LIMS-257: Set Blank and Warning icons in Reference Sample main view
- LIMS-1636: Batch Sample View crash
- LIMS-1524: Invalidate email does not have variables populated
- LIMS-1572: Instrument interface: Sysmex XS-500i
- LIMS-1575: Thermo Arena 20XT
- LIMS-1423: Save details when AR workflow action kicked off
- LIMS-1624: Import default test.xlsx fails
- LIMS-1614: Error when selecting Analysis Administration Tab after receiving a sample with Sampling Workflow enabled
- LIMS-1605: Tescan TIMA interface
- LIMS-1604: BioDrop uLite interface
- LIMS-1603: Life Technologies Qubit interface
- LIMS-1517: Storage field tag untranslated?
- LIMS-1518: Storage Location table
- LIMS-1527: CC Contact on AR view (edit) offers all contacts in system
- LIMS-1536: Add button [Add], to alow quickly addings in referencewidget
- LIMS-1587: Better support for extension of custom sample labels
- LIMS-1622: Version Check does not correctly check cache
- LIMS-1623: Implement bika-frontpage as a BrowserView


3.1.6 (2014-12-17)
------------------

- LIMS-1530: Scrambled Analysis Category order in Published Results
- LIMS-1529: Error while inserting an AR with container-based partitioning is required
- LIMS-1460: Additional field in AR for comments or results interpretation
- LIMS-1441: An error message related to partitions unit is shown when selecting analysis during AR creation
- LIMS-1470: AS Setup. File attachment field tag is missing
- LIMS-1422: Results doesn't display yes/no once verified but 1 or 0
- LIMS-1486: Typos in instrument messages
- LIMS-1498: Published Results not Showing for Logged Clients
- LIMS-1445: Scientific names should be written in italics in published reports
- LIMS-1389: Units in results publishing should allow super(sub)script format, for example in cm2 or m3
- LIMS-1500: Alere Pima's Instrument Interfice
- LIMS-1457: Exponential notation in published AR pdf should be formatted like a×10^b instead of ae^+b
- LIMS-1334: Calculate result precision from Uncertainty value
- LIMS-1446: After retracting a published AR the Sample gets cancelled
- LIMS-1390: More workflow for Batches
- LIMS-1378: Bulking up Batches
- LIMS-1479: new-version and upgrade-steps should be python viewlets
- LIMS-1362: File attachment uploads to Batches
- LIMS-1404: New Batch attributes (and their integration with existing ones on Batch views)
- LIMS-1467: Sample Point Lookup doesn't work on AR modify
- LIMS-1363: Batches per Client
- LIMS-1405: New Sample and AR attributes
- LIMS-1085: Allow Clients to add Attachments to ARs
- LIMS-1444: In AR published report accredited analysis services are not marked as accredited
- LIMS-1443: In published reports the publishing date is not shown in the pdf
- LIMS-1420: Status filter is not kept after moving to next page
- LIMS-1442: Sample Type is not filtred by Sample Point
- LIMS-1448: Reports: when you click on "Analysis turnaround time" displays others
- LIMS-1440: Error when trying to publish with analysis from different categories
- LIMS-1459: Error when checking instrument validity in manage_results
- LIMS-1430: Create an AR from batch allows you to introduce a non existent Client and Contacts don't work properly
- After modifying analysis Category, reindex category name and UID for all subordinate analyses
- Setup data import improvements and fixes
- Simplify installation with a custom Plone overview and add site


3.1.5 (2014-10-06)
------------------

- LIMS-1082: Report Barcode. Was images for pdf/print reports etc
- LIMS-1159: reapply fix for samplepoint visibility
- LIMS-1325: WSTemplate loading incompatible reference analyses
- LIMS-1333: Batch label replace with standard Plone keyword widget
- LIMS-1335: Reference Definitions don't sort alphabetically on WS Template lay-outs
- LIMS-1345: Analysis profiles don't sort
- LIMS-1347: Analysis/AR background colour to be different to for Receive and To be Sampled
- LIMS-1360: Number of analyses in ARs folder view
- LIMS-1374: Auto label printing does not happen for an AR drop-down receive
- LIMS-1377: Error when trying to publish after updating branch hotfix/next or develop
- LIMS-1378: Add AR/Sample default fields to Batch
- LIMS-1395: front page issue tracker url
- LIMS-1402: If no date is chosen, it will never expire." not been accomplished
- LIMS-1416: If a sample point has a default sample type the field is not pulled automatically during AR template creation
- LIMS-1425: Verify Workflow (bika_listing) recursion
- added 'getusers' method to JSON API
- Added 'remove' method to JSON API
- Added AR 'Copy to new' action in more contexts
- Added basic handling of custom Sample Preparation Workflows
- Added decimal mark configuration for result reports
- Added help info regards to new templates creation
- Added IAcquireFieldDefaults - acquire field defaults through acquisition
- Added IATWidgetVisibility - runtime show/hide of AT edit/view widgets
- Added watermark on invalid reports
- Added watermark on provisional reports
- Alert panel when upgrades are available
- All relevant specification ranges are persisted when copying ARs or adding analyses
- Allow comma entry in numbers for e.g. German users
- Bika LIMS javascripts refactoring and optimization
- Fix ZeroDivisionError in variation calculation for DuplicateAnalysis
- Fixed spreadsheet load errors in Windows.
- Fixed template rendering errors in Windows
- JSONAPI update: always use field mutator if available
- JSONAPI: Added 'remove' and 'getusers' methods.
- Refactored ARSpecs, and added ResultsRange field to the AR


3.1.4.1 (2014-07-24)
--------------------

- 3.1.4 release was broken, simple ARs could not be created.
- LIMS-1339: Published reports should use "±" symbol instead of "+/-"
- LIMS-1327: Instrument from worksheet
- LIMS-1328: Instrument calibration test graphs do not work on multiple samples
- LIMS-1347: Analysis/AR background colour to be different to for Receive and To be Sampled
- LIMS-1353: Analyses don't sort in Attachment look-up
- Preview for Results reports
- Single/Multi-AR preview
- Allows to cancel the pre-publish/publish process
- Results reports. Allows to make visible/invisible the QC analyses
- Results reports. Allows to add new custom-made templates
- Results reports. JS machinery allowed for pdf reporting


3.1.4 (2014-07-23)
------------------

- LIMS-113: Allow percentage value for AS uncertainty
- LIMS-1087: Prevent listing of empty categories
- LIMS-1203: Fix Batch-AnalysisRequests query
- LIMS-1207: LIMS-113 Allow percentage value for AS uncertainty
- LIMS-1221: use folder icon for ARImports in nav
- LIMS-1240: fix permissions for "Copy To New" in AR lists
- LIMS-1330: handle duplicate of reference analysis
- LIMS-1340: soft-cache validator results
- LIMS-1343: Prevent sudden death if no version information is available
- LIMS-1352: SamplingWorkflow not saved to sample
- LIMS-334: Add Service/ExponentialFormatPrecision
- LIMS-334: Added ExponentialFormatThreshold setting
- LIMS-334: Allow exponential notation entry in numeric fields
- LIMS-334: Exponent Format used for analysis Result
- LIMS-334: Remove duplicate getFormattedResult code
- LIMS-83: Update Method->calculation reference version when Calculation changes
- Formula statements can be written on multiple lines for clarity.
- Replace kss-bbb ajax-spinner with a quieter one
- bika.lims.utils.log logs location url correctly


3.1.3 (2014-07-17)
------------------

- Missing fixes from 3.1.2
- LIMS-671: Preferred/Restricted client categories
- LIMS-1251: Supply order permission error
- LIMS-1272: Currency in Price Lists
- LIMS-1310: Broken AnalysisProfile selector in AR Add form.


3.1.2 (2014-07-15)
------------------

- LIMS-1292: UI fix Retracted ARs workfow: Warning msg on "full" retract.
- LIMS.1287: UI fix Report parameter formatting
- LIMS-1230: UI fix Livesearch's box
- LIMS-1257: UI fix Long titles in Analysis Profiles, Sample Points, etc.
- LIMS-1214: UI fix More columns
- LIMS-1199: UI fix Worksheet listing: better columns
- LIMS-1303: jsi18n strings must be added to bika-manual.pot.  i18ndude cannot find.
- LIMS-1310: Filter SamplePoints by client in AR Template Edit View
- LIMS-1256: Client objects included in AR-Add filters for Sample Point etc.
- LIMS-1290: Allows Analyst to retract analyses, without giving extra permissions.
- LIMS-1218: Slightly nicer monkey patch for translating content object ID's and titles.
- LIMS-1070: Accreditation text can be customised in bika_setup
- LIMS-1245: off-by-one in part indicators in ar_add
- LIMS-1240: Hide "copy to new" from Analyst users
- LIMS-1059: Added worksheet rejection workflow
- RejectAnalysis (Analysis subclass (has IAnalysis!)) workflow transition.
- Does not retract individual Analysis objects
- Sets attributes on src and dst worksheets:
- WS instance rejected worksheet attribute: .replaced_by = UID
- WS instance replacement worksheet attribute: .replaces_rejected_worksheet:UID
- Fixed some i18n and encoding snags, and updated translations.


3.1.1 (2014-06-29)
------------------

- Some bugs which only appear while running Windows, have been fixed.
- LIMS-1281: Fix Restricted and Default categories in ar_add
- LIMS-1275: Fix lax Aalyst permissions
- LIMS-1301: jsonapi can set ReferenceField=""
- LIMS-1221: Icon for ARImports folder in Navigation
- LIMS-1252: AR Published Results Signature Block formatting
- LIMS-1297: Update frontpage


3.1 (2014-06-23)
----------------

- #oduct and Analysis specifications per AR
- Incorrect published results invalidation workflow
- Improved re-testing workflow
- Adjustment factors on worksheets
- Using '< n' and '> n' results values
- Sample Storage locations
- Sample Categories
- Analysis Prioritisation
- Bulk AR creation from file
- Results reports inclusion of relevant QC results
- Supply Inventory and Orders
- JSON interface
- Management Reports export to CSV
- Enhancements to AR Batching
- Enhancements to Results Reports
- Instrument management module
- Calibration certificates, maintenance, Instrument QC
- Method, Instrument and Analysis integrity
- Instrument import interface: Agilent MS 'Masshunter Quant'
- Instrument import interface: Thermo Gallery
- Instrument import interface: Foss Winescan FT 120, Auto
- Invoices per AR, Analysis per Invoice line.
- Invoices per Supply Order, inventory item per Invoice line
- Invoices by email
- Invoice 'batches' for selected time period, ARs aand Orders per Invoice line
- Invoice batch export to accounts systems
- Price lists. Analysis Services and Supplies


3.1.3036 (2014-05-30)
---------------------

- Added two checboxes in BikaSetup > Security:
- Allow access to worksheets only to assigned analysts (Y/N)
- Only lab managers can create and amange new worksheets (Y/N)

** IMPORTANT NOTES **

The 3036 upgrade sets the above options to true by default, so after
being upgraded, only the labmanagers will be able to manage WS and the
analysts will only have access to the worksheets to which they are
assigned. These defaults can be changed in BikaSetup > Security.


3.0 (2014-03-15)
----------------

- Fix some out-dated dependencies that prevented the app from loading.
- Development of the current bika 3.0 code has slowed, and our efforts have been
  focused on the 3.01a branch for some time.


3.0rc3.5.1 (2013-10-25)
-----------------------

- Fix CSS AR Publication error
- Fix error displaying client sample views


3.0rc3.5 (2013-10-24)
---------------------

- Requires Plone 4.3.
- Fix a serious error saving Analysis results.
- Improve upgrade handling in genericsetup profile
- Fix errors in setupdata loader
- Force UTF-8 encoding of usernames (imported client contacts can now login)
- Removed outdated test setup data
- Handle duplicate request values in bika_listing
- ID server handles changes in ID schemes without error
- Remove folder-full-view from front-page view
- Updated workflow and permissions to prevent some silly errors
- Add robot tests
- Add default robots.txt


3.0rc3.2 (2013-06-28)
---------------------

- Fix site-error displaying upgraded instruments
- Fix spinner (KSS is not always enabled)
- Add extra save button in ar_add
- Label Printing: "Return to list" uses browser history
- Bold worksheet position indicators
- Remove version.txt (use only setup.py for version)


3.0rc3.1 (2013-06-27)
---------------------

- Fix permission name in upgrade step


3.0rc3 (2013-06-25)
-------------------

- Many instrument management improvements! (Merge branch 'imm')
- Removed ReferenceManufacturer (use of generic Manufacturer instead)
- Removed ReferenceSupplier (use Supplier instead)
- Improve service/calculation interim field widgets
- Allows service to include custom fields (without calculation selected)
- Fix services display table categorisation in Analysis Specification views
- Stop focusing the search gadget input when page load completes. (revert)
- Limit access to Import tab (BIKA: Manage Bika)
- New permission: "BIKA: Import Instrument Results"
- New permission: "BIKA: Manage Login Details" - edit contact login details
- Some late changes to better handle the updates to ID creation
- Plone 4.3 compatibility (incomplete)
- Use Collections as a base for Queries (incomplete)
- Many many bugfixes.


3.0rc2.3 (2013-01-29)
---------------------

- Fix bad HTML


3.0rc2.2 (2013-01-28)
---------------------

- Fix an error during AR Publish


3.0rc2.1 (2013-01-21)
---------------------

- Fix bad HTML
- Pin collective.js.jqueryui version to 1.8.16.9


3.0rc2 (2013-01-21)
-------------------

- Updated all translations and added Brazilian Portuguese
- RecordsWidget: subfield_types include "date"
- RecordsWidget: Automatic combogrid lookups
- Added all bika types to Search and Live Search
- Transition SamplePartition IDs to new format (SampleType-000?-P?
- Always handle non-ASCII characters: UTF-8 encoding everywhere
- Accept un-floatable (text) results for analyses
- Hidden InterimFields in Calculations
- Added InterimFields on AnalysisServices for overriding Calculation Interimfields.
- Disable KSS inline-validation
- Categorized analyses in AR views
- Added remarks for individual analyses
- Improved Javascript i18n handling
- Improved default permissions
- Added 'Analysis summary per department' (merge of 'Analyses lab department weekly' and 'Analyses request summary by date range'
- Added 'Analyses performed as % of total' report
- Added Analyses per lab department report
- Added 'Samples received vs. samples reported' report
- Added Daily Samples Received report
- Many many bugfixes.


3.0rc1 (2012-10-01)
-------------------

- Removed Bika Health data from released egg
- Remove remarks from portal_factory screens
- Add Month/Year selectors to default datetime widget
- ClientFolder default sorting.
- Date formats for jquery datepicker
- Don't overwrite the Title specified in @@plone-addsite
- Bug fixes


3.0rc1 (2012-09-25)
-------------------

- Requires Python 2.7 (Plone 4.2)
- Add GNUPlot dependency
- Added client sample points
- Added Sampling Deviation selections
- Added Ad-Hoc sample flag
- Added Sample Matrices (Sampletype categorisation)
- Added custom ResultsFooter field in bika setup
- Added PDF Attachments to published results
- Electronic signature included in Results and Reports
- Login details form to create users for LabContacts
- Sampling workflow is disabled by default
- Methods are versioned by default
- Methods are publicly accessible by default
- Queries WIP
- Reports WIP
- Modified label layouts for easier customisation
- Cleaned print styles
- Use plonelocales for handling Date/Time formats
- SMS and Fax setup items are disabled by default


2012-06-21
----------

- Partitioning & Preservation automation
- Reports
- Sample point & types relations in UI
- AR template enhancements
- Sample and AR layout improvements
- Labels
- Configuration logs
- Faster indexing
- JavaScript optimisation
- Better IE compatibility
- Set-up worksheet improvements
- Updated translations
- Workflow tweaks
- Tweaks to Icons, Views & Lists


2012-04-23
----------

- Optional sampling and preservation workflows and roles.
- Sample partitioning.
- AR templates - Sample point & Sample type restrictions.
- Reports - framework only. 'Analysis per service' shows what is planned.
- Improved i18n handling, and updated strings from Transifex.
- Numerous performance enhancements
- Analysis Service & Method associations.
- An improved Analysis Service pop-up window.
- Sample Type and Sample Point relationship.
- Currency selection from zope locales
- Combined AR View and Edit tabs.
- Re-factored AR 'Add/Remove Analyses' screen
- Store the date of capture for analysis results
- Append only remarks fields on more objects.


2012-01-23
----------

- Made Bika compatible with Plone 4.1
- Sampler and Preserver roles, users and permissions
- Sampling and Preservation workflows
- Inactive and Cancellation Workflows
- #e-preserved Containers
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
---------------------

- Inclusion of BikaMembers 0.0.3. No changes to bika code, version bumped to
  facilitate release of new BikaMembers version.


2.3
---

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
- Resolve client action conflicts
- Sampled date validation
- Drymatter formatting on output corrected
- Correct default none workflows
- Review portlet optimization
- #icelist prints blank for analysis service with price not defined


2.2
---

- Attachments permitted on analysis requests and analyses
- Worksheet resequencing, and sort order for worksheet analysis selection
- Worksheet deletion only available for open worksheets
- Portlet to provide export of analysis services and analysis profiles
- Requirement for unique analysis service names, analysis service keywords,
- instrument import keywords and analysis profile keywords enforced.
- Report headings and formats standardized accross different reports
- AR import alternative layout provided with selection, including profiles
- #ogress bar introduced for long running processes


2.1.1
-----

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
---

- Sample object and workflow introduced
- Results specifications, lab and per client
- Analysis profiles
- Worksheet template engine
- Interface to Bika Calendar
- Import of analysisrequests from csv file
- Export of results to csv file
- #int as publication option
- Lab Departments, lab contacts, and department manager introduced
- Quality Control calculations. Control, blank and duplicate analyses.
- QC graphs, normal distribution, trends and duplicate variation
- Various analysis calculations allowed. Described by Calculation Type
- Dependant Calcs introduced. Where an analysis result is calculated from
-  other analyses: e.g. AnalysisX = AnalysisY - Analysis Z
- Dry matter result reporting. Results are reported on sample as received,
  and also as dry matter result on dried sample
- Re-publication, Pre publication of individual results and per Client
- Many reports including Turn around, analyses repeated and out of spec


1.2.1
-----

- Removed invoice line item descriptions from core code to allow skin integration
- Create dummy titration values for analyses imported from instrument
- More language translations


1.2.0
-----

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
- Permit analysis parent (sample) to be in 'released' state.
- Reference SampleID on AnalysisRequest-
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
-----

This is a bug fix release. Migration from older versions has also been improved
greatly.

Please note that AnalysisRequest now has a custom mutator that expects the
title of the Cultivar, not the UID. This will impact anybode that customised
the *analysisrequed_add.cpy* controller script and the
*validate_analysisrequest_add_form.vpy* validation script.

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
-----

- 1423205: Show logs to labmanager set-up
- 1291750: Added default ID prefixes for Order and Statement
- 1424589: Late analysis alert to be calulated on date received


1.1.1
-----

- Updated portlets with Plone 2.1 style definition list markup
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
-----

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
-----

- Updated 'skins/bika/date_components_support.py' with latest
  version of script in Plone 2.0.5
- Modified access to transitions in workflow scripts, normal
  attribute access seems to guarded since Zope 2.7.5.
- Added CHANGES.txt and README.txt
- Added windows batch script for ID server
  (scripts/start-id-server.bat)
