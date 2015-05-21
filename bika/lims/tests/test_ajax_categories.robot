*** Settings ***

Library          BuiltIn
Library          Selenium2Library  timeout=10  implicit_wait=0.5
Library          String
Resource         keywords.txt
Library          bika.lims.testing.Keywords
Variables        plone/app/testing/interfaces.py
Variables        bika/lims/tests/variables.py
Suite Setup      Start browser
Suite Teardown   Close All Browsers

*** Variables ***

*** Test Cases ***

Test ajax categories
    Log in                            test_labmanager1   test_labmanager1
    # Ensure that categorized services are on
    Go to                             ${PLONEURL}/bika_setup/edit
    Click element                     css=#fieldsetlegend-analyses
    Select checkbox                   css=#CategoriseAnalysisServices
    Click button                      Save
    # We can do all our tests in the artemplate-1 object
    Go to                             ${PLONEURL}/bika_setup/bika_artemplates/artemplate-1
    Click element                     css=#fieldsetlegend-analyses
    # Check that Metals is auto-expanded on load
    Page should contain element       css=tr[title='Calcium']
    Page should not contain element   css=tr[title='Ecoli']
    # check that a category can be expanded with AJAX
    Click element                     css=th[cat='Microbiology']
    Element should be visible         css=tr[title='Ecoli']
    # Check that retracting the category works
    Click element                     css=th[cat='Microbiology']
    Element should not be visible     css=tr[title='Ecoli']
    # Check that expanding an already-expanded category works
    Click element                     css=th[cat='Microbiology']
    Element should be visible         css=tr[title='Ecoli']
