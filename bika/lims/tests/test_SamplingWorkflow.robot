*** Settings ***

Library          Selenium2Library  timeout=5  implicit_wait=0.5
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

Sampler login
# /samples List should contain all to_be_sampled samples
    Enable Sampling Workflow
    ${ar_id}=                         Add an AR

    Log out
    Log in                            test_sampler1  test_sampler1
    Go to                             ${PLONEURL}/samples

    page should contain               To Be Sampled
    @{time} =                         Get Time                year month day hour min sec
    SelectDate                        css=.listing_string_entry    @{time}[2]
    select from list                  css=.listing_select_entry    Lab Sampler 1
    click element                     css=input[transition="sample"]
    wait until page contains          H2O-0001 is waiting to be received.
    page should not contain element   css=.listing_string_entry
    page should not contain element   css=.listing_select_entry
    page should not contain element   css=input[transition="sample"]

# sample the sample from Samples list
# sample the sample from Sample View
# sample the sample from ARs list
# sample the sample from AR View

sample transition from the AR list
    Log in                            test_labmanager         test_labmanager
    Wait until page contains          You are now logged in
    Enable Sampling Workflow
    ${ar_id}=                         Add an AR
    Go to                             ${PLONEURL}/clients/client-1/analysisrequests
    page should contain               To Be Sampled
    @{time} =                         Get Time                year month day hour min sec
    SelectDate                        css=.listing_string_entry    @{time}[2]
    select from list                  css=.listing_select_entry    Lab Sampler 1
    click element                     css=input[transition="sample"]
    wait until page contains          H2O-0001 is waiting to be received.
    page should not contain element   css=.listing_string_entry
    page should not contain element   css=.listing_select_entry
    page should not contain element   css=input[transition="sample"]

sample transition from the Sample list
    Log in                            test_labmanager         test_labmanager
    Wait until page contains          You are now logged in
    Enable Sampling Workflow
    ${ar_id}=                         Add an AR
    Go to                             ${PLONEURL}/clients/client-1/samples
    page should contain               To Be Sampled
    @{time} =                         Get Time                year month day hour min sec
    SelectDate                        css=.listing_string_entry    @{time}[2]
    select from list                  css=.listing_select_entry    Lab Sampler 1
    click element                     css=input[transition="sample"]
    wait until page contains          H2O-0001 is waiting to be received.
    page should not contain element   css=.listing_string_entry
    page should not contain element   css=.listing_select_entry
    page should not contain element   css=input[transition="sample"]

AR view with field analyses
    Log in                            test_labmanager         test_labmanager
    Wait until page contains          You are now logged in
    Enable Sampling Workflow
    ${ar_id}=                         Add an AR
    Go to                             ${PLONEURL}/clients/client-1/analysisrequests
    page should contain               To Be Sampled
    Go to                             ${PLONEURL}/clients/client-1/H2O-0001-R01
    click element                     css=.label-state-to_be_sampled > a
    Click element                     css=a#workflow-transition-sample
    sleep                             1
    Page should contain               Sampler is required
    Page should contain               Date Sampled is required
    @{time} =                         Get Time          year month day hour min sec
    SelectDate                        DateSampled       @{time}[2]
    Select from list                  Sampler           Lab Sampler 1
    click element                     css=.label-state-to_be_sampled > a
    Click element                     css=a#workflow-transition-sample
    sleep                             1
    page should contain               There are field analyses without submitted results
    page should contain element       css=.label-state-sample_due
    Page should not contain           To Be Sampled
    Page should not contain           to_be_sampled
    input text                        css=input.listing_string_entry        5
    select checkbox                   css=#field_analyses_select_all
    click element                     css=input[transition="submit"]
    Wait until page contains          To be verified

Sample View
    Log in                            test_labmanager         test_labmanager
    Wait until page contains          You are now logged in
    Enable Sampling Workflow
    ${ar_id}=                         Add an AR
    Go to                             ${PLONEURL}/clients/client-1/samples
    page should contain               To Be Sampled
    Go to                             ${PLONEURL}/clients/client-1/H2O-0001
    click element                     css=.label-state-to_be_sampled > a
    Click element                     css=a#workflow-transition-sample
    sleep                             1
    Page should contain               Sampler is required
    Page should contain               Date Sampled is required
    @{time} =                         Get Time          year month day hour min sec
    SelectDate                        DateSampled       @{time}[2]
    Select from list                  Sampler           Lab Sampler 1
    click element                     css=.label-state-to_be_sampled > a
    Click element                     css=a#workflow-transition-sample
    sleep                             1
    page should contain element       css=.label-state-sample_due
    Page should not contain           To Be Sampled
    Page should not contain           to_be_sampled

*** Keywords ***

Disable Sampling Workflow
    go to                             ${PLONEURL}/bika_setup/edit
    click link                        Analyses
    unselect checkbox                 SamplingWorkflowEnabled
    click button                      Save

Enable Sampling Workflow
    go to                             ${PLONEURL}/bika_setup/edit
    click link                        Analyses
    select checkbox                   SamplingWorkflowEnabled
    click button                      Save

Add an AR
    Go to                             ${PLONEURL}/clients/client-1/portal_factory/AnalysisRequest/Request%20new%20analyses/ar_add
    Wait until page contains          Request new analyses
    @{time} =                         Get Time                year month day hour min sec
    SelectDate                        css=#ar_0_SamplingDate       @{time}[2]
    Select From Dropdown              css=#ar_0_SampleType         Water
    Select from dropdown              css=#ar_0_Contact            Rita
    Select from dropdown              css=#ar_0_Priority           High
    Click Element                     xpath=//th[@id='cat_field_Water Chemistry']
    Select Checkbox                   xpath=//input[@title='Temperature' and @name='ar.0.Analyses:list:ignore_empty:record']
    Click Element                     xpath=//th[@id='cat_lab_Water Chemistry']
    Select Checkbox                   xpath=//input[@title='Moisture' and @name='ar.0.Analyses:list:ignore_empty:record']
    Click Element                     xpath=//th[@id='cat_lab_Metals']
    Select Checkbox                   xpath=//input[@title='Calcium' and @name='ar.0.Analyses:list:ignore_empty:record']
    Select Checkbox                   xpath=//input[@title='Phosphorus' and @name='ar.0.Analyses:list:ignore_empty:record']
    Set Selenium Timeout              30
    Click Button                      Save
    Wait until page contains          created
    Set Selenium Timeout              5
    ${ar_id} =                        Get text      //dl[contains(@class, 'portalMessage')][2]/dd
    ${ar_id} =                        Set Variable  ${ar_id.split()[2]}
    [return]                          ${ar_id}
