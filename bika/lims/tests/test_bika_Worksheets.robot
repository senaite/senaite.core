*** Settings ***

Library          Selenium2Library  timeout=5  implicit_wait=0.2
Library          String
Resource         keywords.txt
Library          bika.lims.testing.Keywords
Resource         plone/app/robotframework/selenium.robot
Resource         plone/app/robotframework/saucelabs.robot
Variables        plone/app/testing/interfaces.py
Variables        bika/lims/tests/variables.py
Suite Setup      Start browser
Suite Teardown   Close All Browsers

*** Variables ***

*** Test Cases ***

Test Worksheets
    [Documentation]   Worksheets
    ...  Groups analyses together for data entry, instrument interfacing,
    ...  and workflow transition cascades.
    Log in              test_labmanager  test_labmanager
    Create AnalysisRequests
    Create Reference Samples
    Create Worksheet
    Go to                       ${PLONEURL}/worksheets/WS-001
    Select from list            css=select.analyst             Lab Analyst 2
    Select from list            css=select.instrument          Protein Analyser
    Page should contain         Changes saved.
    Reload Page
    ${analyst}=                 Get selected list label        css=select.analyst
    ${instrument}=              Get selected list label        css=select.instrument
    Should be equal             ${analyst}         Lab Analyst 2
    Should be equal             ${Instrument}      Protein Analyser
    Add Analyses                H2O-0001-R01_Ca    H2O-0001-R01_Mg
    Add Reference Analyses
    Unassign all
    Add Analyses                H2O-0001-R01_Ca    H2O-0001-R01_Mg
    Add Reference Analyses
    Submit and Verify and Test
    Unassign all
    Add Analyses                H2O-0002-R01_Ca    H2O-0002-R01_Mg
    Add Reference Analyses
    Submit results quickly
    Add Duplicate: Submit, verify, and check that alerts persist
    Test Retraction
    Log out
    Log in   test_labmanager1   test_labmanager1
    Verify all
    Log out
    Log in   test_labmanager   test_labmanager



*** Keywords ***

Create AnalysisRequests
    [Documentation]     Add and receive some ARs.
    ...                 H2O-0001-R01  Bore
    ...                 H2O-0002-R01  Bruma
    @{time} =                   Get Time        year month day hour min sec
    Go to                       ${PLONEURL}/clients/client-1
    Wait until page contains element    css=body.portaltype-client
    Click Link                  Add
    Wait until page contains    Request new analyses
    Select from dropdown        ar_0_Contact                Rita
    Select from dropdown        ar_1_Contact                Rita
    sleep  1
    Select from dropdown        ar_0_Template               Bore
    Select from dropdown        ar_1_Template               Bruma
    sleep  1
    Select Date                 ar_0_SamplingDate           @{time}[2]
    Select Date                 ar_1_SamplingDate           @{time}[2]
    sleep  1
    Set Selenium Timeout        30
    Click Button                Save
    Wait until page contains    created
    Set Selenium Timeout        10
    Select checkbox             analysisrequests_select_all
    Click element               receive_transition
    Wait until page contains    saved

Create Reference Samples

    #Create Expired Reference Sample

    Go to  ${PLONEURL}/bika_setup/bika_suppliers/supplier-1
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

    #Create Hazardous Metals Reference Sample

    Go to  ${PLONEURL}/bika_setup/bika_suppliers/supplier-1
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

    #Create Distilled Water Reference Sample

    Go to  ${PLONEURL}/bika_setup/bika_suppliers/supplier-2
    Wait Until Page Contains    Add
    Click Link                  Add
    Wait Until Page Contains    Add Reference Sample
    Input Text                  title                       D Water Reference Sample
    Select From List            ReferenceDefinition:list    Distilled Water (Blank)
    Select From List            ReferenceManufacturer:list  Blott
    Input Text                  CatalogueNumber             Numba Too
    Input Text                  LotNumber                   MoreLotOfNumba
    Click Link                  Dates
    Wait Until Page Contains    Expiry Date
    SelectNextMonthDate         ExpiryDate                  25
    Click Button                Save
    Wait Until Page Contains    Changes saved.

    #This reference used to test LIMS-1325
    Go to  ${PLONEURL}/bika_setup/bika_suppliers/supplier-1
    Wait Until Page Contains    Add
    Click Link                  Add
    Wait Until Page Contains    Add Reference Sample
    Input Text                  title                       9METALS
    Select From List            ReferenceDefinition:list    Trace Metals 9
    Click Link                  Dates
    Wait Until Page Contains    Expiry Date
    SelectNextMonthDate         ExpiryDate                  25
    Click Button                Save
    Wait Until Page Contains    Changes saved.

Create Worksheet
    Go to  ${PLONEURL}/worksheets
    Wait Until Page Contains    Mine
    Select From List            analyst          Lab Analyst 1
    Click Button                Add
    Wait Until Page Contains    Add Analyses

Add Analyses
    [Arguments]         @{analyses}

    Go to                               ${PLONEURL}/worksheets/WS-001/add_analyses
    Wait Until Page Contains            Add Analyses
    Click Element                       css=th#foldercontents-getRequestID-column
    Wait Until Page Contains Element    css=th#foldercontents-getRequestID-column.sort_on

    :FOR     ${analysis}   IN   @{analyses}
    \     Select Checkbox         xpath=//input[@selector='${analysis}']

    Set Selenium Timeout        30
    Click Element               assign_transition
    Wait Until Page Contains    Manage Results
    Set Selenium Timeout        10

Add Reference Analyses

    #Add worksheet controls
    Go to                       ${PLONEURL}/worksheets/WS-001/add_control
    Wait Until Page Contains    Trace Metals 10
    Click Element               xpath=//span[@id='worksheet_add_references']//tbody//tr[1]
    Wait Until Page Contains Element  submit_transition

    Go to                       ${PLONEURL}/worksheets/WS-001/add_control
    unselect checkbox           css=input[item_title="Calcium"]
    Wait Until Page Contains    Trace Metals 9
    sleep    1
    Click Element               xpath=//span[@id='worksheet_add_references']//tbody//tr[2]
    Wait Until Page Contains Element  submit_transition

    #Add worksheet blank
    Go to                       ${PLONEURL}/worksheets/WS-001/add_blank
    Wait Until Page Contains    Distilled
    sleep    1
    Click Element               xpath=//span[@id='worksheet_add_references']//tbody//tr[1]
    Wait Until Page Contains Element  submit_transition

    #Add worksheet duplicate
    Go to                       ${PLONEURL}/worksheets/WS-001/add_duplicate
    Wait Until Page Contains    Select a destinaton position
    Click Element               xpath=//span[@id='worksheet_add_duplicate_ars']//tbody//tr[1]
    Wait Until Page Contains Element  submit_transition

    sleep    1
    Xpath Should Match X Times     //tr[@keyword="Ca"]   4
    Xpath Should Match X Times     //tr[@keyword="Mg"]   5

Unassign all
    Select Checkbox             analyses_form_select_all
    Click Element               unassign_transition
    Wait Until Page Contains    Changes saved

Submit and Verify and Test
    [Documentation]     Insert results in all available analyses,
    ...                 checking ranges, workflow, etc during the process.

    # All values are valid for Calcium, this sampletype has no specification linked to it.
    Input Text    xpath=//tr[@keyword='Ca']//input[@selector='Result_Ca']                        9                  # analysis
    TestResultsRange    xpath=(//tr[@keyword='Ca']//input[contains(@selector, 'Result_SA')])[1]     17  10.1        # control
    TestResultsRange    xpath=//tr[@keyword='Ca']//input[contains(@selector, 'Result_D')]           8.1   8.2       # duplicate low
    TestResultsRange    xpath=//tr[@keyword='Ca']//input[contains(@selector, 'Result_D')]           10  9.9         # duplicate high
    TestResultsRange    xpath=(//tr[@keyword='Ca']//input[contains(@selector, 'Result_SA')])[2]     2   0           # blank

    TestSampleState     xpath=//tr[@keyword='Ca']//input[@selector='state_title_Ca']                  Ca                       Received
    TestSampleState     xpath=(//tr[@keyword='Ca']//input[contains(@selector, 'state_title_SA')])[1]  SA-001(Control Calcium)  Assigned
    TestSampleState     xpath=//tr[@keyword='Ca']//input[contains(@selector, 'state_title_D')]        _D(Dup Calcium)          Assigned
    TestSampleState     xpath=(//tr[@keyword='Ca']//input[contains(@selector, 'state_title_SA')])[2]  SA-003(Blank Calcium)    Assigned

    Click Element               xpath=//input[@value='Submit for verification'][1]
    Wait Until Page Contains    Changes saved.

    TestSampleState     xpath=//tr[@keyword='Ca']//input[@selector='state_title_Ca']                   Ca(Normal Calcium)       To be verified
    TestSampleState     xpath=(//tr[@keyword='Ca']//input[contains(@selector, 'state_title_SA')])[1]   SA-001(Control Calcium)  To be verified
    TestSampleState     xpath=//tr[@keyword='Ca']//input[contains(@selector, 'state_title_D')]         _D(Dup Calcium)          To be verified
    TestSampleState     xpath=(//tr[@keyword='Ca']//input[contains(@selector, 'state_title_SA')])[2]   SA-003(Blank Calcium)    To be verified

    Check worksheet state       open

    ## now fill in the remaining results
    input text    xpath=//tr[@keyword='Mg']//input[@selector='Result_Mg']                       9.5     # analysis
    TestResultsRange    xpath=(//tr[@keyword='Mg']//input[contains(@selector, 'Result_SA')])[1]   2      9.2     # control1
    TestResultsRange    xpath=(//tr[@keyword='Mg']//input[contains(@selector, 'Result_SA')])[2]   2      9.2     # control2

    TestResultsRange    xpath=//tr[@keyword='Mg']//input[contains(@selector, 'Result_D')]         8.59   8.6    # duplicate high
    TestResultsRange    xpath=//tr[@keyword='Mg']//input[contains(@selector, 'Result_D')]         10.51  10.5   # duplicate low
    TestResultsRange    xpath=(//tr[@keyword='Mg']//input[contains(@selector, 'Result_SA')])[3]   20     0       # blank

    TestSampleState     xpath=//tr[@keyword='Mg']//input[@selector='state_title_Mg']                   Mg(Normal Magnesium)       Received
    TestSampleState     xpath=(//tr[@keyword='Mg']//input[contains(@selector, 'state_title_SA')])[1]   SA-002(Control Magnesium)  Assigned
    TestSampleState     xpath=//tr[@keyword='Mg']//input[contains(@selector, 'state_title_D')]         _D(Dup Magnesium)          Assigned
    TestSampleState     xpath=(//tr[@keyword='Mg']//input[contains(@selector, 'state_title_SA')])[2]   SA-004(Blank Magnesium)    Assigned

    Click Element               xpath=//input[@value='Submit for verification'][1]
    Wait Until Page Contains    Changes saved.

    TestSampleState     xpath=//tr[@keyword='Mg']//input[@selector='state_title_Mg']                   Mg(Normal Magnesium)       To be verified
    TestSampleState     xpath=(//tr[@keyword='Mg']//input[contains(@selector, 'state_title_SA')])[1]   SA-001(Control Magnesium)  To be verified
    TestSampleState     xpath=//tr[@keyword='Mg']//input[contains(@selector, 'state_title_D')]         _D(Dup Magnesium)          To be verified
    TestSampleState     xpath=(//tr[@keyword='Mg']//input[contains(@selector, 'state_title_SA')])[2]   SA-003(Blank Magnesium)    To be verified

    Check worksheet state       to_be_verified

Submit results quickly
    [Documentation]     The results-entry process is repeated a few times
    ...                 in order to test workflow, so we have a second
    ...                 keyword that is not so slow and needlessly thorough.
    # All values are valid for Calcium, this sampletype has no specification linked to it.

    Input Text    xpath=//tr[@keyword='Ca']//input[@selector='Result_Ca']                        9       # analysis
    Input Text    xpath=//tr[@keyword='Mg']//input[@selector='Result_Mg']                        9.5     # analysis
    Input Text    xpath=(//tr[@keyword='Ca']//input[contains(@selector, 'Result_SA')])[1]        10.1    # control
    Input Text    xpath=(//tr[@keyword='Mg']//input[contains(@selector, 'Result_SA')])[1]        9.2     # control
    Input Text    xpath=(//tr[@keyword='Mg']//input[contains(@selector, 'Result_SA')])[2]        9.2     # control
    Input Text    xpath=//tr[@keyword='Ca']//input[contains(@selector, 'Result_D')]              8.5     # duplicate
    Input Text    xpath=//tr[@keyword='Mg']//input[contains(@selector, 'Result_D')]              10.45   # duplicate
    Input Text    xpath=(//tr[@keyword='Ca']//input[contains(@selector, 'Result_SA')])[2]        0       # blank
    Input Text    xpath=(//tr[@keyword='Mg']//input[contains(@selector, 'Result_SA')])[3]        0      # blank
    Focus                       css=.analyst
    Click Element               xpath=//input[@value='Submit for verification'][1]
    Wait Until Page Contains    Changes saved.

Check worksheet state
    [Arguments]  ${state_id}
    Go to        ${PLONEURL}/worksheets/WS-001
    Wait until page contains element    xpath=//span[@class='state-${state_id}']

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
    Page should contain Image   ${PLONEURL}/++resource++bika.lims.images/exclamation.png

Expect no exclamation
    sleep  0.5
    Page should not contain Image  ${PLONEURL}/++resource++bika.lims.images/exclamation.png

TestSampleState
    [Arguments]  ${locator}=
    ...          ${sample}=
    ...          ${expectedState}=

    ${VALUE}  Get Value  ${locator}
    Should Be Equal  ${VALUE}  ${expectedState}  ${sample} Workflow States incorrect: Expected: ${expectedState} -
    # Log  Testing Sample State for ${sample}: ${expectedState} -:- ${VALUE}  WARN

Unassign Analysis
    [Arguments]  ${locator}
    Go to                               ${PLONEURL}/worksheets/WS-001
    Wait until page contains element    css=body.template-manage_results
    Select checkbox                     ${locator}
    Click element                       unassign_transition
    Wait until page contains            Changes saved.
    Page should not contain element     ${locator}

Test Retraction
    Retract Analysis            xpath=//input[@selector='H2O-0002-R01_Ca'][1]
    ...                         xpath=//input[@selector='H2O-0002-R01_Ca-1'][1]
    Check worksheet state       open
    Input Text                  xpath=//tr[@keyword='Ca']//input[@selector='Result_Ca'][1]   9.5
    Focus                       css=.analyst
    Click Element               xpath=//input[@value='Submit for verification'][1]
    Wait Until Page Contains    Changes saved.
    Check worksheet state       to_be_verified

Retract Analysis
    [Arguments]  ${locator}
    ...          ${new_locator}
    Go to                               ${PLONEURL}/worksheets/WS-001
    Wait until page contains element    css=body.template-manage_results
    select checkbox                     ${locator}
    Click element                       retract_transition
    Wait until page contains            Changes saved.
    ## The new/replacement analysis
    Page should contain element         ${locator}
    ## The old/retracted analysis selector ID
    Page should contain element         ${new_locator}

Add Duplicate: Submit, verify, and check that alerts persist
    Go to                       ${PLONEURL}/worksheets/WS-001/add_duplicate
    Wait Until Page Contains    Select a destinaton position
    Click Element               xpath=//span[@id='worksheet_add_duplicate_ars']//tbody//tr[1]
    Wait Until Page Contains Element  //tr[@keyword='Mg']//input[@type='text' and contains(@selector, 'Result_D')]
    # Check if invalid results are flagged correctly through submit and verify
    Input Text  xpath=//tr[@keyword='Mg']//input[@type='text' and contains(@selector, 'Result_D')]  8.5
    Input Text  xpath=//tr[@keyword='Ca']//input[@type='text' and contains(@selector, 'Result_D')]  55
    page should contain element    css=img[title="Relative percentage difference, 11.1111111111 %, is out of valid range (10.0 %))"]
    Focus                       css=.analyst
    Click Element               xpath=//input[@value='Submit for verification'][1]
    Wait Until Page Contains    Changes saved.

Verify all
    Go to                       ${PLONEURL}/worksheets/WS-001
    select checkbox             analyses_form_select_all
    Click Element               xpath=//input[@value='Verify'][1]
    Wait Until Page Contains    Changes saved.
    Check worksheet state       verified
