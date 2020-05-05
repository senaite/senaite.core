# -*- coding: utf-8 -*-

from plone.app.layout.viewlets.common import GlobalSectionsViewlet as Base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class GlobalSectionsViewlet(Base):
    index = ViewPageTemplateFile("templates/sections.pt")

    _item_markup_template = (
        u'<li class="{id}{has_sub_class} nav-item">'
        u'<a href="{url}" class="nav-link state-{review_state}"{aria_haspopup}>{title}</a>{opener}'  # noqa: E 501
        u'{sub}'
        u'</li>'
    )
    _subtree_markup_wrapper = (
        u'<ul class="has_subtree dropdown">{out}</ul>'
    )
