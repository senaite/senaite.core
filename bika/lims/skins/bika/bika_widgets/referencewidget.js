function referencewidget_lookups(elements){
    // Any reference widgets that don't already have combogrid widgets
    if(elements == undefined){
        var inputs = $(".ArchetypesReferenceWidget [combogrid_options]").not('.has_combogrid_widget');
    } else {
        var inputs = elements;
    }
    for (var i = inputs.length - 1; i >= 0; i--) {
        var element = inputs[i];
        var options = $.parseJSON($(element).attr('combogrid_options'));
        if(options == '' || options == undefined || options == null){
            continue;
        }

        // Prevent from saving previous record when input value is empty
        // By default, a recordwidget input element gets an empty value
        // when receives the focus, so the underneath values must be
        // cleared too.
        var elName = $(element).attr('name');
        $('input[name="'+elName+'"]').live('focusin', function(){
        	var fieldName = $(this).attr('name');
        	if($(this).val() || $(this).val().length==0){
        		var val = $(this).val();
        		var uid = $(this).attr('uid');
        		$(this).val('');
        		$(this).attr('uid', '');
                $('input[name="'+fieldName+'_uid"]').val('');
                $(this).trigger("unselected", [val,uid]);
        	}
    	});

        options.select = function(event, ui){
            event.preventDefault();
            // Set value in activated element (must exist in colModel!)
            var fieldName = $(this).attr('name');
            $(this).val(ui.item[$(this).attr('ui_item')]);
            $(this).attr('uid', ui.item['UID']);
            $('input[name="'+fieldName+'_uid"]').val(ui.item['UID']);
            skip = $(element).attr("skip_referencewidget_lookup");
            if (skip != true){
                $(this).trigger("selected", ui.item['UID']);
            }
            $(element).removeAttr("skip_referencewidget_lookup");
            $(this).next('input').focus();
        }
        if(window.location.href.search("portal_factory") > -1){
            options.url = window.location.href.split("/portal_factory")[0] + "/" + options.url;
        }
        options.url = options.url + '?_authenticator=' + $('input[name="_authenticator"]').val();
        options.url = options.url + '&catalog_name=' + $(element).attr('catalog_name');
        options.url = options.url + '&base_query=' + $(element).attr('base_query');
        options.url = options.url + '&search_query=' + $(element).attr('search_query');
        options.url = options.url + '&colModel=' + $.toJSON( $.parseJSON($(element).attr('combogrid_options'))["colModel"] );
        options.url = options.url + '&search_fields=' + $.toJSON($.parseJSON($(element).attr('combogrid_options'))["search_fields"]);
        options.url = options.url + '&discard_empty=' + $.toJSON($.parseJSON($(element).attr('combogrid_options'))["discard_empty"]);
        options.url = options.url + '&force_all=' + $.toJSON($.parseJSON($(element).attr('combogrid_options'))["force_all"]);
        $(element).combogrid(options);
        $(element).addClass("has_combogrid_widget");
        $(element).attr('search_query', '{}');
    };
}

jQuery(function($){
    $(document).ready(function(){
        _p = jarn.i18n.MessageFactory('plone');
        _ = jarn.i18n.MessageFactory('bika');

        referencewidget_lookups();

    });
});
