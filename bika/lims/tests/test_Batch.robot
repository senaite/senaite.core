*** Settings ***

Library          Selenium2Library  timeout=10  implicit_wait=0.2
Library          String
Resource         keywords.txt
Variables        plone/app/testing/interfaces.py
Variables        bika/lims/tests/variables.py
Suite Setup      Start browser
Suite Teardown   Close All Browsers

*** Variables ***

*** Test Cases ***

Test Batch-AR workflow dependencies
    Log in  test_labmanager  test_labmanager

    Add Batch
    Batch state should be  open
    Add AR
    Batch state should be  open
    Receive AR  AP-0001-R01
    Batch state should be  sample_received
    Add AR
    Batch state should be  open
    Receive AR  AP-0002-R01
    Batch state should be  sample_received
    Submit AR  AP-0001-R01
    Submit AR  AP-0002-R01
    Batch state should be  to_be_verified
    Add AR
    Batch state should be  open
    Receive AR  AP-0003-R01
    Batch state should be  sample_received
    Submit AR  AP-0003-R01
    Batch state should be  to_be_verified
    Retract AR  AP-0001-R01
    Batch state should be  sample_received
    Submit AR  AP-0001-R01
    Batch state should be  to_be_verified
    Log out
    Log in  test_labmanager1  test_labmanager1
    Verify AR  AP-0001-R01
    Verify AR  AP-0002-R01
    Verify AR  AP-0003-R01
    Batch state should be  verified


*** Keywords ***

Start browser
    Open browser         http://localhost:55001/plone/login
    Set selenium speed   ${SELENIUM_SPEED}

Add Batch
    Go to                        http://localhost:55001/plone/batches
    Wait until page contains     Add
    Click Link                   Add
    Wait until page contains     Add Batch
    Input text                   description  Just a regular batch
    Select from dropdown         ClientID     Happy
    Click Button                 xpath=//input[@value="Save"]
    Wait until page contains     saved

Batch state should be
    [Arguments]   ${state_id}
    Go to                        http://localhost:55001/plone/batches/B-001/analysisrequests
    Wait until page contains     Analysis Requests
    Page should contain element  css=span.state-${state_id}

Add AR
    Go to                        http://localhost:55001/plone/batches/B-001/analysisrequests
    Wait until page contains     Add new
    Select from list             col_count  1
    click Link                   Add new
    Wait until page contains     Request new analyses
    Select from dropdown         ar_0_SampleType         Apple
    Select from dropdown         ar_0_Client             Happy
    Select from dropdown         ar_0_Profile            Counts
    SelectDate                   ar_0_SamplingDate       1
    Click Button                 Save
    Wait until page contains     created

Receive AR
    [Arguments]   ${ar_id}
    Go to                        http://localhost:55001/plone/batches/B-001/analysisrequests
    Wait until page contains     ${ar_id}
    Select checkbox              xpath=//input[@item_title="${ar_id}"]
    Click button                 xpath=//input[@value="Receive sample"]
    Wait until page contains     saved

Submit AR
    [Arguments]   ${ar_id}
    Go to                        http://localhost:55001/plone/batches/B-001/analysisrequests
    Wait until page contains     Add new
    Click link                   ${ar_id}
    Wait until page contains     Results not requested
    Input text                   xpath=//tr[@keyword='Ecolicnt']//input[@type='text']    10
    Input text                   xpath=//tr[@keyword='Enterocnt']//input[@type='text']   10
    Input text                   xpath=//tr[@keyword='TVBcnt']//input[@type='text']      10
    Press Key                    xpath=//tr[@keyword='TVBcnt']//input[@type='text']      \t
    focus                        css=#content-core
    Click button                 xpath=//input[@value="Submit for verification"]
    Wait until page contains     saved

Retract AR
    [Arguments]   ${ar_id}
    Go to                        http://localhost:55001/plone/batches/B-001/analysisrequests
    Wait until page contains     ${ar_id}
    Select checkbox              xpath=//input[@item_title="${ar_id}"]
    Click button                 xpath=//input[@value="Retract"]
    Wait until page contains     saved

Verify AR
    [Arguments]   ${ar_id}
    Go to                        http://localhost:55001/plone/batches/B-001/analysisrequests
    Wait until page contains     ${ar_id}
    Select checkbox              xpath=//input[@item_title="${ar_id}"]
    Click button                 xpath=//input[@value="Verify"]
    Wait until page contains     saved
