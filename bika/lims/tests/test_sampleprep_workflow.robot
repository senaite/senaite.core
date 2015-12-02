*** Settings ***

Library          BuiltIn
Library          Selenium2Library  timeout=5  implicit_wait=0.2
Library          String
Resource         keywords.txt
Library          bika.lims.testing.Keywords
Variables        plone/app/testing/interfaces.py
Variables        bika/lims/tests/variables.py
Suite Setup      Start browser
#Suite Teardown   Close All Browsers
Library          DebugLibrary

*** Variables ***

${factory_url}  ${PLONEURL}/clients/client-1/portal_factory/AnalysisRequest/xxx/ar_add

*** Test Cases ***

Test sampleprep_simple workflow - straight through
    Log in                       test_labmanager         test_labmanager
    wait until page contains     logged in
    Disable Print Page
    ${ar_id}=                    Create AR with sampleprep_simple
    go to                        ${PLONEURL}/clients/client-1/H2O-0001-R01

    # transition: Recieve.  SHould kick off the SamplePrep workflow.
    click element                css=span.state-sample_due
    click element                css=#workflow-transition-receive

    # check that the title is correctly translate
    page should not contain      sample_prep
    # check that no ojects remained in received state
    page should not contain      Received
    # Primary state should be indicated with (Pending)
    page should contain          (Pending)

    click element                css=span.state-sampleprep
    click element                css=#workflow-transition-complete

    Debug


#
#Test sampleprep_simple workflow - with sampling workflow enabled
#    Log in                       test_labmanager         test_labmanager
#    wait until page contains     logged in
#    Disable Print Page
#    ${ar_id}=                    Create AR with sampleprep_simple
#    go to                        ${PLONEURL}/clients/client-1/H2O-0001-R01
#
#Test AR and Sample PreparationWorkflow field visibility settings
#    Log in                       test_labmanager         test_labmanager
#    wait until page contains     logged in
#    Disable Print Page
#    ${ar_id}=                    Create AR with sampleprep_simple
#    go to                        ${PLONEURL}/clients/client-1/H2O-0001-R01


*** Keywords ***

Create AR with sampleprep_simple
    Go to                       ${factory_url}
    Wait until page contains    xxx
    Select from dropdown        css=#Contact-0                Rita
    Select from dropdown        css=#Template-0               Bore
    Select Date                 css=#SamplingDate-0           1
    Select from list            css=#PreparationWorkflow-0    sampleprep_simple
    Click Button                Save
    Wait until page contains    created
    ${ar_id} =                  Get text      //dl[contains(@class, 'portalMessage')][2]/dd
    ${ar_id} =                  Set Variable  ${ar_id.split()[2]}
    [return]                    ${ar_id}
