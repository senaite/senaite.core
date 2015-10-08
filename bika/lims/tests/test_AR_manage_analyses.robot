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

Test Manage Analyses
    Log in                            test_labmanager    test_labmanager

    # Create an AR: "H2O-0001-R01"
    Go to                             ${PLONEURL}/clients/client-1
    Wait until page contains element  css=body.portaltype-client
    Click Link                        Add
    Wait until page contains          Request new analyses
    select from dropdown              ar_0_Contact                Rita
    Select from dropdown              ar_0_Template               Bore
    Select Date                       ar_0_SamplingDate           1
    Set Selenium Timeout              30
    Click Button                      Save
    Wait until page contains          created
    Set Selenium Timeout              5
    H2O-0001-R01 is sample_due

    # add new analysis, state remains sample_due. obviously.
    Add new analysis H2O-0001-R01 Metals Copper
    H2O-0001-R01 is sample_due

    # receive AR normally
    Receive H2O-0001-R01
    H2O-0001-R01 is sample_received

    # Add new analysis, state should remain sample_received. obviously.
    Add new analysis H2O-0001-R01 Metals Iron
    H2O-0001-R01 is sample_received

    # Submit results, state changes to to_be_verified.
    Go to                             ${PLONEURL}/clients/client-1/analysisrequests
    Wait until page contains          H2O-0001-R01
    Click link                        H2O-0001-R01    # click instead of url access to test view redirection.
    Wait until page contains          Results not requested
    Input text                        xpath=//tr[@keyword='Ca']//input[@type='text']   10
    Input text                        xpath=//tr[@keyword='Cu']//input[@type='text']   10
    Input text                        xpath=//tr[@keyword='Fe']//input[@type='text']   10
    Input text                        xpath=//tr[@keyword='Mg']//input[@type='text']   10
    Press Key                         xpath=//tr[@keyword='Mg']//input[@type='text']   \t
    Click button                      xpath=//input[@value="Submit for verification"]
    Wait until page contains          saved
    H2O-0001-R01 is to_be_verified

    # Add an analysis for the 'Ƭest' service.
    # It does not exist in AR Spec, so input values must be ""
    Go to                         ${PLONEURL}/clients/client-1/H2O-0001-R01/analyses
    ${count} =        Get Matching XPath Count              //th[@cat='Metals' and contains(@class, 'collapsed')]
    Run Keyword If    '${count}' == '1'    Click element    xpath=//th[@cat='Metals' and contains(@class, 'collapsed')]
    # There should be no min/max/error elements with empty values
    Page should contain element     css=[value=''][field='min']
    Page should contain element     css=[value=''][field='max']
    Page should contain element     css=[value=''][field='error']
    Select checkbox           xpath=//input[@item_title="Ƭest"]
    # And now there should be one each of min/max/error, with empty values.
    Page should contain element     css=[value=''][field='min']
    Page should contain element     css=[value=''][field='max']
    Page should contain element     css=[value=''][field='error']
    Click element             xpath=//input[@transition="save_analyses_button"]
    Wait until page contains  saved
    # AR will be retracted to sample_received.
    H2O-0001-R01 is sample_received

    # Submit a value for new analysis, state changes back to to_be_verified
    Input text                        xpath=//tr[@keyword='T']//input[@type='text']   10
    Press Key                         xpath=//tr[@keyword='T']//input[@type='text']   \t
    Click button                      xpath=//input[@value="Submit for verification"]
    Wait until page contains          saved
    H2O-0001-R01 is to_be_verified

*** Keywords ***

${ar_id} is ${state_id}
    Go to                             ${PLONEURL}/clients/client-1/${ar_id}
    Page should contain element       css=span.state-${state_id}

Add new analysis ${ar_id} ${category} ${title}
    Go to                       ${PLONEURL}/clients/client-1/${ar_id}/analyses
    ${count} =      Get Matching XPath Count                      //th[@cat=${category} and contains(@class, 'collapsed')]
    Run Keyword If  '${count}' == '1'    Click element        xpath=//th[@cat=${category} and contains(@class, 'collapsed')]
    sleep                     1
    Select checkbox           xpath=//input[@item_title="${title}"]
    Click element             xpath=//input[@transition="save_analyses_button"]
    Wait until page contains  saved

Receive ${ar_id}
    Go to                        ${PLONEURL}/clients/client-1/analysisrequests
    Wait until page contains     ${ar_id}
    Select checkbox              xpath=//input[@item_title="${ar_id}"]
    Click button                 xpath=//input[@id="receive_transition"]
    Wait until page contains     saved
