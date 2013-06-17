AnalysisRequestQuery tests
==========================

AnalysisRequestQuery uses plone.app.collection to make a query form for
AnalysisRequests.

Some test setup.

    >>> from plone.app.testing import login
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_NAME
    >>> from plone.app.testing import TEST_USER_PASSWORD
    >>> login(layer['portal'], TEST_USER_NAME)
    >>> setRoles(layer['portal'], TEST_USER_ID, ('Manager',))
    >>> layer['portal'].restrictedTraverse('@@authenticator')
    <Products.Five.metaclass.AuthenticatorView object at ...>

And a test browser.

    >>> from plone.testing.z2 import Browser
    >>> browser = Browser(layer['app'])
    >>> browser.open('http://nohost/plone/login_form')
    >>> browser.getControl(name='__ac_name').value = TEST_USER_NAME
    >>> browser.getControl(name='__ac_password').value = TEST_USER_PASSWORD
    >>> browser.getControl('Log in').click()
    >>> 'You are now logged in' in browser.contents
    True

Create a new AnalysisRequestQuery object.

    >>> queries = layer['portal'].queries
    >>> queries.invokeFactory('AnalysisRequestQuery', id='q1', title='Q 1')
    'q1'
    >>> queries.q1.processForm()
    >>> import transaction
    >>> transaction.commit()


All fields from analysisrequestquery.xml should be present in the rendered
form.

  >>> browser.open("http://nohost/plone/queries/q1/edit")
  >>> import pdb

