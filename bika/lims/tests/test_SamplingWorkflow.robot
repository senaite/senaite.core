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

# XXX field analyses

Analysis Request with Sampling Workflow on
    Enable Sampling Workflow
    ${ar_id}=                 Add an AR
    Go to                     ${PLONEURL}/clients/client-1/analysisrequests
    page should contain       To Be Sampled
    Go to                     ${PLONEURL}/clients/client-1/H2O-0001-R01

    debug

    Go to                     ${PLONEURL}/clients/client-1/${ar_id}
    Click element             css=.state-to_be_sampled
    sleep    .5
    Click element             css=#workflow-transition-sample
    Page should contain       saved.
    Page should contain       Received

*** Keywords ***

Start browser
    Open browser                        ${PLONEURL}/login_form
    Log in                              test_labmanager         test_labmanager
    Wait until page contains            You are now logged in
    Set selenium speed                  ${SELENIUM_SPEED}

Disable Sampling Workflow
    go to                               ${PLONEURL}/bika_setup/edit
    click link                          Analyses
    unselect checkbox                   SamplingWorkflowEnabled
    click button                        Save

Enable Sampling Workflow
    go to                               ${PLONEURL}/bika_setup/edit
    click link                          Analyses
    select checkbox                     SamplingWorkflowEnabled
    click button                        Save

Add an AR
    Go to                     ${PLONEURL}/clients/client-1
    Click Link                Add
    @{time} =                  Get Time                year month day hour min sec
    SelectDate                 ar_0_SamplingDate       @{time}[2]
    Select From Dropdown       ar_0_SampleType         Water
    Select from dropdown       ar_0_Contact            Rita
    Select from dropdown       ar_0_Priority           High
    Click Element              xpath=//th[@id='cat_field_Water Chemistry']
    Select Checkbox            xpath=//input[@title='Temperature' and @name='ar.0.Analyses:list:ignore_empty:record']
    Click Element              xpath=//th[@id='cat_lab_Water Chemistry']
    Select Checkbox            xpath=//input[@title='Moisture' and @name='ar.0.Analyses:list:ignore_empty:record']
    Click Element              xpath=//th[@id='cat_lab_Metals']
    Select Checkbox            xpath=//input[@title='Calcium' and @name='ar.0.Analyses:list:ignore_empty:record']
    Select Checkbox            xpath=//input[@title='Phosphorus' and @name='ar.0.Analyses:list:ignore_empty:record']
    Set Selenium Timeout       60
    Click Button               Save
    Wait until page contains   created
    ${ar_id} =                 Get text      //dl[contains(@class, 'portalMessage')][2]/dd
    ${ar_id} =                 Set Variable  ${ar_id.split()[2]}
    [return]                   ${ar_id}
