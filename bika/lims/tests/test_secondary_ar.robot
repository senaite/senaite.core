*** Settings ***

Library                 Selenium2Library  timeout=2  implicit_wait=0.2
Library  Remote  ${PLONE_URL}/RobotRemote
Resource                keywords.txt
Variables               plone/app/testing/interfaces.py
Suite Setup             Start browser
Suite Teardown          Close All Browsers

*** Variables ***

${SELENIUM_SPEED}  0
${PLONEURL}        http://localhost:55001/plone
${ar_factory_url}  portal_factory/AnalysisRequest/Request new analyses/ar_add

*** Test Cases ***

Create two different ARs from the same sample.
    Create AR
    Create Secondary AR
    In a client context, only allow selecting samples from that client.

*** Keywords ***

Start browser
    Log in                      test_labmanager  test_labmanager
    Set selenium speed   ${SELENIUM_SPEED}
    Open browser         ${PLONEURL}/clients

Create AR
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
    Select checkbox             xpath=//input[@item_title="${ar_id}"]
    Click button                xpath=//input[@value="Receive sample"]
    Wait until page contains    saved
    [return]                    ${ar_id}


Create Secondary AR
    @{time} =                   Get Time        year month day hour min sec
    Go to                       ${PLONEURL}/clients/client-1
    Wait until page contains element    css=body.portaltype-client
    Click Link                  Add
    Wait until page contains    Request new analyses
    Select from dropdown        ar_0_Contact                Rita
    Select from dropdown        ar_0_Template               Bruma
    select from dropdown        ar_0_Sample
    Set Selenium Timeout        30
    Click Button                Save
    Set Selenium Timeout        2
    Wait until page contains    created
    ${ar_id} =                  Get text      //dl[contains(@class, 'portalMessage')][2]/dd
    ${ar_id} =                  Set Variable  ${ar_id.split()[2]}
    [return]                    ${ar_id}


In a client context, only allow selecting samples from that client.
    @{time} =                   Get Time        year month day hour min sec
    Go to                       ${PLONEURL}/clients/client-2
    Wait until page contains element    css=body.portaltype-client
    Click Link                  Add
    Wait until page contains    Request new analyses
    Select from dropdown        ar_0_Contact               Johanna
    Select from dropdown        ar_0_Template              Bore    1
    Run keyword and expect error
    ...   ValueError: Element locator 'xpath=//div[contains(@class,'cg-colItem')][1]' did not match any elements.
    ...   Select from dropdown        ar_0_Sample
