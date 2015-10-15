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

Creating secondary AR inside Client Batch, should only show Client's samples
  Enable autologin as  LabManager
  Disable stickers
  Simple AR Creation  client-1  Rita  Water  Metals  Calcium
  Execute transition receive on item H2O-0001-R01 in ARList
  Given an ar add form in client-1 with columns layout and 1 ars
   When I select H2O-0001 from the Sample combogrid in column 0
   Then xpath should match x times   .//input[@disabled]   12
   # We only check that the twelve fields are disabled; assuming that their
   # values are correct.

*** Keywords ***
