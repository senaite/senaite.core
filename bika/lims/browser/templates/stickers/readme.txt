Ho to create specific content type stickers
===========================================

If you want to create stickers for Content Type, first add the action in the
Content Type xml definition file. You can found this files in
bika/lims/profiles/default/types/*xml

(Please, look at the 'url_expr' part.)

```
<action title="Stickers preview"
        action_id="sticker_preview"
        category="document_actions"
        condition_expr=""
        icon_expr="string:${object_url}/++resource++bika.lims.images/sticker_preview.png"
        link_target="Stickers preview"
        url_expr="string:${object_url}/sticker?filter_by_type=<<type_id>>"
        i18n:attributes="title"
        visible="True">
    <permission value="View"/>
</action>
```

Then create a new folder inside the stickers resource using the <<type_id>>.
