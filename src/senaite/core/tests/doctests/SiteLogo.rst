Site Logo
---------

The `site-logo` view sends the site logo of the SENAITE setup. The browser
may cache the logo and asks with the `ETag` if it has changed.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t SiteLogo


Test Setup
..........

    >>> from plone.formwidget.namedfile.converter import b64encode_file
    >>> from senaite.core.browser.globals.sitelogo import SiteLogo
    >>> from Products.Five.browser import BrowserView
    >>> from senaite.core.interfaces import ISenaiteCore
    >>> from zExceptions import NotFound
    >>> from zope.component import getMultiAdapter
    >>> from zope.interface import alsoProvides
    >>> from zope.viewlet.interfaces import IViewletManager

    >>> portal = self.portal
    >>> request = self.request
    >>> alsoProvides(request, ISenaiteCore)
    >>> response = request.response
    >>> setup = portal.setup

    >>> logo = b'<svg xmlns="http://www.w3.org/2000/svg"></svg>'

Helper to call the view by URL with the filename of the logo:

    >>> def call(filename="logo.svg", etag=None):
    ...     request.environ.pop("HTTP_IF_NONE_MATCH", None)
    ...     if etag:
    ...         request.environ["HTTP_IF_NONE_MATCH"] = etag
    ...     response.setStatus(200)
    ...     view = SiteLogo(portal, request)
    ...     view.publishTraverse(request, filename)
    ...     return view()

Helper to get the logo URL of the toolbar:

    >>> def get_toolbar_logo():
    ...     view = BrowserView(portal, request)
    ...     manager = getMultiAdapter(
    ...         (portal, request, view), IViewletManager, name="plone.toolbar")
    ...     return manager.get_toolbar_logo()


Without site logo
.................

Without a site logo in the setup the view is not found:

    >>> setup.setSiteLogo(None)
    >>> call()
    Traceback (most recent call last):
    ...
    NotFound: site-logo

And the toolbar shows the default logo:

    >>> print(get_toolbar_logo())
    http://nohost/plone/++plone++senaite.core.static/images/senaite.svg


With site logo
..............

    >>> setup.setSiteLogo(b64encode_file("logo.svg", logo))

The view sends the logo with its `ETag` and lets the browser cache it:

    >>> call() == logo
    True

    >>> response.getStatus()
    200

    >>> response.getHeader("Content-Type")
    'image/svg+xml'

    >>> response.getHeader("Cache-Control")
    'public, max-age=86400'

    >>> etag = response.getHeader("ETag")
    >>> etag
    '"..."'

The toolbar links the logo with its version, so that a new logo gets a new
URL:

    >>> url = get_toolbar_logo()
    >>> print(url)
    http://nohost/plone/@@site-logo/logo.svg?v=...

    >>> url.endswith("?v={}".format(etag.strip('"')))
    True


Cached site logo
................

A browser that has the logo already gets a `304 Not Modified` without the
logo:

    >>> call(etag=etag)
    ''

    >>> response.getStatus()
    304

Also when the `ETag` is weak or one of several:

    >>> call(etag="W/{}".format(etag))
    ''

    >>> call(etag='"other", {}'.format(etag))
    ''

A browser with another `ETag` gets the logo:

    >>> call(etag='"other"') == logo
    True

    >>> response.getStatus()
    200


Changed site logo
.................

A new logo gets a new `ETag` and a new URL in the toolbar:

    >>> new_logo = b'<svg xmlns="http://www.w3.org/2000/svg"><g/></svg>'
    >>> setup.setSiteLogo(b64encode_file("logo.svg", new_logo))

    >>> call(etag=etag) == new_logo
    True

    >>> response.getHeader("ETag") == etag
    False

    >>> get_toolbar_logo() == url
    False
