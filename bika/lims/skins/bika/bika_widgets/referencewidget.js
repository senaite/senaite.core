(function ($) {

$(document).ready(function(){
    referencewidget_lookups();

    $(".reference_multi_item .deletebtn").live('click', function(){
        var fieldName = $(this).attr("fieldName");
        var uid = $(this).attr("uid");
        var existing_uids = $("input[name^='"+fieldName+"_uid']").val().split(",");
        destroy(existing_uids, uid);
        $("input[name^='"+fieldName+"_uid']").val(existing_uids.join(","));
        $("input[name='"+fieldName+"']").attr("uid", existing_uids.join(","));
        $(this).parent().remove();
    });

    $(".ArchetypesReferenceWidget").bind("selected blur change", function(){
        var e = $(this).children("input.referencewidget");
        if (e.val() == '') {
            fieldName = $(e).attr("name").split(":")[0];
            $(e).attr("uid", "");
            $("input[name^='"+fieldName+"_uid']").val("");
            $("div[name='"+fieldName+"-listing']").empty();
        }
    });
    save_UID_check();
    check_UID_check();
    loadAddButtonOveray();
});

}(jQuery));

function destroy(arr, val) {
    for (var i = 0; i < arr.length; i++) if (arr[i] === val) arr.splice(i, 1);
    return arr;
}

function referencewidget_lookups(elements){
    // Any reference widgets that don't already have combogrid widgets
    var inputs;
    if(elements === undefined){
        inputs = $(".ArchetypesReferenceWidget [combogrid_options]").not(".has_combogrid_widget");
    } else {
        inputs = elements;
    }
    for (var i = inputs.length - 1; i >= 0; i--) {
        var element = inputs[i];
        var options = $.parseJSON($(element).attr("combogrid_options"));
        if(!options){
            continue;
        }

        // Prevent from saving previous record when input value is empty
        // By default, a recordwidget input element gets an empty value
        // when receives the focus, so the underneath values must be
        // cleared too.
        // var elName = $(element).attr("name");
        // $("input[name='"+elName+"']").live("focusin", function(){
        //  var fieldName = $(this).attr("name");
        //  if($(this).val() || $(this).val().length===0){
        //      var val = $(this).val();
        //      var uid = $(this).attr("uid");
        //      $(this).val("");
        //      $(this).attr("uid", "");
        //      $("input[name='"+fieldName+"_uid']").val("");
        //      $(this).trigger("unselected", [val,uid]);
        //  }
        // });

        options.select = function(event, ui){
            event.preventDefault();
            var fieldName = $(this).attr("name");
            var skip;
            var uid_element = $("input[name='"+fieldName+"_uid']");
            var listing_div = $("div#"+fieldName+"-listing");
            if($("#"+fieldName+"-listing").length > 0) {
                // Add selection to textfield value
                var existing_uids = $("input[name='"+fieldName+"_uid']").val().split(",");
                destroy(existing_uids,"");
                destroy(existing_uids,"[]");
                var selected_value = ui.item[$(this).attr("ui_item")];
                var selected_uid = ui.item.UID;
                if (existing_uids.indexOf(selected_uid) == -1) {
                    existing_uids.push(selected_uid);
                    $(this).val("");
                    $(this).attr("uid", existing_uids.join(","));
                    $(uid_element).val(existing_uids.join(","));
                    // insert item to listing
                    var del_btn_src = window.portal_url+"/++resource++bika.lims.images/delete.png";
                    var del_btn = "<img class='deletebtn' src='"+del_btn_src+"' fieldName='"+fieldName+"' uid='"+selected_uid+"'/>";
                    var new_item = "<div class='reference_multi_item' uid='"+selected_uid+"'>"+del_btn+selected_value+"</div>";
                    $(listing_div).append($(new_item));
                }
                skip = $(element).attr("skip_referencewidget_lookup");
                if (skip !== true){
                    $(this).trigger("selected", ui.item.UID);
                }
                $(element).removeAttr("skip_referencewidget_lookup");
                $(this).next("input").focus();
            } else {
                // Set value in activated element (must exist in colModel!)
                $(this).val(ui.item[$(this).attr("ui_item")]);
                $(this).attr("uid", ui.item.UID);
                $("input[name='"+fieldName+"_uid']").val(ui.item.UID);
                skip = $(element).attr("skip_referencewidget_lookup");
                if (skip !== true){
                    $(this).trigger("selected", ui.item.UID);
                }
                $(element).removeAttr("skip_referencewidget_lookup");
                $(this).next("input").focus();
            }
        };

        if(window.location.href.search("portal_factory") > -1){
            options.url = window.location.href.split("/portal_factory")[0] + "/" + options.url;
        }
        options.url = options.url + "?_authenticator=" + $("input[name='_authenticator']").val();
        options.url = options.url + "&catalog_name=" + $(element).attr("catalog_name");
        options.url = options.url + "&base_query=" + $(element).attr("base_query");
        options.url = options.url + "&search_query=" + $(element).attr("search_query");
        options.url = options.url + "&colModel=" + $.toJSON( $.parseJSON($(element).attr("combogrid_options")).colModel);
        options.url = options.url + "&search_fields=" + $.toJSON($.parseJSON($(element).attr("combogrid_options")).search_fields);
        options.url = options.url + "&discard_empty=" + $.toJSON($.parseJSON($(element).attr("combogrid_options")).discard_empty);
        options.url = options.url + "&force_all=" + $.toJSON($.parseJSON($(element).attr("combogrid_options")).force_all);
        $(element).combogrid(options);
        $(element).addClass("has_combogrid_widget");
        $(element).attr("search_query", "{}");
    }
}

function save_UID_check(){
    //Save the selected uid's item to avoid introduce non-listed
    //values inside the widget.
    $(".ArchetypesReferenceWidget").bind("selected", function(){
        var uid = $(this).children("input.referencewidget").attr("uid");
        var val = $(this).children("input.referencewidget").val();
        $(this).children("input.referencewidget").attr("uid_check",uid);
        $(this).children("input.referencewidget").attr("val_check",val);
    });
}

function check_UID_check(){
    //Remove the necessary values to submit if the introduced data is
    //not correct.
    $(".ArchetypesReferenceWidget").children("input.referencewidget").bind("blur", function(){
        var chk = $(this).attr("uid_check");
        var val_chk = $(this).attr("val_check");
        var value = $(this).val();
        //When is the first time you click on
        if ((chk == undefined || chk == false) && (value != "") && $(this).attr("uid")){
            $(this).attr("uid_check", $(this).attr("uid"));
            $(this).attr("val_check",value);
        }
        //Write a non existent selection
        else if ((chk == undefined || chk == false) && (value != "")){
            $(this).attr('uid','');
            $(this).attr('value','');
        }
        //UID is diferent from the checkUID, preventive option, maybe
        //never will be accomplished
        else if ($(this).attr("value") && (chk != undefined || chk != false) && (chk != $(this).attr("uid"))){
            $(this).attr('uid',chk);
            $(this).attr('value',val_chk);
        }
        //Modified the value by hand and wrong, it restores the
        //previous option.
        else if ((val_chk != value) && value != ''){
            $(this).attr('uid',chk);
            $(this).attr('value',val_chk);
        }
    });
}

function loadAddButtonOveray() {
    /**
     * Add the overlay conditions for the AddButton.
     */
    $("a.add_button_overlay").prepOverlay(getOverlayConf());
}

function getOverlayConf() {
    /**
     * Define the overlay configuration parameters.
     */
    edit_overlay = {
        subtype: 'ajax',
        filter: 'head>*,#content>*:not(div.configlet),dl.portalMessage.error,dl.portalMessage.info',
        formselector: 'form[id$="base-edit"]',
        closeselector: '[name="form.button.cancel"]',
        width: '70%',
        noform:'close',
        config: {
            onLoad: function() {
                // Manually remove remarks
                this.getOverlay().find("#archetypes-fieldname-Remarks").remove();
                // Remove menstrual status widget to avoid my suicide
                // with a "500 service internal error"
                this.getOverlay().find("#archetypes-fieldname-MenstrualStatus").remove();

                // Force to reload bika.lims.initalize method with the needed overlay's health controllers.
                // This is done to work with specific js and widgets in the overlay.
                if ($("a.add_button_overlay").attr("data_js_controllers")){
                    window.bika.lims.loadControllers(false,$("a.add_button_overlay").attr("data_js_controllers"));
                }
                // Address widget
                $.ajax({
                    url: 'bika_widgets/addresswidget.js',
                    dataType: 'script',
                    async: false
                });
            },
            onBeforeClose: function() {
                // Fill the box with the recently created object
                var name = $('#Firstname').val() + ' ' + $("#Surname").val();
                if ($('#Firstname').val() == undefined) {
                    name = $('#title').val();
                }
                var overlay_trigger = $('div.overlay').overlay().getTrigger().attr("id");
                var trigger_id = $("[rel='#" + overlay_trigger + "']").attr('id').replace('_addButtonOverlay','');
                if (name.length > 1) {
                    $('#' + trigger_id).val(name).focus();
                    setTimeout(function() {
                        $('.cg-DivItem').first().click();
                    }, 500);
                }
                setTimeout(function() {return true; 100;});
            }
        }
    };
    return edit_overlay;
}