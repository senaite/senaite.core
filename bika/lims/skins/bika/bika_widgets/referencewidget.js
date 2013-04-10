jQuery(function($){
    $(document).ready(function(){
        _p = jarn.i18n.MessageFactory('plone');
        _ = jarn.i18n.MessageFactory('bika');

        function referencewidget_lookups(elements){
            // Any reference widgets that don't already have combogrid widgets
            if(elements == undefined){
                var inputs = $("[combogrid_options]").not('.has_combogrid_widget');
            } else {
                var inputs = elements;
            }
            for (var i = inputs.length - 1; i >= 0; i--) {
                var element = inputs[i];
                var options = $.parseJSON($(element).attr('combogrid_options'));
                if(options == '' || options == undefined || options == null){
                    continue;
                }
                options.select = function(event, ui){
                    event.preventDefault();
                    // Set value in activated element (must exist in colModel!)
                    var fieldName = $(this).attr('name');
                    $(this).val(ui.item[$(this).attr('ui_item')]);
                    $(this).attr('uid', ui.item['UID']);
                    $('input[name='+fieldName+'_uid]').val(ui.item['UID']);
                }
                if(window.location.href.search("portal_factory") > -1){
                    options.url = window.location.href.split("/portal_factory")[0] + "/" + options.url;
                }
                options.url = options.url + '?_authenticator=' + $('input[name="_authenticator"]').val();
                options.url = options.url + '&catalog_name=' + $(element).attr('catalog_name');
                options.url = options.url + '&base_query=' + $(element).attr('base_query');
                options.url = options.url + '&search_query=' + $(element).attr('search_query');
                options.url = options.url + '&combogrid_options=' + $(element).attr('combogrid_options');
                $(element).combogrid(options);
                $(element).addClass("has_combogrid_widget");
                $(element).attr('search_query', '{}');
            };
        }
        referencewidget_lookups();

    });
});
