*** Settings ***

Documentation  Worksheets - creating ARs

Library                 Selenium2Library  timeout=10  implicit_wait=0
Library                 bika.lims.tests.base.Keywords
Library                 Collections
Resource                keywords.txt
Variables               plone/app/testing/interfaces.py
Suite Setup             Start browser
## Suite Teardown         Close All Browsers

*** Variables ***

${SELENIUM_SPEED}       0

*** Test Cases ***

Create Worksheets
    Log in              test_labmanager  test_labmanager

    Add ARs

    Create Expired Reference Sample
    Create Benign Metals Reference Sample
    Create Hazardous Metals Reference Sample
    Create Distilled Water Reference Sample

    Create Worksheet
    Add worksheet control
    Add worksheet blank
    Add worksheet duplicate
    Check worksheet state       open

    ## Value range testing: badValue followed by goodValue

    ## ANALYSES
    TestResultsRange    Result_Ca       0   9
    TestSampleState     state_title_Ca  Ca  Received
    ## CONTROL
    TestResultsRange    Result_SA-001       17  10.1
    TestSampleState     state_title_SA-001  SA-001(Control Calcium)  Assigned
    ## DUPLICATE
    TestResultsRange    Result_D-001        8   8.1
    TestResultsRange    Result_D-001        10  9.9
    TestSampleState     state_title_D-001   D-001(Dup Calcium)  Assigned
    ## BLANK
    TestResultsRange    Result_SA-003       2  0
    TestSampleState     state_title_SA-003  SA-003(Blank Calcium)  Assigned

    Click Element  submit_transition
    Wait Until Page Contains  Changes saved.

    Check worksheet state       open

    #all entries with results should have a state: to be verified
    TestSampleState     state_title_Ca      Ca(Normal Calcium)       To be verified
    TestSampleState     state_title_SA-001  SA-001(Control Calcium)  To be verified
    TestSampleState     state_title_D-001   D-001(Dup Calcium)       To be verified
    TestSampleState     state_title_SA-003  SA-003(Blank Calcium)    To be verified

    #now fill in the remaining results

    ## ANALYSES
    TestResultsRange    Result_Mg       13  9.5
    TestSampleState     state_title_Mg  Mg  Received
    ## CONTROL
    TestResultsRange    Result_SA-002       2  9.2
    TestSampleState     state_title_SA-002  SA-002(Control Magnesium)  Assigned
    ## DUPLICATE
    TestResultsRange    Result_D-002        8.54   8.55
    TestResultsRange    Result_D-002        10.46  10.45
    TestSampleState     state_title_D-002   D-002(Dup Magnesium)  Assigned
    ## BLANK
    TestResultsRange    Result_SA-004       20  0
    TestSampleState     state_title_SA-004  SA-004(Blank Magnesium)  Assigned

    #all entries with results should have a state: to be verified
    TestSampleState     state_title_Ca      Ca(Normal Calcium)       To be verified
    TestSampleState     state_title_SA-001  SA-001(Control Calcium)  To be verified
    TestSampleState     state_title_D-001   D-001(Dup Calcium)       To be verified
    TestSampleState     state_title_SA-003  SA-003(Blank Calcium)    To be verified

    Click Element  submit_transition
    Wait Until Page Contains  Changes saved.

    Check worksheet state       to_be_verified


    #RetractAnalysis

    Hang


*** Keywords ***

Start browser
    Open browser  http://localhost:55001/plone/login_form
    Set selenium speed  ${SELENIUM_SPEED}


Add ARs
    [Documentation]     Add and receive some ARs.
    ...                 H2O-0001-R01  Bore
    ...                 H2O-0002-R01  Bore

    @{time} =           Get Time        year month day hour min sec
    Go to               http://localhost:55001/plone/clients/client-1
    Wait until page contains element    css=body.portaltype-client
    Click Link                  Add
    Wait until page contains    Request new analyses
    Select from dropdown        ar_0_Template               Bore
    Select from dropdown        ar_1_Template               Bore
#    Select from dropdown        ar_2_Template               Bruma
#    Select from dropdown        ar_3_Template               Bruma
    Select from datepicker      ar_0_SamplingDate           @{time}[2]
    Select from datepicker      ar_1_SamplingDate           @{time}[2]
    Select from datepicker      ar_2_SamplingDate           @{time}[2]
    Select from datepicker      ar_3_SamplingDate           @{time}[2]
    Set Selenium Timeout        60
    Click Button                Save
    Wait until page contains    created
    Set Selenium Timeout        10
    Select checkbox             analysisrequests_select_all
    Click element               receive_transition
    Wait until page contains    saved


Create Expired Reference Sample
    Go to  http://localhost:55001/plone/bika_setup/bika_suppliers/supplier-1
    Wait Until Page Contains    Add
    Click Link                  Add
    Wait Until Page Contains    Add Reference Sample
    Input Text                  title                       Expired Reference Sample
    Select From List            ReferenceDefinition:list    Trace Metals 10
    Select Checkbox             Hazardous
    Select From List            ReferenceManufacturer:list  Neiss
    Input Text                  CatalogueNumber  Old Numba
    Input Text                  LotNumber  Finished
    Click Link                  Dates
    Wait Until Page Contains    Expiry Date
    SelectPrevMonthDate         ExpiryDate                  1
    Click Button                Save
    Wait Until Page Contains    Changes saved.


Create Benign Metals Reference Sample
    Go to  http://localhost:55001/plone/bika_setup/bika_suppliers/supplier-1
    Wait Until Page Contains    Add
    Click Link                  Add
    Wait Until Page Contains    Add Reference Sample
    Input Text                  title                       Benign Metals Reference Sample
    Select From List            ReferenceDefinition:list    Trace Metals 10
    Select From List            ReferenceManufacturer:list  Neiss
    Input Text                  CatalogueNumber             Numba Waan
    Input Text                  LotNumber                   AlotOfNumba
    Click Link                  Dates
    Wait Until Page Contains    Expiry Date
    SelectNextMonthDate         ExpiryDate                  25
    Click Button                Save
    Wait Until Page Contains    Changes saved.


Create Hazardous Metals Reference Sample
    Go to  http://localhost:55001/plone/bika_setup/bika_suppliers/supplier-1
    Wait Until Page Contains    Add
    Click Link                  Add
    Wait Until Page Contains    Add Reference Sample
    Input Text                  title                       Hazardous Metals Reference Sample
    Select From List            ReferenceDefinition:list    Trace Metals 10
    Select From List            ReferenceManufacturer:list  Neiss
    Select Checkbox  Hazardous
    Input Text                  CatalogueNumber             Numba Waanabe
    Input Text                  LotNumber                   AlotOfNumbaNe
    Click Link                  Dates
    Wait Until Page Contains    Expiry Date
    SelectNextMonthDate         ExpiryDate                  25
    Click Button                Save
    Wait Until Page Contains    Changes saved.


Create Distilled Water Reference Sample
    Go to  http://localhost:55001/plone/bika_setup/bika_suppliers/supplier-2
    Wait Until Page Contains    Add
    Click Link                  Add
    Wait Until Page Contains    Add Reference Sample
    Input Text                  title                       D Water Reference Sample
    Select From List            ReferenceDefinition:list    Distilled Water
    Select From List            ReferenceManufacturer:list  Blott
    Input Text                  CatalogueNumber             Numba Too
    Input Text                  LotNumber                   MoreLotOfNumba
    Click Link                  Dates
    Wait Until Page Contains    Expiry Date
    SelectNextMonthDate         ExpiryDate                  25
    Click Button                Save
    Wait Until Page Contains    Changes saved.


Create Worksheet
    [Documentation]     Add one worksheet, with all
    ...                 analyses from H2O-0001-R01 selected (Ca, Mg)
    Go to  http://localhost:55001/plone/worksheets
    Wait Until Page Contains    Mine
    Select From List            analyst          Lab Analyst 1
    Click Button                Add
    Wait Until Page Contains    Add Analyses

    ## order AR's in list
    Click Element                       css=th#foldercontents-getRequestID-column
    Wait Until Page Contains Element    css=th#foldercontents-getRequestID-column.sort_on

    Select Checkbox             xpath=//input[@selector='H2O-0001-R01_Ca']
    Select Checkbox             xpath=//input[@selector='H2O-0001-R01_Mg']

    Set Selenium Timeout        30
    Click Element               assign_transition
    Wait Until Page Contains    Manage Results
    Set Selenium Timeout        10


Check worksheet state
    [Arguments]  ${state_id}
    Go to        http://localhost:55001/plone/worksheets/WS-001
    Wait until page contains element    xpath=//span[@class='state-${state_id}']


Add worksheet control
    Go to                       http://localhost:55001/plone/worksheets/WS-001
    Click Link                  Add Control Reference
    Wait Until Page Contains    Trace Metals 10
    Click Element               xpath=//span[@id='worksheet_add_references']//tbody//tr[1]
    Wait Until Page Contains Element  submit_transition


Add worksheet blank
    Go to                       http://localhost:55001/plone/worksheets/WS-001
    Click Link                  Add Duplicate
    Wait Until Page Contains    Add Duplicate
    Click Element               xpath=//span[@id='worksheet_add_duplicate_ars']//tbody//tr[1]
    Wait Until Page Contains Element  submit_transition


Add worksheet duplicate
    Go to                       http://localhost:55001/plone/worksheets/WS-001
    Click Link                  Add Blank Reference
    Wait Until Page Contains    Add Blank Reference
    Click Element               xpath=//span[@id='worksheet_add_references']//tbody//tr[1]
    Wait Until Page Contains Element  submit_transition


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
    [Arguments]  ${selector}=
    ...          ${badResult}=
    ...          ${goodResult}=

    Log  Testing Result Range for ${selector} -:- values: ${badResult} and ${goodResult}  WARN

    Input Text          xpath=//input[@selector='${selector}'][1]  ${badResult}
    Press Key           xpath=//input[@selector='${selector}'][1]  \t
    Expect exclamation
    Input Text          xpath=//input[@selector='${selector}'][1]  ${goodResult}
    Press Key           xpath=//input[@selector='${selector}'][1]  \t
    Expect no exclamation


Expect exclamation
    sleep  1
    Page should contain Image   http://localhost:55001/plone/++resource++bika.lims.images/exclamation.png


Expect no exclamation
    sleep  1
    Page should not contain Image  http://localhost:55001/plone/++resource++bika.lims.images/exclamation.png


TestSampleState
    [Arguments]  ${selector}=
    ...          ${sample}=
    ...          ${expectedState}=

    ${VALUE}  Get Value  xpath=//input[@selector='${selector}'][1]
    Should Be Equal  ${VALUE}  ${expectedState}  ${sample} Workflow States incorrect: Expected: ${expectedState} -
    Log  Testing Sample State for ${sample}: ${expectedState} -:- ${VALUE}  WARN

Hang
    sleep  600
    Log  Hang Timeout Expired  WARN

