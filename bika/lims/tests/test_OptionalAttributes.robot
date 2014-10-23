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

${ar_factory_url}  portal_factory/AnalysisRequest/Request%20new%20analyses/ar_add

*** Test Cases ***

Create AR with hidden attributes
    Hide Attributes
    Check hidden fields on AR Add
    ${ar_id}=          Create Primary AR
    Check hidden fields on AR view ${ar_id}
    Check hidden fields on AR invoice ${ar_id}
    

*** Keywords ***

Start browser
    Open browser                        ${PLONEURL}/login_form
    Set selenium speed                  ${SELENIUM_SPEED}

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
    sleep   1
    Select Date                 ar_0_SamplingDate           @{time}[2]
    sleep   1
    Select from dropdown        ar_0_Contact                Rita
    sleep   1
    Select from dropdown        ar_0_Template               Bore
    sleep   1
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
    Go to                       http://localhost:55001/plone/clients/client-1/H2O-0001
    Page should not contain     Sample Point
    Page should not contain     Sampling Deviation
    Page should not contain     Client SID
    Page should not contain     Ad-Hoc
