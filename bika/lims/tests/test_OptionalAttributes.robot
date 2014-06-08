*** Settings ***

Library          Selenium2Library  timeout=5  implicit_wait=0.2
Library          String
Library          DebugLibrary
Resource         keywords.txt
Library          bika.lims.testing.Keywords
Resource         plone/app/robotframework/selenium.robot
Resource         plone/app/robotframework/saucelabs.robot
Variables        plone/app/testing/interfaces.py
Variables        bika/lims/tests/variables.py
Suite Setup      Start browser
Suite Teardown   Close All Browsers

*** Variables ***

${ar_factory_url}  portal_factory/AnalysisRequest/Request%20new%20analyses/ar_add

*** Test Cases ***

Create AR with hidden attributes
    Hide Attributes
    Check hidden fields on AR Add
    ${ar_id}=          Create Primary AR
    Check hidden fields on AR view ${ar_id}
    Check hidden fields on AR invoice ${ar_id}
    

*** Keywords ***

Hide Attributes
    Log in                      admin    secret
    Wait until page contains    You are now logged in
    Go to                       ${PLONEURL}/portal_registry/edit/bika.lims.hiddenattributes
    Click Button                Add
    Input Text                 form-widgets-value-0     AnalysisRequest\nClientOrderNumber\ngetClientOrderNumber\nSamplingDeviation\nAdHoc\nInvoiceExclude\nSamplePoint
    Click Button                Add
    Input Text                 form-widgets-value-1     Sample\nSamplingDeviation\nSamplePoint

    Click Button                Save
    Log out

Start browser
    Open browser                        ${PLONEURL}/login_form
    Set selenium speed                  ${SELENIUM_SPEED}

Check hidden fields on AR Add
    Log in                      test_labmanager  test_labmanager
    Go to                       ${PLONEURL}/clients/client-1
    Wait until page contains element    css=body.portaltype-client
    Page should not contain     Client Order
    Page should not contain     Sampling Deviation

    Click Link                  Add
    Wait until page contains    Request new analyses
    Page should not contain     Sample Point
    Page should not contain     Sampling Deviation
    Page should not contain     Client Order Number
    Page should not contain     Ad-Hoc
    Page should not contain     Invoice Exclude

Create Primary AR
    Log in                      test_labmanager  test_labmanager
    @{time} =                   Get Time        year month day hour min sec
    Go to                       ${PLONEURL}/clients/client-1
    Wait until page contains element    css=body.portaltype-client
    Click Link                  Add
    Wait until page contains    Request new analyses
    Select from dropdown        ar_0_Contact                Rita
    Select from dropdown        ar_0_Template               Bore
    Select Date                 ar_0_SamplingDate           @{time}[2]
    Set Selenium Timeout        30
    Click Button                Save
    Set Selenium Timeout        10
    Wait until page contains    created
    ${ar_id} =                  Get text      //dl[contains(@class, 'portalMessage')][2]/dd
    ${ar_id} =                  Set Variable  ${ar_id.split()[2]}
    Go to                       http://localhost:55001/plone/clients/client-1/analysisrequests
    Wait until page contains    ${ar_id}
    [return]                    ${ar_id}

Check hidden fields on AR view ${ar_id}
    Go to                       http://localhost:55001/plone/clients/client-1/${ar_id}
    Page should not contain     Sample Point
    Page should not contain     Sampling Deviation
    Page should not contain     Client Order Number
    Page should not contain     Ad-Hoc
    Page should not contain     Invoice Exclude

Check hidden fields on AR invoice ${ar_id}
    Go to                       http://localhost:55001/plone/clients/client-1/${ar_id}/invoice
    Page should not contain     Sample Point
    Page should not contain     Sampling Deviation
    Page should not contain     Client Order Number
    Page should not contain     Ad-Hoc
    Page should not contain     Invoice Exclude

Check hidden fields on Sample view
http://localhost:55001/plone/clients/client-1/H2O-0001
    Go to                       http://localhost:55001/plone/clients/client-1/H2O-0001
    Page should not contain     Sample Point
    Page should not contain     Sampling Deviation
    Page should not contain     Client SID
    Page should not contain     Ad-Hoc

Receive sample
    Select checkbox             xpath=//input[@item_title="${ar_id}"]
    Click button                xpath=//input[@value="Receive sample"]
    Wait until page contains    saved


Complete ar_add form Without template
    @{time} =                  Get Time        year month day hour min sec
    SelectDate                 ar_0_SamplingDate   @{time}[2]
    Select From Dropdown       ar_0_SampleType    Water
    Select from dropdown       ar_0_Contact       Rita
    Select from dropdown       ar_0_Priority           High
    Click Element              xpath=//th[@id='cat_lab_Water Chemistry']
    Select Checkbox            xpath=//input[@title='Moisture' and @name='ar.0.Analyses:list:ignore_empty:record']
    Click Element              xpath=//th[@id='cat_lab_Metals']
    Select Checkbox            xpath=//input[@title='Calcium' and @name='ar.0.Analyses:list:ignore_empty:record']
    Select Checkbox            xpath=//input[@title='Phosphorus' and @name='ar.0.Analyses:list:ignore_empty:record']
    Click Element              xpath=//th[@id='cat_lab_Microbiology']
    Select Checkbox            xpath=//input[@title='Clostridia' and @name='ar.0.Analyses:list:ignore_empty:record']
    Select Checkbox            xpath=//input[@title='Ecoli' and @name='ar.0.Analyses:list:ignore_empty:record']
    Select Checkbox            xpath=//input[@title='Enterococcus' and @name='ar.0.Analyses:list:ignore_empty:record']
    Select Checkbox            xpath=//input[@title='Salmonella' and @name='ar.0.Analyses:list:ignore_empty:record']
    Set Selenium Timeout       60
    Click Button               Save
    Wait until page contains   created
    ${ar_id} =                 Get text      //dl[contains(@class, 'portalMessage')][2]/dd
    ${ar_id} =                 Set Variable  ${ar_id.split()[2]}
    [return]                   ${ar_id}

Submit results with out of range tests
    [Documentation]   Complete all received analysis result entry fields
    ...               Do some out-of-range checking, too

    ${count} =                 Get Matching XPath Count    //input[@type='text' and @field='Result']
    ${count} =                 Convert to integer    ${count}
    :FOR    ${index}           IN RANGE    1   ${count+1}
    \    TestResultsRange      xpath=(//input[@type='text' and @field='Result'])[${index}]       5   10
    Sleep                      10s
    Click Element              xpath=//input[@value='Submit for verification'][1]
    Wait Until Page Contains   Changes saved.

Submit results
    [Documentation]   Complete all received analysis result entry fields

    ${count} =                 Get Matching XPath Count    //input[@type='text' and @field='Result']
    ${count} =                 Convert to integer    ${count}
    :FOR    ${index}           IN RANGE    1   ${count+1}
    \    Input text            xpath=(//input[@type='text' and @field='Result'])[${index}]   10
    Sleep                      10s
    Click Element              xpath=//input[@value='Submit for verification'][1]
    Wait Until Page Contains   Changes saved.

Add new ${service} analysis to ${ar_id}
    Go to                      ${PLONEURL}/clients/client-1/${ar_id}/analyses
    select checkbox            xpath=//input[@alt='Select ${service}']
    click element              save_analyses_button_transition
    wait until page contains   saved.

${ar_id} state should be ${state_id}
    Go to                        ${PLONEURL}/clients/client-1/${ar_id}
    log     span.state-${state_id}   warn
    Page should contain element  css=span.state-${state_id}

TestResultsRange
    [Arguments]  ${locator}=
    ...          ${badResult}=
    ...          ${goodResult}=

    # Log  Testing Result Range for ${locator} -:- values: ${badResult} and ${goodResult}  WARN

    Input Text          ${locator}  ${badResult}
    Press Key           ${locator}   \\9
    Expect exclamation
    Input Text          ${locator}  ${goodResult}
    Press Key           ${locator}   \\9
    Expect no exclamation

Expect exclamation
    sleep  .5
    Page should contain Image   ${PLONEURL}/++resource++bika.lims.images/exclamation.png

Expect no exclamation
    sleep  .5
    Page should not contain Image  ${PLONEURL}/++resource++bika.lims.images/exclamation.png

TestSampleState
    [Arguments]  ${locator}=
    ...          ${sample}=
    ...          ${expectedState}=

    ${VALUE}  Get Value  ${locator}
    Should Be Equal  ${VALUE}  ${expectedState}  ${sample} Workflow States incorrect: Expected: ${expectedState} -
    # Log  Testing Sample State for ${sample}: ${expectedState} -:- ${VALUE}  WARN

