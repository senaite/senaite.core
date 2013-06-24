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

    Unassign Analysis   xpath=//input[@selector='H2O-0001-R01_Ca'][1]
    Add Analysis        xpath=//input[@selector='H2O-0001-R01_Ca'][1]

    Add worksheet control
    Add worksheet blank
    Add worksheet duplicate

    ## Value range testing: badValue followed by goodValue

    TestResultsRange    xpath=//tr[@keyword='Ca']//input[@selector='Result_Ca'][1]               0   9      # analysis
    TestResultsRange    xpath=//tr[@keyword='Ca']//input[@selector='Result_SA-001']              17  10.1   # control
    TestResultsRange    xpath=//tr[@keyword='Ca']//input[contains(@selector, 'Result_D')]        8   8.1    # duplicate
    TestResultsRange    xpath=//tr[@keyword='Ca']//input[contains(@selector, 'Result_D')]        10  9.9    # duplicate
    TestResultsRange    xpath=//tr[@keyword='Ca']//input[@selector='Result_SA-003']              2   0      # blank

    TestSampleState     xpath=//tr[@keyword='Ca']//input[@selector='state_title_Ca']            Ca                       Received
    TestSampleState     xpath=//tr[@keyword='Ca']//input[@selector='state_title_SA-001']        SA-001(Control Calcium)  Assigned
    TestSampleState     xpath=//tr[@keyword='Ca']//input[contains(@selector, 'state_title_D')]  _D(Dup Calcium)          Assigned
    TestSampleState     xpath=//tr[@keyword='Ca']//input[@selector='state_title_SA-003']        SA-003(Blank Calcium)    Assigned

    Click Element               xpath=//input[@value='Submit for verification'][1]
    Wait Until Page Contains    Changes saved.

    TestSampleState     xpath=//tr[@keyword='Ca']//input[@selector='state_title_Ca']            Ca(Normal Calcium)       To be verified
    TestSampleState     xpath=//tr[@keyword='Ca']//input[@selector='state_title_SA-001']        SA-001(Control Calcium)  To be verified
    TestSampleState     xpath=//tr[@keyword='Ca']//input[contains(@selector, 'state_title_D')]  _D(Dup Calcium)          To be verified
    TestSampleState     xpath=//tr[@keyword='Ca']//input[@selector='state_title_SA-003']        SA-003(Blank Calcium)    To be verified

    ## now fill in the remaining results

    TestResultsRange    xpath=//tr[@keyword='Mg']//input[@selector='Result_Mg']                   13     9.5     # analysis
    TestResultsRange    xpath=//tr[@keyword='Mg']//input[@selector='Result_SA-002']               2      9.2     # control
    TestResultsRange    xpath=//tr[@keyword='Mg']//input[contains(@selector, 'Result_D')]         8.54   8.55    # duplicate
    TestResultsRange    xpath=//tr[@keyword='Mg']//input[contains(@selector, 'Result_D')]         10.46  10.45   # duplicate
    TestResultsRange    xpath=//tr[@keyword='Mg']//input[@selector='Result_SA-004']               20     0       # blank

    TestSampleState     xpath=//tr[@keyword='Mg']//input[@selector='state_title_Mg']            Mg(Normal Magnesium)       Received
    TestSampleState     xpath=//tr[@keyword='Mg']//input[@selector='state_title_SA-002']        SA-002(Control Magnesium)  Assigned
    TestSampleState     xpath=//tr[@keyword='Mg']//input[contains(@selector, 'state_title_D')]  _D(Dup Magnesium)          Assigned
    TestSampleState     xpath=//tr[@keyword='Mg']//input[@selector='state_title_SA-004']        SA-004(Blank Magnesium)    Assigned

    Click Element               xpath=//input[@value='Submit for verification'][1]
    Wait Until Page Contains    Changes saved.

    TestSampleState     xpath=//tr[@keyword='Mg']//input[@selector='state_title_Mg']            Mg(Normal Magnesium)       To be verified
    TestSampleState     xpath=//tr[@keyword='Mg']//input[@selector='state_title_SA-002']        SA-001(Control Magnesium)  To be verified
    TestSampleState     xpath=//tr[@keyword='Mg']//input[contains(@selector, 'state_title_D')]  _D(Dup Magnesium)          To be verified
    TestSampleState     xpath=//tr[@keyword='Mg']//input[@selector='state_title_SA-004']        SA-003(Blank Magnesium)    To be verified

    # Retract
    Check worksheet state       to_be_verified
    Retract Analysis    xpath=//input[@selector='H2O-0001-R01_Ca'][1]
    ...                 xpath=//input[@selector='H2O-0001-R01_Ca-1'][1]
    Check worksheet state       open
    # Re-submit
    TestResultsRange            xpath=//tr[@keyword='Ca']//input[@selector='Result_Ca'][1]          0.5   9.5
    Click Element               xpath=//input[@value='Submit for verification'][1]
    Wait Until Page Contains    Changes saved.
    Check worksheet state       to_be_verified

    # verify all results
    Log out
    Log in   test_labmanager1   test_labmanager1
    Go to                       http://localhost:55001/plone/worksheets/WS-001
    select checkbox             analyses_form_select_all
    Click Element               xpath=//input[@value='Verify'][1]
    Wait Until Page Contains    Changes saved.
    Check worksheet state       verified


*** Keywords ***

Start browser
    Open browser  http://localhost:55001/plone/login_form
    Set selenium speed  ${SELENIUM_SPEED}

Add ARs
    [Documentation]     Add and receive some ARs.
    ...                 H2O-0001-R01  Bore

    @{time} =           Get Time        year month day hour min sec
    Go to               http://localhost:55001/plone/clients/client-1
    Wait until page contains element    css=body.portaltype-client
    Click Link                  Add
    Wait until page contains    Request new analyses
    Select from dropdown        ar_0_Template               Bore
    Select from datepicker      ar_0_SamplingDate           @{time}[2]
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
    Click Link                  Add Blank Reference
    Wait Until Page Contains    Distilled
    Click Element               xpath=//span[@id='worksheet_add_references']//tbody//tr[1]
    Wait Until Page Contains Element  submit_transition

Add worksheet duplicate
    Go to                       http://localhost:55001/plone/worksheets/WS-001
    Click Link                  Add Duplicate
    Wait Until Page Contains    Select a destinaton position
    Click Element               xpath=//span[@id='worksheet_add_duplicate_ars']//tbody//tr[1]
    Wait Until Page Contains Element  submit_transition

TestResultsRange
    [Arguments]  ${locator}=
    ...          ${badResult}=
    ...          ${goodResult}=

    # Log  Testing Result Range for ${locator} -:- values: ${badResult} and ${goodResult}  WARN

    Input Text          ${locator}  ${badResult}
    Focus               css=.analyst
    Expect exclamation
    Input Text          ${locator}  ${goodResult}
    Focus               css=.analyst
    Expect no exclamation

Expect exclamation
    sleep  0.5
    Page should contain Image   http://localhost:55001/plone/++resource++bika.lims.images/exclamation.png

Expect no exclamation
    sleep  0.5
    Page should not contain Image  http://localhost:55001/plone/++resource++bika.lims.images/exclamation.png

TestSampleState
    [Arguments]  ${locator}=
    ...          ${sample}=
    ...          ${expectedState}=

    ${VALUE}  Get Value  ${locator}
    Should Be Equal  ${VALUE}  ${expectedState}  ${sample} Workflow States incorrect: Expected: ${expectedState} -
    # Log  Testing Sample State for ${sample}: ${expectedState} -:- ${VALUE}  WARN

Unassign Analysis
    [Arguments]  ${locator}
    Go to                               http://localhost:55001/plone/worksheets/WS-001
    Wait until page contains element    css=body.template-manage_results
    Select checkbox                     ${locator}
    Click element                       unassign_transition
    Wait until page contains            Changes saved.
    Page should not contain element     ${locator}

Add Analysis
    [Arguments]         ${locator}
    Go to                               http://localhost:55001/plone/worksheets/WS-001/add_analyses
    Wait until page contains element    css=body.template-add_analyses
    Select checkbox                     ${locator}
    Click element                       assign_transition
    Wait until page contains element    css=body.template-manage_results
    page should contain element         ${locator}

Retract Analysis
    [Arguments]  ${locator}
    ...          ${new_locator}
    Go to                               http://localhost:55001/plone/worksheets/WS-001
    Wait until page contains element    css=body.template-manage_results
    select checkbox                     ${locator}
    Click element                       retract_transition
    Wait until page contains            Changes saved.
    ## The new/replacement analysis
    Page should contain element         ${locator}
    ## The old/retracted analysis selector ID
    Page should contain element         ${new_locator}
