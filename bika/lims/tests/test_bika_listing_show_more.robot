 *** Settings ***

Library         BuiltIn
Library         Selenium2Library  timeout=5  implicit_wait=0.2
Library         String
Resource        keywords.txt
Resource        plone/app/robotframework/selenium.robot
Library         Remote  ${PLONEURL}/RobotRemote
Variables       plone/app/testing/interfaces.py
Variables       bika/lims/tests/variables.py

Suite Setup     Start browser
Suite Teardown  Close All Browsers

Library          DebugLibrary

*** Variables ***

*** Test Cases ***


Test show_more button
    Enable autologin as  LabManager
    set autologin username  test_labmanager
    Create Object   clients  Client  c01   title=Client01
    Create Object   clients  Client  c02   title=Client02
    Create Object   clients  Client  c03   title=Client03
    Create Object   clients  Client  c04   title=Client04
    Create Object   clients  Client  c05   title=Client05
    Create Object   clients  Client  c06   title=Client06
    Create Object   clients  Client  c07   title=Client07
    Create Object   clients  Client  c08   title=Client08
    Create Object   clients  Client  c09   title=Client09
    Create Object   clients  Client  c10   title=Client10
    go to    ${PLONEURL}/clients?list_pagesize=5
    page should not contain      Client10
    click element      css=.bika_listing_show_more
    wait until page contains     Client10

*** Keywords ***

Start browser
    Open browser                        ${PLONEURL}  chrome
    Set selenium speed                  ${SELENIUM_SPEED}
