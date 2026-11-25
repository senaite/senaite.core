Theme View
----------

The `senaite_theme` view delivers the configured icons. By URL it only
calls its icon functions with exactly one icon name, in page templates it
only traverses to the functions of `ISenaiteTheme`.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t ThemeView


Test Setup
..........

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

    >>> 'width="16"' in call("icon_tag", "sample", width="16")
    True


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
