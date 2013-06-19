*** Settings ***

Documentation  Worksheets - creating ARs

Library  Selenium2Library  timeout=10  implicit_wait=0.5
Library  bika.lims.tests.base.Keywords
Library  Collections
Resource  src/bika.lims/bika/lims/tests/keywords.txt



Variables  plone/app/testing/interfaces.py

#file location -> /Applications/Plone/buildout-cache/eggs/plone.app.testing-4.2.2-py2.7.egg/plone/app/testing/interfaces.py

Suite Setup      Start browser
#Suite Teardown  Close All Browsers

*** Variables ***

# higher speed variables slows process down ie 0.1, 0.3 etc in seconds
${SELENIUM_SPEED}  0

#use following to locate Analysis Service when defining an Analysis Profile
${AnalysisServices_global_Title}  Analysis Services Title
${AnalysisServices_locator}  Select ${AnalysisServices_global_Title}
${AnalysisCategory_global_Title}  Analysis Category Title
${ClientName_global}  Client Name
${Prefix_global}  PREFIX
${user-labmanager}  labmanager
${user-labmanager1}  labmanager1

#general purpose variable
${VALUE}
#general status variable
${STATUS}

${WS_SAMPLE_LIST}
${WS_CONTROL_LIST_1}
${WS_CONTROL_LIST_2}
${WS_BLANK_LIST_1}
${WS_BLANK_LIST_2}
${WS_DUPLICATE_LIST_1}
${WS_DUPLICATE_LIST_2}


*** Test Cases ***


CreateWorksheets

    #test availability ofkeywords in resource keywords.txt
    Test Keyword

    #Log in as  ${user-labmanager}
    Log in as site owner

    #LoadData

    #switch off Label Printing - loading Data turns it on
    RunBikaSetup

    SelectClientAndAddAR  Bruma
    SelectClientAndAddAR  Bore

    ReceiveCreatedARs

    #expired
    CreatReferenceSample_expired

    #reference sample
    CreatReferenceSamples_Hazardous_Metals
    #only create one - it simplifies the selection when retracting
    #CreatReferenceSamples_Benign_Metals

    #blanks
    CreatReferenceSample_D_Water

    #CreateWorksheetEntryLists

    CreateWorksheet

    #RetractAnalysis

    Hang



    #Log out as  ${user-labmanager}

    #Log in as  ${user-labmanager1}

    #Verify AR

    #Alister
    #072 872 0593


*** Keywords ***

Start browser
    Open browser  http://localhost:55001/plone/login_form
    Set selenium speed  ${SELENIUM_SPEED}


RunBikaSetup
    Go to  http://localhost:55001/plone/bika_setup/edit
    Click Link  Labels
    #Select Checkbox  SamplingWorkflowEnabled
    Select From List  AutoPrintLabels  None

    Log  BIKA Setup: label printing set to: None  WARN
    Click Button  Save
    Wait Until Page Contains  Changes saved.



LoadData
    Go to  http://localhost:55001/plone
    Wait Until Page Contains Element  portaltab-import
    Click Link  Import
    Wait Until Page Contains Element  fieldsetlegend-setupdata
    Click Link  Load Setup Data
    Wait Until Page Contains Element  existing

    Log  Setting timeout to: 300  WARN
    Set Selenium Timeout  300

    Select From List  existing  bika.lims:test
    Click Element  setupexisting
    Wait Until Page Contains  Changes saved.

    Log  Setting timeout to: 10  WARN
    Set Selenium Timeout  10


SelectClientAndAddAR
    [Arguments]  ${TemplateName}=

    Go to  http://localhost:55001/plone/clients
    sleep  0.5
    Go to  http://localhost:55001/plone/clients/client-1

    Wait Until Page Contains  Analysis Request
    Click Link  Add
    Wait Until Page Contains  Request new analyses

    #Click Element  ar_0_Batch
    #Select First From Dropdown  ar_0_Batch

    #Click Element  ar_0_Template
    #Input Text  ar_0_Template  ${TemplateName}
    #Select First From Dropdown  ar_0_Template

    SelectSpecificFromDropdown  ar_0_Template  ${TemplateName}
    SelectSpecificFromDropdown  ar_1_Template  ${TemplateName}
    #SelectSpecificFromDropdown  ar_2_Template  ${TemplateName}
    #SelectSpecificFromDropdown  ar_3_Template  ${TemplateName}
    #SelectSpecificFromDropdown  ar_4_Template  ${TemplateName}
    #SelectSpecificFromDropdown  ar_5_Template  ${TemplateName}

    #Click Element  ar_0_Profile
    #Select First From Dropdown  ar_0_Profile
    #Click Element  ar_0_Sample
    #Select First From Dropdown  ar_0_Sample

    SelectPrevMonthDate  ar_0_SamplingDate  1
    SelectPrevMonthDate  ar_1_SamplingDate  1
    #SelectPrevMonthDate  ar_2_SamplingDate  1
    #SelectPrevMonthDate  ar_3_SamplingDate  1
    #SelectPrevMonthDate  ar_4_SamplingDate  1
    #SelectPrevMonthDate  ar_5_SamplingDate  1

    #Click Element  ar_0_SampleType
    #Select First From Dropdown  ar_0_SampleType
    #Click Element  ar_0_SamplePoint
    #Select First From Dropdown  ar_0_SamplePoint
    #Click Element  ar_0_ClientOrderNumber
    #Select First From Dropdown  ar_0_ClientOrderNumber
    #Click Element  ar_0_ClientReference
    #Select First From Dropdown  ar_0_ClientReference
    #Click Element  ar_0_ClientSampleID
    #Select First From Dropdown  ar_0_ClientSampleID
    #Click Element  ar_0_SamplingDeviation
    #Select First From Dropdown  ar_0_SamplingDeviation
    #Click Element  ar_0_SampleCondition
    #Select First From Dropdown  ar_0_SampleCondition
    #Click Element  ar_0_DefaultContainerType
    #Select First From Dropdown  ar_0_DefaultContainerType

    #Select Checkbox  ar_0_AdHoc
    #Select Checkbox  ar_0_Composite
    #Select Checkbox  ar_0_ReportDryMatter
    #Select Checkbox  ar_0_InvoiceExclude

    Log  Copy accross NOT tested  WARN

    #Click Element  Batch
    #Click Element  Template
    #Click Element  Profile
    #Click Element  Sample
    #Click Element  SamplingDate
    #Click Element  SampleType
    #Click Element  SamplePoint
    #Click Element  ClientOrderNumber
    #Click Element  ClientReference
    #Click Element  ClientSampleID
    #Click Element  SamplingDeviation
    #Click Element  SampleCondition
    #Click Element  DefaultContainerType
    #Click Element  AdHoc
    #Click Element  Composite
    #Click Element  ReportDryMatter
    #Click Element  InvoiceExclude

    Click Button  Save
    Log  Setting timeout to: 60  WARN
    Set Selenium Timeout  60

    Wait Until Page Contains  successfully created.
    Log  Setting timeout to: 10  WARN
    Set Selenium Timeout  10

    #first select analysis category then service
    #Click Element  cat_lab_${AnalysisCategory_global_Title}
    #Select Checkbox  ar.0.Analyses:list:ignore_empty:record



ReceiveCreatedARs

    Select Checkbox  analysisrequests_select_all
    Click Element  receive_transition


CreatReferenceSample_expired

    Go to  http://localhost:55001/plone/bika_setup/bika_suppliers
    Wait Until Page Contains Element  deactivate_transition
    Click Link  http://localhost:55001/plone/bika_setup/bika_suppliers/supplier-1
    Wait Until Page Contains  Add
    Click Link  Add
    Wait Until Page Contains Element  title
    Input Text  title  Expired Reference Sample

    Select From List  ReferenceDefinition:list  Trace Metals 10
    Select Checkbox  Hazardous

    Select From List  ReferenceManufacturer:list  Neiss
    Input Text  CatalogueNumber  Old Numba
    Input Text  LotNumber  Finished

    Click Link  Dates
    Wait Until Page Contains Element  ExpiryDate
    Click Element  ExpiryDate
    Click Element  xpath=//a[@title='Prev']
    Click Link  1

    Click Button  Save
    Wait Until Page Contains  Changes saved.



CreatReferenceSamples_Benign_Metals

    Go to  http://localhost:55001/plone/bika_setup/bika_suppliers
    Wait Until Page Contains Element  deactivate_transition
    Click Link  http://localhost:55001/plone/bika_setup/bika_suppliers/supplier-1
    Wait Until Page Contains  Add
    Click Link  Add
    Wait Until Page Contains Element  title
    Input Text  title  Benign Metals Reference Sample

    Select From List  ReferenceDefinition:list  Trace Metals 10
    #Select Checkbox  Hazardous

    Select From List  ReferenceManufacturer:list  Neiss
    Input Text  CatalogueNumber  Numba Waan
    Input Text  LotNumber  AlotOfNumba

    Click Link  Dates
    Wait Until Page Contains Element  ExpiryDate
    Click Element  ExpiryDate
    Click Element  xpath=//a[@title='Next']
    Click Link  25

    Click Button  Save
    Wait Until Page Contains  Changes saved.


CreatReferenceSamples_Hazardous_Metals

    Go to  http://localhost:55001/plone/bika_setup/bika_suppliers
    Wait Until Page Contains Element  deactivate_transition
    Click Link  http://localhost:55001/plone/bika_setup/bika_suppliers/supplier-1
    Wait Until Page Contains  Add
    Click Link  Add
    Wait Until Page Contains Element  title
    Input Text  title  Hazardous Metals Reference Sample

    Select From List  ReferenceDefinition:list  Trace Metals 10
    Select Checkbox  Hazardous

    Select From List  ReferenceManufacturer:list  Neiss
    Input Text  CatalogueNumber  Numba Waanabe
    Input Text  LotNumber  AlotOfNumbaNe

    Click Link  Dates
    Wait Until Page Contains Element  ExpiryDate
    Click Element  ExpiryDate
    Click Element  xpath=//a[@title='Next']
    Click Link  25

    Click Button  Save
    Wait Until Page Contains  Changes saved.




CreatReferenceSample_D_Water

    Go to  http://localhost:55001/plone/bika_setup/bika_suppliers
    Wait Until Page Contains Element  deactivate_transition
    Click Link  http://localhost:55001/plone/bika_setup/bika_suppliers/supplier-2
    Wait Until Page Contains  Add
    Click Link  Add
    Wait Until Page Contains Element  title
    Input Text  title  D Water Reference Sample

    Select From List  ReferenceDefinition:list  Distilled Water
    #Select Checkbox  Hazardous

    Select From List  ReferenceManufacturer:list  Blott
    Input Text  CatalogueNumber  Numba Too
    Input Text  LotNumber  MoreLotOfNumba

    Click Link  Dates
    Wait Until Page Contains Element  ExpiryDate
    Click Element  ExpiryDate
    Click Element  xpath=//a[@title='Next']
    Click Link  25

    Click Button  Save
    Wait Until Page Contains  Changes saved.


CreateWorksheetEntryLists

    @{SampleReference} =     Create list    'a'  'b'  'c'

    log             ${SampleReference}       warn

    # print first item from array
    log             @{SampleReference}[0]    warn

    # put first item into variable
    ${first} =      set variable    @{SampleReference}[0]
    log             ${first}        warn

    #SA-13-001 to 007
    #D-13-001 to 006


CreateWorksheet
    Log  Creating Worksheets now.  WARN
    #Click Link  Worksheets
    Log  Unable to select Worksheet via NAVIGATION menu - using URL!!  WARN
    Go to  http://localhost:55001/plone/worksheets
    Wait Until Page Contains  Worksheets
    
    Select From List  xpath=//select[@class='analyst']  Lab Analyst 1
    Click Button  Add
    Wait Until Page Contains  Add Analyses

    #order AR's in list
    Click Element  xpath=//th[@id='foldercontents-getRequestID-column']
    #wait for ordering to complete
    Log  Waiting for ordering to complete  WARN
    Wait Until Page Contains Element  xpath=//th[@id='foldercontents-getRequestID-column' and @class='sortable column sort_on ascending indexed']

    Select Checkbox  xpath=//input[@alt='Select Calcium']
    Select Checkbox  xpath=//input[@alt='Select Sodium']
    Select Checkbox  xpath=//input[@alt='Select Copper']
    Select Checkbox  xpath=//input[@alt='Select Iron']
    Select Checkbox  xpath=//input[@alt='Select Magnesium']
    Select Checkbox  xpath=//input[@alt='Select Zinc']
    Select Checkbox  xpath=//input[@alt='Select Manganese']

    Click Element  assign_transition
    Wait Until Page Contains Element  submit_transition

    #check page state is open
    Page Should Contain Element  xpath=//span[@class='state-open']

    #Note: if the order in which Referencees, Duplicates and Blanks are added the further testing will fail 

    Click Link  Add Control Reference
    Wait Until Page Contains  Add Control Reference
    #this table is not sortable - only add one reference and select the first
    Click Element  xpath=//span[@id='worksheet_add_references']/form/div/table/tbody/tr[1]
    Wait Until Page Contains Element  submit_transition

    Click Link  Add Duplicate
    Wait Until Page Contains  Add Duplicate
    Click Element  xpath=//span[@id='worksheet_add_duplicate_ars']/form/div/table/tbody/tr[1]
    Wait Until Page Contains Element  submit_transition

    Click Link  Add Blank Reference
    Wait Until Page Contains  Add Blank Reference
    Click Element  xpath=//span[@id='worksheet_add_references']/form/div/table/tbody/tr[1]
    Wait Until Page Contains Element  submit_transition

    #Value range testing: badValue followed by goodValue

    #ANALYSIS
    TestResultsRange  xpath=//input[@selector='Result_Ca'][1]  0  9
    TestSampleState   xpath=//input[@selector='state_title_Cu']  Cu  Received

    TestResultsRange  xpath=//input[@selector='Result_Na'][1]  8  10
    TestSampleState   xpath=//input[@selector='state_title_Na']  Na  Received
 
    TestResultsRange  xpath=//input[@selector='Result_Cu'][1]  8  11
    TestSampleState   xpath=//input[@selector='state_title_Cu']  Cu  Received

    TestResultsRange  xpath=//input[@selector='Result_Zn'][1]  3  9.3
    TestSampleState   xpath=//input[@selector='state_title_Zn']  Zn  Received

    TestResultsRange  xpath=//input[@selector='Result_Fe'][1]  25  10.5
    TestSampleState   xpath=//input[@selector='state_title_Fe']  Fe  Received

    TestResultsRange  xpath=//input[@selector='Result_Mg'][1]  13  9.5
    TestSampleState   xpath=//input[@selector='state_title_Mg']  Mg  Received

    TestResultsRange  xpath=//input[@selector='Result_Mn'][1]  7  9.8
    TestSampleState   xpath=//input[@selector='state_title_Mn']  Mn  Received

    #REFERENCE
    #Copper: Result_SA-13-002
    TestResultsRange  xpath=//input[@selector='Result_SA-13-002'][1]  17  10.1
    TestSampleState   xpath=//input[@selector='state_title_SA-13-002']  SA-13-002  Assigned
    #Sodium: Result_SA-13-006
    TestResultsRange  xpath=//input[@selector='Result_SA-13-006'][1]  2  9.2
    TestSampleState   xpath=//input[@selector='state_title_SA-13-006']  SA-13-006  Assigned

    #from here onwards no error images no more  !!!!!!!
    #DUPLICATES
    #Iron: Result_D-13-001
    #TestResultsRange  xpath=//input[@selector='Result_D-13-001'][1]  22  10.9
    #Copper: Result_D-13-003
    #TestResultsRange  xpath=//input[@selector='Result_D-13-003'][1]  15  10.2

    Log  Not testing Duplicate range values - no images  WARN
    Log  Hope the first entry is not incidently selected  WARN

    #interim hack
    Input Text  xpath=//input[@selector='Result_D-13-001'][1]  10
    TestSampleState   xpath=//input[@selector='state_title_D-13-001']  D-13-001  Assigned
    #Input Text  xpath=//input[@selector='Result_D-13-002'][1]  10
    #TestSampleState   xpath=//input[@selector='state_title_D-13-002']  D-13-002  Assigned
    Input Text  xpath=//input[@selector='Result_D-13-003'][1]  10
    TestSampleState   xpath=//input[@selector='state_title_D-13-003']  D-13-003  Assigned
    #Input Text  xpath=//input[@selector='Result_D-13-004'][1]  10
    #TestSampleState   xpath=//input[@selector='state_title_D-13-004']  D-13-004  Assigned
    #Input Text  xpath=//input[@selector='Result_D-13-005'][1]  10
    #TestSampleState   xpath=//input[@selector='state_title_D-13-005']  D-13-005  Assigned
    #Input Text  xpath=//input[@selector='Result_D-13-006'][1]  10
    #TestSampleState   xpath=//input[@selector='state_title_D-13-006']  D-13-006  Assigned
    #Input Text  xpath=//input[@selector='Result_D-13-007'][1]  10
    #TestSampleState   xpath=//input[@selector='state_title_D-13-007']  D-13-007  Assigned

    #click mouse out of input fields
    Click Element  xpath=//div[@id='content-core']

    #BLANKS (array selection range 8 to 14)
    TestResultsRange  xpath=//input[@selector='Result_SA-13-009'][1]  2  0
    TestSampleState   xpath=//input[@selector='state_title_SA-13-009']  SA-13-009  Assigned
    TestResultsRange  xpath=//input[@selector='Result_SA-13-013'][1]  20  0
    TestSampleState   xpath=//input[@selector='state_title_SA-13-013']  SA-13-013  Assigned

    #click mouse out of input fields
    Click Element  xpath=//div[@id='content-core']

    Click Element  submit_transition
    Wait Until Page Contains  Changes saved.

    #check page stte is still open
    Page Should Contain Element  xpath=//span[@class='state-open']

    #all entries with results should have a state: to be verified

    TestSampleState   xpath=//input[@selector='state_title_Ca']  Ca  To be verified
    TestSampleState   xpath=//input[@selector='state_title_Na']  Na  To be verified
    TestSampleState   xpath=//input[@selector='state_title_Cu']  Cu  To be verified
    TestSampleState   xpath=//input[@selector='state_title_Zn']  Zn  To be verified
    TestSampleState   xpath=//input[@selector='state_title_Fe']  Fe  To be verified
    TestSampleState   xpath=//input[@selector='state_title_Mg']  Mg  To be verified
    TestSampleState   xpath=//input[@selector='state_title_Mn']  Mn  To be verified

    TestSampleState   xpath=//input[@selector='state_title_SA-13-002']  SA-13-002  To be verified
    TestSampleState   xpath=//input[@selector='state_title_SA-13-006']  SA-13-006  To be verified

    TestSampleState   xpath=//input[@selector='state_title_D-13-001']  D-13-001  To be verified
    TestSampleState   xpath=//input[@selector='state_title_D-13-003']  D-13-003  To be verified

    TestSampleState   xpath=//input[@selector='state_title_SA-13-009']  SA-13-009  To be verified
    TestSampleState   xpath=//input[@selector='state_title_SA-13-013']  SA-13-013  To be verified


    #now fill in the remaining results

    #REFERENCE
    #Calcium: Result_SA-13-001
    TestResultsRange  xpath=//input[@selector='Result_SA-13-001'][1]  3  10
    TestSampleState   xpath=//input[@selector='state_title_SA-13-001']  SA-13-001  Assigned
    #Iron: Result_SA-13-003
    TestResultsRange  xpath=//input[@selector='Result_SA-13-003'][1]  3  10
    TestSampleState   xpath=//input[@selector='state_title_SA-13-003']  SA-13-003  Assigned
    #Magnesium: Result_SA-13-004
    TestResultsRange  xpath=//input[@selector='Result_SA-13-004'][1]  3  10
    TestSampleState   xpath=//input[@selector='state_title_SA-13-004']  SA-13-004  Assigned
    #Manganese: Result_SA-13-005
    TestResultsRange  xpath=//input[@selector='Result_SA-13-005'][1]  3  10
    TestSampleState   xpath=//input[@selector='state_title_SA-13-005']  SA-13-005  Assigned
    #Zink: Result_SA-13-007
    TestResultsRange  xpath=//input[@selector='Result_SA-13-007'][1]  3  10
    TestSampleState   xpath=//input[@selector='state_title_SA-13-007']  SA-13-007  Assigned


    #DUPLICATES
    #interim hack

    Input Text  xpath=//input[@selector='Result_D-13-005'][1]  10
    TestSampleState   xpath=//input[@selector='state_title_D-13-005']  D-13-005  Assigned
    Input Text  xpath=//input[@selector='Result_D-13-006'][1]  10
    TestSampleState   xpath=//input[@selector='state_title_D-13-006']  D-13-006  Assigned
    Input Text  xpath=//input[@selector='Result_D-13-002'][1]  10
    TestSampleState   xpath=//input[@selector='state_title_D-13-002']  D-13-002  Assigned
    Input Text  xpath=//input[@selector='Result_D-13-004'][1]  10
    TestSampleState   xpath=//input[@selector='state_title_D-13-004']  D-13-004  Assigned
    Input Text  xpath=//input[@selector='Result_D-13-007'][1]  10
    TestSampleState   xpath=//input[@selector='state_title_D-13-007']  D-13-007  Assigned


    #BLANKS
    TestResultsRange  xpath=//input[@selector='Result_SA-13-008'][1]  12  0
    TestSampleState   xpath=//input[@selector='state_title_SA-13-008']  SA-13-008  Assigned

    TestResultsRange  xpath=//input[@selector='Result_SA-13-010'][1]  40  0
    TestSampleState   xpath=//input[@selector='state_title_SA-13-010']  SA-13-010  Assigned

    TestResultsRange  xpath=//input[@selector='Result_SA-13-011'][1]  20  0
    TestSampleState   xpath=//input[@selector='state_title_SA-13-011']  SA-13-011  Assigned

    TestResultsRange  xpath=//input[@selector='Result_SA-13-012'][1]  8  0
    TestSampleState   xpath=//input[@selector='state_title_SA-13-012']  SA-13-012  Assigned

    TestResultsRange  xpath=//input[@selector='Result_SA-13-014'][1]  2  0
    TestSampleState   xpath=//input[@selector='state_title_SA-13-014']  SA-13-014  Assigned

    #click mouse out of input fields
    Click Element  xpath=//div[@id='content-core']

    Click Element  submit_transition
    Wait Until Page Contains  Changes saved.

    TestSampleState   xpath=//input[@selector='state_title_SA-13-001']  SA-13-001  To be verified
    TestSampleState   xpath=//input[@selector='state_title_SA-13-003']  SA-13-003  To be verified
    TestSampleState   xpath=//input[@selector='state_title_SA-13-004']  SA-13-004  To be verified
    TestSampleState   xpath=//input[@selector='state_title_SA-13-006']  SA-13-006  To be verified

    TestSampleState   xpath=//input[@selector='state_title_D-13-005']  D-13-005  To be verified
    TestSampleState   xpath=//input[@selector='state_title_D-13-006']  D-13-006  To be verified
    TestSampleState   xpath=//input[@selector='state_title_D-13-002']  D-13-002  To be verified
    TestSampleState   xpath=//input[@selector='state_title_D-13-004']  D-13-004  To be verified
    TestSampleState   xpath=//input[@selector='state_title_D-13-007']  D-13-007  To be verified

    TestSampleState   xpath=//input[@selector='state_title_SA-13-008']  SA-13-008  To be verified
    TestSampleState   xpath=//input[@selector='state_title_SA-13-010']  SA-13-010  To be verified
    TestSampleState   xpath=//input[@selector='state_title_SA-13-011']  SA-13-011  To be verified
    TestSampleState   xpath=//input[@selector='state_title_SA-13-012']  SA-13-012  To be verified
    TestSampleState   xpath=//input[@selector='state_title_SA-13-014']  SA-13-014  To be verified

    #check page has changed state
    Page Should Contain Element  xpath=//span[@class='state-to_be_verified']

    Log  IF YOU GET THIS FAR THE RANDOM DUPLICATE WARNING IMAGE BUG DID NOT APPEAR - RUN TEST AGAIN  WARN


RetractAnalysis
    #continue on existing page
    Log  ...testing Retracting  WARN


    #selector="H2O13-0001-R01_Mg
    #selector="QC-13-002_SA-13-004 and sometimes selector="QC-13-003_SA-13-004
    #selector="WS-13-001_D-13-002

    #WS-13-001

    #get page header
    ${VALUE}  Get Text  xpath=//div[@id='content']/h1/span
    #Log  Text Header: ${VALUE}  WARN

    Log  Retracting analysis: H2O13-0001-R01_Mg  WARN
    Select Checkbox  xpath=//input[@selector='H2O13-0001-R01_Mg']

    Click Element  retract_transition
    Wait Until Page Contains  Changes saved.
    TestSampleState   xpath=//input[@selector='state_title_Mg-1']  Mg  Retracted

    #check page has changed state from 'To be verified' to 'Open'???
    Page Should Contain Element  xpath=//span[@class='state-open']

    #retract reference
    Log  Retracting reference: QC-13-002_SA-13-004  WARN
    Select Checkbox  xpath=//input[@selector='QC-13-002_SA-13-004']
    Click Element  retract_transition
    Wait Until Page Contains  Changes saved.
    TestSampleState   xpath=//input[@selector='state_title_SA-13-004']  SA-13-004  Assigned

    #check page state remains Open
    Page Should Contain Element  xpath=//span[@class='state-open']

    #retract duplicate
    Log  Retracting duplicate: WS-13-001_D-13-002  WARN
    Select Checkbox  xpath=//input[@selector='WS-13-001_D-13-002']
    Click Element  retract_transition
    Wait Until Page Contains  Changes saved.
    TestSampleState   xpath=//input[@selector='state_title_D-13-002']  D-13-002  Assigned

    #check page remains Open
    Page Should Contain Element  xpath=//span[@class='state-open']

    Log  Re-assigning Analysis, Reference and Duplicates etc.  WARN
    TestResultsRange  xpath=//input[@selector='Result_Mg'][1]  13  9.5
    TestSampleState   xpath=//input[@selector='state_title_Mg']  Mg  Received

    TestResultsRange  xpath=//input[@selector='Result_SA-13-004'][1]  3  10
    TestSampleState   xpath=//input[@selector='state_title_SA-13-004']  SA-13-004  Assigned

    Input Text  xpath=//input[@selector='Result_D-13-002'][1]  10
    #click mouse out of input fields - remember direct text input is still a temp hack due to missing images
    Click Element  xpath=//div[@id='content-core']
    TestSampleState   xpath=//input[@selector='state_title_D-13-002']  D-13-002  Assigned

    Click Element  submit_transition
    Wait Until Page Contains  Changes saved.

    TestSampleState   xpath=//input[@selector='state_title_Mg']  Mg  To be verified
    TestSampleState   xpath=//input[@selector='state_title_SA-13-004']  SA-13-004  To be verified
    TestSampleState   xpath=//input[@selector='state_title_D-13-002']  D-13-002  To be verified

    check page has changed state
    Page Should Contain Element  xpath=//span[@class='state-to_be_verified']

#remove item
#unassign_transition

TestResultsRange
    [Arguments]  ${element}=
    ...          ${badResult}=
    ...          ${goodResult}=

    Log  Testing Result Range for ${element} -:- values: ${badResult} and ${goodResult}  WARN
    Input Text  ${element}  ${badResult}
    #pres the tab key to move out the field
    Press Key  ${element}  \t
    #Warning img -> http://localhost:55001/plone/++resource++bika.lims.images/warning.png
    sleep  0.5
    Page Should Contain Image  http://localhost:55001/plone/++resource++bika.lims.images/exclamation.png
    Input Text  ${element}  ${goodResult}
    Press Key  ${element}  \t
    sleep  0.5
    Page Should Not Contain Image  http://localhost:55001/plone/++resource++bika.lims.images/exclamation.png



TestSampleState
    [Arguments]  ${element}=
    ...          ${sample}=
    ...          ${expectedState}=

    ${VALUE}  Get Value  ${element}
    Should Be Equal  ${VALUE}  ${expectedState}  ${sample} Workflow States incorrect: Expected: ${expectedState} -
    Log  Testing Sample State for ${sample}: ${expectedState} -:- ${VALUE}  WARN


SelectSpecificFromDropdown
    [Arguments]  ${Element}=
    ...          ${Option}=

    Click Element  ${Element}
    Input Text  ${Element}  ${Option}
    Select First From Dropdown  ${Element}

SelectDate
    [Arguments]  ${Element}=
    ...          ${Date}=

    Click Element  ${Element}
    Click Link  ${Date}

SelectPrevMonthDate
    [Arguments]  ${Element}=
    ...          ${Date}=

    Click Element        ${Element}
    sleep                0.5
    #Click Element        xpath=//a[@title='Prev']  
    Click Element        xpath=//div[@id='ui-datepicker-div']/div/a[@title='Prev']
    sleep                0.5
    #Click Link          ${Date}
    Click Link           xpath=//div[@id='ui-datepicker-div']/table/tbody/tr/td/a[contains (text(),'${Date}')]


#div[@id='ui-datepicker-div']/div/a[@title='Prev']
#div[@id='ui-datepicker-div']/div/a[@title='Next']
#div[@id='ui-datepicker-div']/table/tbody/tr/td[@a='1']

SelectNextMonthDate
    [Arguments]  ${Element}=
    ...          ${Date}=

    Click Element        ${Element}
    sleep                0.5
    Click Element        xpath=//a[@title='Next']
    sleep                0.5
    Click Link           ${Date}



Hang
    sleep  600
    Log  Hang Timeout Expired  WARN

#add blank
#add control reference
#add duplicate


    ###################









Create SampleTypes
    [Arguments]  ${Title}=
    ...          ${Description}=
    ...          ${Days}=
    ...          ${Hours}=
    ...          ${Minutes}=

    Go to  http://localhost:55001/plone/bika_setup/bika_sampletypes

    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}

    Input Text  RetentionPeriod.days:record:ignore_empty  ${Days}
    Input Text  RetentionPeriod.hours:record:ignore_empty  ${Hours}
    Input Text  RetentionPeriod.minutes:record:ignore_empty  ${Minutes}

    Select Checkbox  Hazardous

    #Click Element  SampleMatrix:list
    Select from list  SampleMatrix:list

    Input Text  Prefix  ${Prefix_global}
    Input Text  MinimumVolume  20 ml

    #Click Element  ContainerType:list
    Select from list  ContainerType:list
    Click Button  Save
    Wait Until Page Contains  Changes saved.
 

Create LabDepartment
    [Arguments]  ${Title}=
    ...          ${Description}=

    Go to  http://localhost:55001/plone/bika_setup/bika_departments
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${Title}
    Input Text  description  ${Description}
    #Select from list  Manager:list  ${Manager}
    Click Button  Save
    Page should contain  Changes saved.

Create AnalysisCategories
    [Arguments]  ${Description}=

    Go to  http://localhost:55001/plone/bika_setup/bika_analysiscategories
    Wait Until Page Contains  Analysis Categories
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${AnalysisCategory_global_Title}
    Input Text  description  ${Description}
    Select From List  Department:list

    Click Button  Save
    Page should contain  Changes saved.

Create AnalysisServices
    [Arguments]  ${Description}=

    Go to  http://localhost:55001/plone/bika_setup/bika_analysisservices
    Wait Until Page Contains  Analysis Services
    Click link  Add
    Wait Until Page Contains Element  title
    Input Text  title  ${AnalysisServices_global_Title}
    Input Text  description  ${Description}
    Input Text  Unit  measurement Unit
    Input Text  Keyword  AnalysisKeyword

    Log  AS: Lab Sample selected  WARN

    Select Radio Button  PointOfCapture  lab
    #Select Radio Button  PointOfCapture  field

    Click Element  Category
    #if you know the category name, another option is to:
    #Input Text  Category  Analysis
    Select First From Dropdown  Category

    Input Text  Price  50.23
    Input Text  BulkPrice  30.00
    Input Text  VAT  15.00
    Click Element  Department
    #Input Text  Department  Lab
    Select First From Dropdown  Department

    #sleep  2
    #Click Button  Save

    #now move on to Analysis without saving
    Click link  Analysis
    Wait Until Page Contains Element  Precision
    Input Text  Precision  3
    Select Checkbox  ReportDryMatter
    Select From List  AttachmentOption  n
    Input Text  MaxTimeAllowed.days:record:ignore_empty  3
    Input Text  MaxTimeAllowed.hours:record:ignore_empty  3
    Input Text  MaxTimeAllowed.minutes:record:ignore_empty  3
    #sleep  2
    #Click Button  Save

    #now move on to Analysis without saving
    Click link  Method
    Wait Until Page Contains Element  Instrument
    Click Element  Method
    #following because in small test files this info is not available
    Select First From Dropdown  Method
    Click Element  Instrument
    Select First From Dropdown  Instrument
    Click Element  Calculation
    Select First From Dropdown  Calculation

    Input Text  InterimFields-keyword-0  Keyword
    Input Text  InterimFields-title-0  Field Title
    Input Text  InterimFields-value-0  Default Value
    Input Text  InterimFields-unit-0  Unit

    Select Checkbox  InterimFields-hidden-0

    Input Text  DuplicateVariation  5
    Select Checkbox  Accredited

    #sleep  2
    #Click Button  Save

    #now move on to Uncertainties without saving
    Click link  Uncertainties

    Input Text  Uncertainties-intercept_min-0  2
    Input Text  Uncertainties-intercept_max-0  9
    Input Text  Uncertainties-errorvalue-0  3.8

    Click Button  Uncertainties_more
    Input Text  Uncertainties-intercept_min-1  0
    Input Text  Uncertainties-intercept_max-1  10
    Input Text  Uncertainties-errorvalue-1  5.5

    #sleep  2
    #Click Button  Save

    #now move on to Result Options without saving
    Click link  Result Options

    Input Text  ResultOptions-ResultValue-0  10
    Input Text  ResultOptions-ResultText-0  Result Text 0
    Click Button  ResultOptions_more
    Input Text  ResultOptions-ResultValue-1  2
    Input Text  ResultOptions-ResultText-1  Result Text 1

    #sleep  2
    #Click Button  Save


    Log  AnalysisServices: Preservation fields NOT selected for DEBUG  WARN
    #Log  AnalysisServices: Preservation fields ARE selected  WARN    

    #now move on to Container and Preservation without saving
    Click link  Container and Preservation
    Wait Until Page Contains Element  Preservation
    #Select Checkbox  Separate

    #Click Element  Preservation
    #Select First From Dropdown  Preservation

    #Click Element  Container
    #Select First From Dropdown  Container

    #Select From List  PartitionSetup-sampletype-0

    #Click Element  PartitionSetup-separate-0

    #Select From List  PartitionSetup-preservation-0

    #Select From List  PartitionSetup-container-0

    #Input Text  PartitionSetup-vol-0  Volume 123

    #sleep  2

    Click Button  Save
    Wait Until Page Contains  Changes saved.



#Clients
Create AddClients
    [Arguments]  ${ID}=
    ...          ${Country}=
    ...          ${State}=
    ...          ${City}=
    ...          ${ZIP}=
    ...          ${Physical Address}=
    ...          ${Postal Address}=


    Go to  http://localhost:55001/plone/clients
    Wait Until Page Contains  Clients
    Click link  Add
    Wait Until Page Contains Element  Name

    Input Text  Name  ${ClientName_global}
    Input Text  ClientID  ${ID}
    Input Text  TaxNumber  98765A
    Input Text  Phone  011 3245679
    Input Text  Fax  011 3245678
    Input Text  EmailAddress  client@client.com

    Select Checkbox  BulkDiscount
    Select Checkbox  MemberDiscountApplies

    Click link  Address
    Wait Until Page Contains Element  PhysicalAddress.country
    Select From List  PhysicalAddress.country:record  ${Country}
    Select From List  PhysicalAddress.state:record  ${State}
    #district is on autoselect last entry
    Select From List  PhysicalAddress.district:record
    Input Text  PhysicalAddress.city  ${City}
    Input Text  PhysicalAddress.zip  ${ZIP}
    Input Text  PhysicalAddress.address  ${Physical Address}
    Select From List  PostalAddress.selection  PhysicalAddress
    Input Text  PostalAddress.address  ${Postal Address}
    Select From List  BillingAddress.selection  PostalAddress
    Input Text  BillingAddress.address  ${Postal Address}

    Click link  Bank details
    Input Text  AccountType  Account Type
    Input Text  AccountName  Account Name
    Input Text  AccountNumber  Account Number
    Input Text  BankName  Bank Name
    Input Text  BankBranch  Bank Branch

    #Select Preferences link like this to avoid Admin Preferences confusion
    Click link  fieldsetlegend-preferences

    Select From List  EmailSubject:list
    #Select From List  DefaultCategories:list
    #Select From List  RestrictedCategories:list

    Click Button  Save
    Page should contain  Changes saved.


#Client contact required before request may be submitted


#Contacts
Create ClientContact
    [Arguments]  ${Salutation}=
    ...          ${Firstname}=
    ...          ${Middleinitial}=
    ...          ${Middlename}=
    ...          ${Surname}=
    ...          ${Jobtitle}=
    ...          ${Department}=
    ...          ${Email}=
    ...          ${Businessphone}=
    ...          ${Businessfax}=
    ...          ${Homephone}=
    ...          ${Mobilephone}=
    ...          ${Country}=
    ...          ${State}=
    ...          ${City}=
    ...          ${ZIP}=
    ...          ${Physical Address}=
    ...          ${Postal Address}=
    ...          ${Preference}=

    Go to  http://localhost:55001/plone/clients
    sleep  1

    Click link  ${ClientName_global}
    Click link  Contacts
    Click link  Add

    Wait Until Page Contains Element  Firstname
    Input Text  Salutation  ${Salutation}
    Input Text  Firstname  ${Firstname}
    Input Text  Middleinitial  ${Middleinitial}
    Input Text  Middlename  ${Middlename}
    Input Text  Surname  ${Surname}
    Input Text  JobTitle  ${Jobtitle}    
    Input Text  Department  ${Department}

    Click Link  Email Telephone Fax
    Wait Until Page Contains Element  EmailAddress
    Input Text  EmailAddress  ${Email}
    Input Text  BusinessPhone  ${Businessphone}
    Input Text  BusinessFax  ${Businessfax}
    Input Text  HomePhone  ${Homephone}
    Input Text  MobilePhone  ${Mobilephone}

    Click Link  Address
    Wait Until Page Contains Element  PhysicalAddress.country
    Select From List  PhysicalAddress.country:record  ${Country}
    Select From List  PhysicalAddress.state:record  ${State}
    #district is on autoselect last entry
    Select From List  PhysicalAddress.district:record
    Input Text  PhysicalAddress.city  ${City}
    Input Text  PhysicalAddress.zip  ${ZIP}
    Input Text  PhysicalAddress.address  ${Physical Address}
    Select From List  PostalAddress.selection  PhysicalAddress
    Input Text  PostalAddress.address  ${Postal Address}

    Click Link  Publication preference
    Wait Until Page Contains Element  PublicationPreference
    Select from list  PublicationPreference:list  ${Preference}
    Select Checkbox  AttachmentsPermitted

    Log  What does archetypes-fieldname-CCContact field do??  WARN

#what is this supposed to do??
#add more clients
    #Click Element  archetypes-fieldname-CCContact

    Click Button  Save
    Page should contain  Changes saved.


#end LabContact

    #now continue with AR

    Go to  http://localhost:55001/plone/clients
    Wait Until Page Contains  Clients
    Click Link  ${ClientName_global}
    Wait Until Page Contains  Analysis Request
    Click Link  Add
    Wait Until Page Contains  Request new analyses

    Click Element  ar_0_Batch
    Select First From Dropdown  ar_0_Batch
    Click Element  ar_0_Template
    Select First From Dropdown  ar_0_Template
    Click Element  ar_0_Profile
    Select First From Dropdown  ar_0_Profile
    Click Element  ar_0_Sample
    Select First From Dropdown  ar_0_Sample
    Click Element  ar_0_SamplingDate
    Click link  1
    Click Element  ar_0_SampleType
    Select First From Dropdown  ar_0_SampleType
    Click Element  ar_0_SamplePoint
    Select First From Dropdown  ar_0_SamplePoint
    Click Element  ar_0_ClientOrderNumber
    Select First From Dropdown  ar_0_ClientOrderNumber
    Click Element  ar_0_ClientReference
    Select First From Dropdown  ar_0_ClientReference
    Click Element  ar_0_ClientSampleID
    Select First From Dropdown  ar_0_ClientSampleID
    Click Element  ar_0_SamplingDeviation
    Select First From Dropdown  ar_0_SamplingDeviation
    Click Element  ar_0_SampleCondition
    Select First From Dropdown  ar_0_SampleCondition
    Click Element  ar_0_DefaultContainerType
    Select First From Dropdown  ar_0_DefaultContainerType

    Select Checkbox  ar_0_AdHoc
    Select Checkbox  ar_0_Composite
    Select Checkbox  ar_0_ReportDryMatter
    Select Checkbox  ar_0_InvoiceExclude

    Log  AR: NO Copy Across Testing  WARN
    #Log  AR: Copy Across Testing  WARN

    Click Element  Batch
    Click Element  Template
    Click Element  Profile
    Click Element  Sample
    Click Element  SamplingDate
    Click Element  SampleType
    Click Element  SamplePoint
    Click Element  ClientOrderNumber
    Click Element  ClientReference
    Click Element  ClientSampleID
    Click Element  SamplingDeviation
    Click Element  SampleCondition
    Click Element  DefaultContainerType
    Click Element  AdHoc
    Click Element  Composite
    Click Element  ReportDryMatter
    Click Element  InvoiceExclude

    #first select analysis category then service
    Click Element  cat_lab_${AnalysisCategory_global_Title}
    Select Checkbox  ar.0.Analyses:list:ignore_empty:record

    Click Button  Save
    Wait Until Page Contains  was successfully created.

    #this selects the actual AR detail - that wil be a later test
    #Click Link  ${Prefix_global}-0001-R01

    #just select the AR checkbox
    Select Checkbox  xpath=//input[@alt='Select ${Prefix_global}-0001-R01']

    #test for Workflow State Change
    ${VALUE}  Get Value  xpath=//input[@selector='state_title_${Prefix_global}-0001-R01']
    #Log  VALUE = ${VALUE}  WARN

    Should Be Equal  ${VALUE}  Sample Due  Workflow States incorrect: Expected: Sample Due -

    Click Element  receive_transition
    Wait Until Page Contains  Changes saved.

    ${VALUE}  Get Value  xpath=//input[@selector='state_title_${Prefix_global}-0001-R01']
    Should Be Equal  ${VALUE}  Received  Workflow States incorrect: Expected: Received -  
    Click Link  ${Prefix_global}-0001-R01
    Wait Until Page Contains  ${Prefix_global}-0001-R01

    Select From List  xpath=//select[@selector='Result_AnalysisKeyword']

    Click Element  submit_transition
    Page should contain  Changes saved.



Verify AR

    Click Link  to_be_verified_${Prefix_global}-0001-R01

    Wait Until Page Contains Element  xpath=//a[@title='Change the state of this item']/span[@class='state-to_be_verified']

    Element Should Contain  xpath=//a[@title='Change the state of this item']/span[@class='state-to_be_verified']  To be verified

    Click Link  xpath=//a[@title='Change the state of this item']
    Wait Until Page Contains Element  workflow-transition-verify
    Click Link  workflow-transition-verify

    Wait Until Page Contains Element  xpath=//a[@title='Change the state of this item']/span[@class='state-verified']
    Element Should Contain  xpath=//a[@title='Change the state of this item']/span[@class='state-verified']  Verified

    Click Link  xpath=//a[@title='Change the state of this item']
    Wait Until Page Contains Element  workflow-transition-publish
    #Click Link  workflow-transition-publish
    Log  Publish NOT clicked - no way of testing result  WARN


Select First Option in Dropdown
    #sleep  0.5
    #Click Element  xpath=//div[contains(@class,'cg-DivItem')]
    Select First From Dropdown  UNKNOWN

Select First From Dropdown
    [Arguments]  ${elementName}
    sleep  0.5
    #select the first item in the dropdown and return status
    ${STATUS}  Run Keyword And Return Status  Click Element  xpath=//div[contains(@class,'cg-DivItem')]
    #if no content in dropdown output warning and continue
    Run Keyword If  '${STATUS}' == 'False'  Log  No items found in dropdown: ${elementName}  WARN


Log in
    [Arguments]  ${userid}  ${password}

    Go to  http://localhost:55001/plone/login_form
    Page should contain element  __ac_name
    Page should contain element  __ac_password
    Page should contain button  Log in
    Input text  __ac_name  ${userid}
    Input text  __ac_password  ${password}
    Click Button  Log in

Log in as
    [Arguments]  ${user}
    Log in  test_${user}  test_${user}

Log in as test user
    Log in  ${TEST_USER_NAME}  ${TEST_USER_PASSWORD}

Log in as site owner
    Log in  ${SITE_OWNER_NAME}  ${SITE_OWNER_PASSWORD}

Log in as test user with role
    [Arguments]  ${usrid}  ${role}

Log out as
    [Arguments]  ${user}=

    Click Link  test_${user}
    sleep  0.5
    Click Link  Log out
    Log  User ${user} logging out!  WARN
    Wait Until Page Contains  Log in


Log out
    Go to  http://localhost:55001/plone/logout
    Page should contain  logged out



#stuff hereafter

    #xpath examples
    #Click Element  xpath=//th[@cat='${AnalysisCategory_global_Title}']
    #Select Checkbox  xpath=//input[@alt='${AnalysisServices_locator}']

            

