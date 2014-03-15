*** Settings ***

Library                 Selenium2Library  timeout=10  implicit_wait=0.1
Library                 Collections
Library                 DebugLibrary
Library                 DebugLibrary
Resource                keywords.txt
Variables               plone/app/testing/interfaces.py

Suite Setup             Start browser
Suite Teardown          Close All Browsers

*** Variables ***

${SELENIUM_SPEED}  0
${PLONEURL}        http://localhost:55001/plone

*** Test Cases ***

View client screens as Client Contact.

    Log in                     ritamo    ritamo
    sleep      1

    Go to                      ${PLONEURL}/clients/client-1/ar_add?col_count=1
    ${ar_id}=                  Complete ar_add form with template    Lab: Borehole 12 Hardness

    Go to                      ${PLONEURL}/clients/client-1/edit
    Wait until page contains   Preferences
    Click element              fieldsetlegend-preferences
    Select from list           DefaultCategories:list        Metals
    Click button               Save
    Wait until page contains   Changes saved.

    # Debug

    Go to                      ${PLONEURL}/clients/client-1/samples
    Wait until page contains   H2O14-0001
    Click link                 H2O14-0001
    Wait until page contains   Magnesium

    Go to                      ${PLONEURL}/clients/client-1/samplepoints
    Click link                 Add
    Wait until page contains   Add Sample Point
    Input text                 title     Test Sample Point 1
    Click button               Save
    Wait until page contains   Changes saved.

    # There are no batches, but we should be able to at least visit this page
    Go to                      ${PLONEURL}/clients/client-1/batches
    Wait until page contains   Cancelled

    Go to                      ${PLONEURL}/clients/client-1/analysisrequests
    Wait until page contains   H2O14-0001-R01
    Click link                 H2O14-0001-R01
    Wait until page contains   H2O14-0001-P1

    Go to                      ${PLONEURL}/clients/client-1/analysisprofiles
    Click link                 Add
    Wait until page contains   Add Analysis Profile
    Input text                 title     Test Analysis Profile 1
    Click link                 Analyses
    Select Checkbox            xpath=(//input[contains(@id, '_cb_')])[1]
    Select Checkbox            xpath=(//input[contains(@id, '_cb_')])[2]
    Select Checkbox            xpath=(//input[contains(@id, '_cb_')])[3]
    Click button               Save
    Wait until page contains   Changes saved.

    Go to                      ${PLONEURL}/clients/client-1/artemplates
    Click link                 Add
    Wait until page contains   Add AR Template
    Input text                 title     Test AR Template 1
    Click link                 Analyses
    Select from list           AnalysisProfile:list   Test Analysis Profile 1
    Click button               Save
    Wait until page contains   Changes saved.


*** Keywords ***

Start browser
    Open browser        ${PLONEURL}/login_form
    Set selenium speed  ${SELENIUM_SPEED}

Complete ar_add form with template
    [Arguments]  ${template}=

    wait until page contains element    ar_0_SamplingDate

    @{time} =               Get Time        year month day hour min sec

    SelectDate                  ar_0_SamplingDate     @{time}[2]
    Select from list            ar_0_ARTemplate       ${template}
    sleep    1

    Set Selenium Timeout        30
    Click Button                Save
    Wait until page contains    created
    Set Selenium Timeout        10
    ${ar_id} =                  Get text      //dl[contains(@class, 'portalMessage')][2]/dd
    ${ar_id} =                  Set Variable  ${ar_id.split()[2]}
    [return]                    ${ar_id}
