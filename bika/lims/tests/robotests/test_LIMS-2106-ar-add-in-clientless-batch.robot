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
*** Keywords ***

Create Batch
    go to  ${PLONEURL}/batches/portal_factory/Batch/xxx/edit
    click button   Save

Simple AR Creation in Batch
    [Documentation]  Create a simple AR
    [Arguments]  ${batch_id}
    ...          ${client_title}
    ...          ${Contact}
    ...          ${SampleType}
    ...          ${ASCategory}
    ...          ${ASTitle}
    @{time} =                   Get Time        year month day hour min sec
    given an ar add form in ${batch_id} with columns layout and 1 ars
    I select ${client_title} from the Client combogrid in column 0
    I select ${Contact} from the Contact combogrid in column 0
    Select Date  SamplingDate-0  @{time}[2]
    I select ${SampleType} from the SampleType combogrid in column 0
    I expand the lab ${ASCategory} category
    I select the ${ASTitle} service in column 0
    Click Button                Save
    wait until page contains element  xpath=.//dd[contains(text(), 'created')]
    ${dd_text} =  Get text  xpath=.//dd[contains(text(), 'created')]
    ${ar_id} =  Set Variable  ${dd_text.split()[2]}
    [return]  ${ar_id}

an ar add form in ${batch_id} with ${layout} layout and ${ar_count} ars
    [Documentation]  Load a fresh AR Add form in a Batch
    go to  ${PLONEURL}/batches/${batch_id}/portal_factory/AnalysisRequest/xxx/ar_add
    wait until page contains  xxx

*** Test Cases ***


Attribute error when adding AR inside batch if batch has no client
  Enable autologin as  LabManager
  Disable stickers
  Create Batch
  Simple AR Creation in Batch  B-001  Happy Hills  Rita  Water  Metals  Calcium
  Execute transition receive on item H2O-0001-R01 in ARList

*** Keywords ***
