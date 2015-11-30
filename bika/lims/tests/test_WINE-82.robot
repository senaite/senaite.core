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
*** Test Cases ***

WINE-82: An invalid entry in the Sample field should not cause an error
    [Documentation]  Even though all required fields are completed on Request
    ...   New Analyses page, the save button underneath list of analyses does
    ...   not appear to do anything and requests cannot be completed. This
    ...   happens if all columns are completed or only one or two. No error
    ...   message appears, nothing appears to happen!
  Enable autologin as  LabClerk
  Given an ar add form in client-1 with columns layout and 1 ars
   When I select Borehole 12 from the SamplePoint combogrid in column 0
   When I select Water from the SampleType combogrid in column 0
    And I select Rita from the Contact combogrid in column 0
    And select date    css=#SamplingDate-0    1
    And Input text     css=#Sample-0          asdf
    And I expand the lab Metals category
    And I select the Calcium service in column 0
    click button  Save
    wait until page contains   Analysis request H2O-0001-R01 was successfully created


*** Keywords ***
