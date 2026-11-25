HTML Attributes
---------------

`render_html_attributes` renders the attributes of the html tags built in
Python, e.g. by `get_image`, `get_link` or the `icon_tag` of the theme
view. The values are escaped, so that a value cannot break out of its
attribute.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t HTMLAttributes


Test Setup
..........

    >>> from bika.lims.utils import get_image
    >>> from bika.lims.utils import render_html_attributes
    >>> from senaite.core.browser.globals.theme import SenaiteTheme

    >>> portal = self.portal
    >>> request = self.request


Render attributes
.................

    >>> print(render_html_attributes(title="Sample"))
    title="Sample"

The key `css_class` is rendered as `class`:

    >>> print(render_html_attributes(css_class="icon"))
    class="icon"

Other values than strings are rendered as text:

    >>> print(render_html_attributes(width=16))
    width="16"

Non-ASCII values are returned as utf-8:

    >>> render_html_attributes(title=u"Pr\xfcfung")
    'title="Pr\xc3\xbcfung"'

No attributes render an empty string:

    >>> render_html_attributes()
    ''


Escape the values
.................

Quotes and markup in a value are escaped:

    >>> print(render_html_attributes(title='"><script>alert(1)</script>'))
    title="&quot;&gt;&lt;script&gt;alert(1)&lt;/script&gt;"

    >>> print(render_html_attributes(title="Fish & Chips"))
    title="Fish &amp; Chips"

A value containing `css_class` is kept as it is:

    >>> print(render_html_attributes(title="css_class"))
    title="css_class"


Escape the values of icon tags
..............................

The theme view renders the attributes of its icon tags the same way:

    >>> theme = SenaiteTheme(portal, request)
    >>> print(theme.icon_tag("sample", title='"><b>bold</b>'))
    <img src=".../icons/sample.svg" title="&quot;&gt;&lt;b&gt;bold&lt;/b&gt;" />

And so does `get_image` for an icon of the theme:

    >>> print(get_image("warning.png", title='"><b>bold</b>'))
    <img src=".../icons/warning.svg" ...title="&quot;&gt;&lt;b&gt;bold&lt;/b&gt;"... />

and for an image that is not part of the theme, e.g. the icon for the
comment of a specification:

    >>> print(get_image("comment_ico.png", title='"><b>bold</b>'))
    <img src=".../comment_ico.png" title="&quot;&gt;&lt;b&gt;bold&lt;/b&gt;"/>
