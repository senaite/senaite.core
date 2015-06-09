*** Settings ***

Library         BuiltIn
Library         Selenium2Library  timeout=5  implicit_wait=0.2
Library         String
Resource        keywords.txt
Library         bika.lims.testing.Keywords
Resource        plone/app/robotframework/selenium.robot
Library         Remote  ${PLONEURL}/RobotRemote
Variables       plone/app/testing/interfaces.py
Variables       bika/lims/tests/variables.py

Suite Setup     Start browser
Suite Teardown  Close All Browsers

Library          DebugLibrary

*** Variables ***

*** Test Cases ***

Reject worksheet with regular, blank, control and duplicate analyses
    Log in                            test_labmanager         test_labmanager
    Wait until page contains          You are now logged in

    Create reference sample from   Distilled Water (Blank)
    Create reference sample from   Trace Metals 10
    ${ar_id}=                         Add an AR
    Receive ${ar_id}
    Go to                             ${PLONEURL}/clients/worksheets
    Select from list                  analyst         Lab Analyst 1
    click element                     css=.worksheet_add
    select checkbox                   list_select_all
    Click button                      xpath=//input[@value="Assign"]
    Wait until page contains          Add Blank Reference
    Click link                        Add Blank Reference
    Wait until page contains element  css=#worksheet_add_references .bika-listing-table
    Click element                     css=#worksheet_add_references .bika-listing-table tbody.item-listing-tbody tr
    Wait until page contains          Add Blank Reference
    Click link                        Add Control Reference
    Click element                     css=#worksheet_add_references .bika-listing-table tbody.item-listing-tbody tr
    Wait until page contains          Add Blank Reference
    Click link                        Add Duplicate
    Click element                     css=#worksheet_add_duplicate_ars .bika-listing-table tbody.item-listing-tbody tr
    Wait until page contains          Add Blank Reference
    Input text                        xpath=//input[@selector='Result_Ca']           21
    Input text                        xpath=//input[@selector='Result_SA-001']       21
    Input text                        xpath=//input[@selector='Result_SA-002']       21
    Input text                        xpath=//input[@selector='Result_D-001']        21
    Click button                      xpath=//input[@value="Submit for verification"]
    Go to                             ${PLONEURL}/clients/worksheets/WS-001
    click element                     css=.state-to_be_verified
    click element                     css=#workflow-transition-reject
    wait until page contains          Item state changed
    page should contain               This worksheet has been rejected.
    Xpath Should Match X Times        //td[contains(@class, 'state-rejected') and contains(@class, 'state_title')]     4
    Go to                             ${PLONEURL}/clients/worksheets/WS-002
    page should contain               This worksheet has been created to replace the rejected
    Xpath Should Match X Times        //td[contains(@class, 'state-sample_received') and contains(@class, 'state_title')]     1
    Xpath Should Match X Times        //td[contains(@class, 'state-assigned') and contains(@class, 'state_title')]     4

*** Keywords ***

Add an AR
    Go to                             ${PLONEURL}/clients/client-1/portal_factory/AnalysisRequest/Request%20new%20analyses/ar_add
    Wait until page contains          Request new analyses
    @{time} =                         Get Time                year month day hour min sec
    SelectDate                        css=#ar_0_SamplingDate       @{time}[2]
    Select From Dropdown              css=#ar_0_SampleType         Water
    Select from dropdown              css=#ar_0_Contact            Rita
    Select from dropdown              css=#ar_0_Priority           High
    Click Element                     xpath=//th[@id='cat_lab_Metals']
    Select Checkbox                   xpath=//input[@title='Calcium' and @name='ar.0.Analyses:list:ignore_empty:record']
    Set Selenium Timeout              30
    Click Button                      Save
    Wait until page contains          created
    Set Selenium Timeout              5
    ${ar_id} =                        Get text      //dl[contains(@class, 'portalMessage')][2]/dd
    ${ar_id} =                        Set Variable  ${ar_id.split()[2]}
    [return]                          ${ar_id}

Receive ${ar_id}
    Go to                             ${PLONEURL}/clients/client-1/analysisrequests
    Wait until page contains          ${ar_id}
    Select checkbox                   xpath=//input[@item_title="${ar_id}"]
    Click button                      xpath=//input[@id="receive_transition"]
    Wait until page contains          saved

Create reference sample from
    [arguments]                       ${ref_definition_title}
    Go to                             ${PLONEURL}/bika_setup/bika_suppliers/supplier-2
    Click link                        Add
    Wait Until Page Contains Element  title
    Input Text                        title           new ${ref_definition_title} ref
    Select From List                  ReferenceDefinition:list    ${ref_definition_title}
    Click Link                        Dates
    Wait Until Page Contains Element  DateSampled
    SelectPrevMonthDate               DateReceived  3
    SelectNextMonthDate               ExpiryDate  5
    Click Button                      Save
