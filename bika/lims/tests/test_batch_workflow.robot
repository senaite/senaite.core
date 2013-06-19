*** Settings ***

Library   Selenium2Library  timeout=20  implicit_wait=0
Resource  keywords.txt

Suite Setup     Start browser
#Suite Teardown  Close All Browsers

*** Test Cases ***

Test Batch-AR workflow dependencies
    Log in  test_labmanager  test_labmanager

    Add Batch
    Batch state should be  open
    Add AR
    Batch state should be  open
    Receive AR  FN-0001-R01
    Batch state should be  sample_received
    Add AR
    Batch state should be  open
    Receive AR  FN-0002-R01
    Batch state should be  sample_received
    Submit AR  FN-0001-R01
    Submit AR  FN-0002-R01
    Batch state should be  to_be_verified
    Add AR
    Batch state should be  open
    Receive AR  FN-0003-R01
    Batch state should be  sample_received
    Submit AR  FN-0003-R01
    Batch state should be  to_be_verified
    Retract AR  FN-0001-R01
    Batch state should be  sample_received
    Submit AR  FN-0001-R01
    Batch state should be  to_be_verified
    Log out
    Log in  test_labmanager1  test_labmanager1
    Verify AR  FN-0001-R01
    Verify AR  FN-0002-R01
    Verify AR  FN-0003-R01
    Batch state should be  verified


*** Keywords ***

Start browser
    Open browser         http://localhost:55001/plone/
    Set selenium speed   0

Add Batch
    Go to                        http://localhost:55001/plone/batches
    Wait until page contains     Add
    Click Link                   Add
    Wait until page contains     Add Case
    Input text                   description  Just a regular batch
    # Select from dropdown         ClientID   Happy    1
    Click Button                 xpath=//input[@value="Save"]
    Wait until page contains     saved

Batch state should be
    [Arguments]   ${state_id}
    Go to                        http://localhost:55001/plone/batches/B-13-001
    Wait until page contains     Analysis Requests
    Page should contain element  css=span.state-${state_id}

Add AR
    Go to                        http://localhost:55001/plone/batches/B-13-001
    Wait until page contains     Add new
    Select from list             col_count  1
    click Link                   Add new
    Wait until page contains     Request new analyses
    Input text                   ar_0_SampleType              Fingernails
    Select from list             ar_0_AnalysisProfile         Lab: Micro-Bio Counts
    Select from datepicker       ar_0_SamplingDate            1
    Click Button                 Save
    Wait until page contains     created

Receive AR
    [Arguments]   ${ar_id}
    Go to                        http://localhost:55001/plone/batches/B-13-001
    Wait until page contains     ${ar_id}
    Select checkbox              xpath=//input[@item_title="${ar_id}"]
    Click button                 xpath=//input[@value="Receive sample"]
    Wait until page contains     saved

Submit AR
    [Arguments]   ${ar_id}
    Go to                        http://localhost:55001/plone/batches/B-13-001
    Wait until page contains     Add new
    Click link                   ${ar_id}
    Wait until page contains     Results not requested
    Select from list             xpath=//tr[@keyword='Clos']//select         Negative
    Select from list             xpath=//tr[@keyword='Ecoli']//select        Negative
    Select from list             xpath=//tr[@keyword='Entero']//select       Negative
    Select from list             xpath=//tr[@keyword='Salmon']//select       Negative
    Click button                 xpath=//input[@value="Submit for verification"]
    Wait until page contains     saved

Retract AR
    [Arguments]   ${ar_id}
    Go to                        http://localhost:55001/plone/batches/B-13-001
    Wait until page contains     ${ar_id}
    Select checkbox              xpath=//input[@item_title="${ar_id}"]
    Click button                 xpath=//input[@value="Retract"]
    Wait until page contains     saved

Verify AR
    [Arguments]   ${ar_id}
    Go to                        http://localhost:55001/plone/batches/B-13-001
    Wait until page contains     ${ar_id}
    Select checkbox              xpath=//input[@item_title="${ar_id}"]
    Click button                 xpath=//input[@value="Verify"]
    Wait until page contains     saved
