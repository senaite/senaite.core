Theme View
----------

The `senaite_theme` view delivers the configured icons. By URL it only
calls its icon functions with exactly one icon name, in page templates it
only traverses to the functions of `ISenaiteTheme`.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t ThemeView


Test Setup
..........

    >>> from bika.lims.utils import get_image
    >>> from senaite.core.browser.globals.theme import SenaiteTheme
    >>> from zExceptions import NotFound
    >>> from zope.traversing.interfaces import TraversalError

    >>> portal = self.portal
    >>> request = self.request
    >>> portal_url = portal.absolute_url()

Helper to call the view by URL with a subpath and form values:

    >>> def call(*subpath, **form):
    ...     request.form.clear()
    ...     request.form.update(form)
    ...     view = SenaiteTheme(portal, request)
    ...     for name in subpath:
    ...         view.publishTraverse(request, name)
    ...     return view()

Helper to check that a call by URL is not found:

    >>> def not_found(*subpath):
    ...     try:
    ...         call(*subpath)
    ...     except NotFound:
    ...         return True
    ...     return False

    >>> theme = SenaiteTheme(portal, request)
    >>> icon_path = theme.icon_path("sample")
    >>> icon_url = "{}/{}".format(portal_url, icon_path)


Icon functions by URL
.....................

The icon functions return the icon for the name in the subpath:

    >>> call("icon_url", "sample") == icon_url
    True

    >>> call("icon_path", "sample") == icon_path
    True

Form values are passed to the function, e.g. as attributes of the tag:

    >>> print(call("icon_tag", "sample", width="16"))
    <img src=".../icons/sample.svg" width="16" />


Attributes of the icon tag
..........................

The values of the attributes are escaped, so that a value cannot break out
of its attribute:

    >>> print(theme.icon_tag("sample", title='"><b>bold</b>'))
    <img src=".../icons/sample.svg" title="&quot;&gt;&lt;b&gt;bold&lt;/b&gt;" />

    >>> print(theme.icon_tag("sample", title="Fish & Chips"))
    <img src=".../icons/sample.svg" title="Fish &amp; Chips" />

The key `css_class` is rendered as `class`, a value containing it is kept:

    >>> print(theme.icon_tag("sample", css_class="icon"))
    <img src=".../icons/sample.svg" class="icon" />

    >>> print(theme.icon_tag("sample", title="css_class"))
    <img src=".../icons/sample.svg" title="css_class" />

Other values than strings are rendered as text and non-ASCII values are
returned as utf-8:

    >>> print(theme.icon_tag("sample", width=16))
    <img src=".../icons/sample.svg" width="16" />

    >>> theme.icon_tag("sample", title=u"Pr\xfcfung")
    '<img src=".../icons/sample.svg" title="Pr\xc3\xbcfung" />'

`get_image` renders the attributes the same way, for an icon of the theme:

    >>> print(get_image("warning.png", title='"><b>bold</b>'))
    <img src=".../icons/warning.svg" ...title="&quot;&gt;&lt;b&gt;bold&lt;/b&gt;"... />

and for an image that is not part of the theme, e.g. the icon for the
comment of a specification:

    >>> print(get_image("comment_ico.png", title='"><b>bold</b>'))
    <img src=".../comment_ico.png" title="&quot;&gt;&lt;b&gt;bold&lt;/b&gt;"/>


Default icon
............

An unknown icon name returns the icon for not found icons:

    >>> print(theme.icon_url("unknown"))
    http://nohost/plone/.../icons/icon-not-found.svg

Another icon can be set as default, also by URL:

    >>> print(theme.icon_url("unknown", default="sample"))
    http://nohost/plone/.../icons/sample.svg

    >>> print(call("icon_url", "unknown", default="sample"))
    http://nohost/plone/.../icons/sample.svg

The default is not rendered as attribute of the icon tag:

    >>> print(theme.icon_tag("unknown", default="sample", width=16))
    <img src=".../icons/sample.svg" width="16" />

An unknown default returns the icon for not found icons as well:

    >>> print(theme.icon_url("unknown", default="unknown"))
    http://nohost/plone/.../icons/icon-not-found.svg


Icon response
.............

The icon is returned with headers that allow the browser to cache it:

    >>> data = call("icon", "sample")
    >>> data == theme.icon_data("sample")
    True

    >>> response = request.response
    >>> print(response.getHeader("Content-Type"))
    image/svg+xml

    >>> print(response.getHeader("Cache-Control"))
    public, max-age=86400

    >>> last_modified = response.getHeader("Last-Modified")

A browser that has the icon already gets an empty response:

    >>> request.environ["HTTP_IF_MODIFIED_SINCE"] = last_modified
    >>> call("icon", "sample")
    ''

    >>> response.getStatus()
    304

A browser with an older version or an invalid date gets the icon:

    >>> response.setStatus(200)
    >>> request.environ["HTTP_IF_MODIFIED_SINCE"] = (
    ...     "Thu, 01 Jan 1970 00:00:00 GMT")
    >>> call("icon", "sample") == data
    True

    >>> request.environ["HTTP_IF_MODIFIED_SINCE"] = "invalid"
    >>> call("icon", "sample") == data
    True

    >>> del request.environ["HTTP_IF_MODIFIED_SINCE"]


Other calls by URL are not found
................................

A call without a subpath:

    >>> not_found()
    True

An unknown function:

    >>> not_found("unknown", "sample")
    True

A private method or an attribute of the view:

    >>> not_found("_get_last_modified", "sample")
    True

    >>> not_found("context")
    True

The icon mapping, which takes no icon name:

    >>> not_found("icons", "sample")
    True

An icon function without an icon name or with more segments:

    >>> not_found("icon_url")
    True

    >>> not_found("icon_url", "sample", "more")
    True


Traversal in page templates
...........................

A path like `senaite_theme/icon_url/sample` traverses to the function and
then calls it with the icon name:

    >>> traverser = theme.traverse("icon_url", ["sample"])
    >>> traverser.traverse("sample", []) == icon_url
    True

The icon mapping can be traversed as well:

    >>> "sample" in theme.traverse("icons", [])()
    True

Other names are not traversed:

    >>> def not_traversed(name):
    ...     try:
    ...         theme.traverse(name, [])
    ...     except TraversalError:
    ...         return True
    ...     return False

    >>> not_traversed("portal")
    True

    >>> not_traversed("context")
    True
