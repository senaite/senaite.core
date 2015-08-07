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

Create AR with hidden attributes
    # Hide Attributes
    enable autologin as  Manager
    Go to                       ${PLONEURL}/portal_registry/edit/bika.lims.hiddenattributes
    Click Button                Add
    Input Text                 form-widgets-value-0     AnalysisRequest\nClientOrderNumber\ngetClientOrderNumber\nSamplingDeviation\nAdHoc\nInvoiceExclude\nSamplePoint
    Click Button                Add
    Input Text                 form-widgets-value-1     Sample\nSamplingDeviation\nSamplePoint
    Click Button                Save
    disable autologin

    enable autologin as  LabManager
    # Check hidden fields on AR Add
    Go to                       ${PLONEURL}/clients/client-1
    Wait until page contains element    css=body.portaltype-client

    given an ar add form in client-1 with columns layout and 1 ars
    Page should not contain     Sample Point
    Page should not contain     Sampling Deviation
    Page should not contain     Client Order Number
    Page should not contain     Ad-Hoc
    Page should not contain     Invoice Exclude

    ${ar_id}=          Create Primary AR
    Check hidden fields on AR view ${ar_id}
    Check hidden fields on AR invoice ${ar_id}
    
*** Keywords ***

Create Primary AR
    given an ar add form in client-1 with columns layout and 1 ars
    select date  SamplingDate-0  1
    I select Rita from the Contact combogrid in column 0
    I select Bore from the Template combogrid in column 0
    Click Button                Save
    wait until page contains element  xpath=.//dd[contains(text(), 'created')]
    ${dd_text} =  Get text  xpath=.//dd[contains(text(), 'created')]
    ${ar_id} =  Set Variable  ${dd_text.split()[2]}
    [return]  ${ar_id}

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
