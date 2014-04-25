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

Test Manage Analyses
    Log in     test_labmanager    test_labmanager
    Create AnalysisRequests
    H2O-0001-R01 state should be sample_due
    Set Selenium Timeout        300
    Add new analysis H2O-0001-R01 Metals Copper
    Set Selenium Timeout        10
    H2O-0001-R01 state should be sample_due
    Receive H2O-0001-R01
    H2O-0001-R01 state should be sample_received
    Add new analysis H2O-0001-R01 Metals Iron
    H2O-0001-R01 state should be sample_received
    Submit H2O-0001-R01
    H2O-0001-R01 state should be to_be_verified
    Add new analysis H2O-0001-R01 Metals Zinc
    H2O-0001-R01 state should be sample_received
    Input text                   xpath=//tr[@keyword='Zn']//input[@type='text']   10
    Press Key                    xpath=//tr[@keyword='Zn']//input[@type='text']   \t
    Click button                 xpath=//input[@value="Submit for verification"]
    Wait until page contains     saved
    H2O-0001-R01 state should be to_be_verified


*** Keywords ***

Start browser
    Open browser                http://localhost:55001/plone
    Set selenium speed          ${SELENIUM_SPEED}

Create AnalysisRequests
    [Documentation]     Add and receive some ARs.
    ...                 H2O-0001-R01  Bore
    ...                 H2O-0002-R01  Bruma
    @{time} =                   Get Time        year month day hour min sec
    Go to                       ${PLONEURL}/clients/client-1
    Wait until page contains element    css=body.portaltype-client
    Click Link                  Add
    Wait until page contains    Request new analyses
    sleep    1
    Select Date                 ar_0_SamplingDate           1
    select from dropdown        ar_0_Contact                Rita
    Select from dropdown        ar_0_Template               Bore
    sleep    2
    Set Selenium Timeout        30
    Click Button                Save
    Wait until page contains    created
    Set Selenium Timeout        10

${ar_id} state should be ${state_id}
    Go to                        http://localhost:55001/plone/clients/client-1/${ar_id}
    Page should contain element  css=span.state-${state_id}

Add new analysis ${ar_id} ${category} ${title}
    Go to                       http://localhost:55001/plone/clients/client-1/${ar_id}/analyses
    ${count} =      Get Matching XPath Count                      //th[@cat=${category} and contains(@class, 'collapsed')]
    Run Keyword If  '${count}' == '1'    Click element        xpath=//th[@cat=${category} and contains(@class, 'collapsed')]
    sleep                     1

    Select checkbox           xpath=//input[@item_title="${title}"]
    Capture Page Screenshot
    Click element             xpath=//input[@transition="save_analyses_button"]
    Wait until page contains  saved

Receive ${ar_id}
    Go to                        http://localhost:55001/plone/clients/client-1/analysisrequests
    Wait until page contains     ${ar_id}
    Select checkbox              xpath=//input[@item_title="${ar_id}"]
    Click button                 xpath=//input[@value="Receive sample"]
    Wait until page contains     saved

Submit ${ar_id}
    Go to                        http://localhost:55001/plone/clients/client-1/analysisrequests
    Wait until page contains     ${ar_id}
    Click link                   ${ar_id}
    Wait until page contains     Results not requested
    Input text                   xpath=//tr[@keyword='Ca']//input[@type='text']   10
    Input text                   xpath=//tr[@keyword='Cu']//input[@type='text']   10
    Input text                   xpath=//tr[@keyword='Fe']//input[@type='text']   10
    Input text                   xpath=//tr[@keyword='Mg']//input[@type='text']   10
    Press Key                    xpath=//tr[@keyword='Mg']//input[@type='text']   \t
    Click button                 xpath=//input[@value="Submit for verification"]
    Wait until page contains     saved

Retract ${ar_id}
    Go to                        http://localhost:55001/plone/clients/client-1/analysisrequests
    Wait until page contains     ${ar_id}
    Select checkbox              xpath=//input[@item_title="${ar_id}"]
    Click button                 xpath=//input[@value="Retract"]
    Wait until page contains     saved

Verify ${ar_id}
    Go to                        http://localhost:55001/plone/clients/client-1/analysisrequests
    Wait until page contains     ${ar_id}
    Select checkbox              xpath=//input[@item_title="${ar_id}"]
    Click button                 xpath=//input[@value="Verify"]
    Wait until page contains     saved
