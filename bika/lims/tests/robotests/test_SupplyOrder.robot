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

Test client supply order as LabManager
    Enable autologin as  LabManager
    # https://jira.bikalabs.com/browse/LIMS-1827
    Given a blank order form in client-1
     When I enter 1 for product Glass Container
      and I select the contact Ŝarel Seemonster
      and I submit the new order
    page should contain   Seemonster
    Then when I trigger dispatch transition
    page should contain  Item state changed.

Test client supply order as Client Contact
    Enable autologin as  Owner
    Set autologin username   ritamo

    Given a blank order form in client-1
     Then I can not select the contact Rita Mohale  # cannot select own self?
      and I can not select the contact Johanna Smith
      and I select the contact Ŝarel Seemonster
     Then when I enter 4 for product Glass Container
      and I enter 3 for product Glass Pipet
     subtotal is 430.36
     vat is 60.25
     total is 490.61
     Then when I submit the new order
     page should contain   Seemonster


*** Keywords ***

# --- Given ------------------------------------------------------------------

a blank order form in ${client_id}
    [Documentation]  Load a fresh Order form
    go to  ${PLONEURL}/clients/${client_id}/portal_factory/SupplyOrder/xxx/edit
    wait until page contains  xxx

# --- When -------------------------------------------------------------------

I enter ${nr} for product ${product_title}
    [Documentation]  Simply input the value for this product
    input text   xpath=.//input[@data-product_title='${product_title}']   ${nr}
    press key    xpath=.//input[@data-product_title='${product_title}']   \t

I submit the new order
    [Documentation]  Save the order and wait for the submission to complete
    click button  Save
    wait until page contains  Order pending

I trigger ${transitionId} transition
    Element Should Be Visible  css=dl#plone-contentmenu-workflow span
    Element Should Not Be Visible  css=dl#plone-contentmenu-workflow dd.actionMenuContent
    Click link  css=dl#plone-contentmenu-workflow dt.actionMenuHeader a
    Wait until keyword succeeds  1  5  Element Should Be Visible  css=dl#plone-contentmenu-workflow dd.actionMenuContent
    Click Link  workflow-transition-${transitionId}

# --- Then -------------------------------------------------------------------

I select the contact ${contact}
    [Documentation]  See that a contact is available for selection
    wait until page contains element  css=#Contact
    Input text  css=#Contact  ${contact}
    sleep  1
    Click Element  xpath=//div[contains(@class,'cg-colItem')][1]

I can not select the contact ${contact}
    [Documentation]  See that a contact is not available for selection
    wait until page contains element  css=#Contact
    Input text  css=#Contact  ${contact}
    sleep  1
    Element should not be visible   xpath=//div[contains(@class,'cg-colItem')][1]

status message should be ${message}
    wait until page contains element  css=dl.portalMessage dt  Info
    wait until page contains element  css=dl.portalMessage dd  ${message}

subtotal is ${nr}
    [Documentation]  Verify the subtotal is calculated correctly
    element text should be  css=span.subtotal  ${nr}

vat is ${nr}
    [Documentation]  Verify the vat is calculated correctly
    element text should be  css=span.vat  ${nr}

total is ${nr}
    [Documentation]  Verify the total is calculated correctly
    element text should be  css=span.total  ${nr}

