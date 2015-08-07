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

Test Pricelist-AR
    Log in  test_labmanager  test_labmanager

    # Debug

    #Add Pricelist
    Go to                        http://localhost:55001/plone/pricelists
    Wait until page contains     Add
    Click Link                   Add
    Wait until page contains     Add Pricelist
    Input text                   title  All services update.
    select from list             css=#edit_form_effectiveDate_0_year    2014
    select from list             css=#edit_form_effectiveDate_0_month   01
    select from list             css=#edit_form_effectiveDate_0_day     01
    select from list             css=#edit_form_expirationDate_1_year    2019
    select from list             css=#edit_form_expirationDate_1_month   01
    select from list             css=#edit_form_expirationDate_1_day     01
    Click Button                 xpath=//input[@value="Save"]
    Wait until page contains     saved
    # pricelist view should now have all lineitems pre-populated.
    Page should contain          Iron (mg/l)
    Page should contain          10.00
    Page should contain          1.40
    Page should contain          11.40

    # test bulk discount
    Click Link                   Edit
    Wait until page contains     Bulk discount applies
    click element                css=#BulkDiscount_1
    Click Button                 xpath=//input[@value="Save"]
    Wait until page contains     saved
    # old lineitems are gone:
    Page should not contain      10.00
    Page should not contain      1.40
    Page should not contain      11.40
    Page should contain          7.50
    Page should contain          1.05
    Page should contain          8.55

    # test bulk Discount % of 50%
    Click Link                   Edit
    Wait until page contains     Bulk discount applies
    click element                css=#BulkDiscount_2
    Input text                   css=#BulkPrice         50
    Click Button                 xpath=//input[@value="Save"]
    Wait until page contains     saved
    Page should contain          5.00
    Page should contain          0.70
    Page should contain          5.70

*** Keywords ***

