/**
 * Controller class for calculation events
 */
function CalculationUtils() {

    var that = this;

    that.load = function() {

        $(".state-retracted .ajax_calculate").removeClass('ajax_calculate');

        $(".ajax_calculate").live('focus', function(){
            $(this).attr('focus_value', $(this).val());
            $(this).addClass("ajax_calculate_focus");
        });

        // 'blur' handler only if the value did NOT change
        $(".ajax_calculate").live('blur', function(){
            if ($(this).attr('focus_value') == $(this).val()){
                $(this).removeAttr("focus_value");
                $(this).removeClass("ajax_calculate_focus");
            }
        });

        // otherwise 'change' handler is fired.
        $(".ajax_calculate").live('change', function(){
            $(this).removeAttr("focus_value");
            $(this).removeClass("ajax_calculate_focus");

            form = $(this).parents("form");
            form_id = $(form).attr("id");
            td = $(this).parents('td');
            uid = $(this).attr('uid');
            field = $(this).attr('field');
            value = $(this).attr('value');
            item_data = $(this).parents('table').prev('input[name="item_data"]').val();

            // clear out the alerts for this field
            $(".alert").filter("span[uid='"+$(this).attr("uid")+"']").empty();

            if ($(this).parents('td').last().hasClass('interim')){
                // add value to form's item_data
                item_data = $.parseJSON(item_data);
                for(i = 0; i < item_data[uid].length;i++){
                    if(item_data[uid][i]['keyword'] == field){
                        item_data[uid][i]['value'] = value;
                        item_data = $.toJSON(item_data);
                        $(this).parents('table').prev('input[name="item_data"]').val(item_data);
                        break;
                    }
                }
            }

            // collect all form results into a hash (by analysis UID)
            var results = {};
            $.each($("td:not(.state-retracted) input[field='Result'], td:not(.state-retracted) select[field='Result']"), function(i, e){
                results[$(e).attr("uid")] = $(e).val();
            });

            options = {
                type: 'POST',
                url: 'listing_string_entry',
                data: {
                    '_authenticator': $('input[name="_authenticator"]').val(),
                    'uid': uid,
                    'field': field,
                    'value': value,
                    'results': $.toJSON(results),
                    'item_data': item_data,
                    'specification': $(".specification")
                        .filter(".selected").attr("value")
                },
                dataType: "json",
                success: function(data,textStatus,$XHR){
                    // clear out all row alerts for rows with fresh results
                    for(i=0;i<$(data['results']).length;i++){
                        result = $(data['results'])[i];
                        $(".alert").filter("span[uid='"+result.uid+"']").empty();
                    }
                    // put new alerts
                    $.each( data['alerts'], function( auid, alerts ) {
                        for (var i = 0; i < alerts.length; i++) {
                            lert = alerts[i]
                            $("span[uid='"+auid+"']")
                                .filter("span[field='"+lert.field+"']")
                                .append("<img src='"+window.portal_url+"/"+lert.icon+
                                    "' title='"+lert.msg+
                                    "' uid='"+auid+
                                    "'/>");
                        };
                    });
                    // Update uncertainty value
                    for(i=0;i<$(data['uncertainties']).length;i++){
                        u = $(data['uncertainties'])[i];
                        $('#'+u.uid+"-uncertainty").val(u.uncertainty);
                    }
                    // put result values in their boxes
                    for(i=0;i<$(data['results']).length;i++){
                        result = $(data['results'])[i];

                        $("input[uid='"+result.uid+"']").filter("input[field='Result']").val(result.result);

                        $('[type="hidden"]').filter("[field='ResultDM']").filter("[uid='"+result.uid+"']").val(result.dry_result);
                        $($('[type="hidden"]').filter("[field='ResultDM']").filter("[uid='"+result.uid+"']").siblings()[0]).empty().append(result.dry_result);
                        if(result.dry_result != ''){
                            $($('[type="hidden"]').filter("[field='ResultDM']").filter("[uid='"+result.uid+"']").siblings().filter(".after")).empty().append("<em class='discreet'>%</em>")
                        }

                        $("input[uid='"+result.uid+"']").filter("input[field='formatted_result']").val(result.formatted_result);
                        $("span[uid='"+result.uid+"']").filter("span[field='formatted_result']").empty().append(result.formatted_result);

                        // check box
                        if (results != ''){
                            if ($("[id*='cb_"+result.uid+"']").prop("checked") == false) {
                                $("[id*='cb_"+result.uid+"']").prop('checked', true);
                            }
                        }
                    }
                    if($('.ajax_calculate_focus').length > 0){
                        if($(form).attr('submit_after_calculation')){
                            $('#submit_transition').click();
                        }
                    }
                }
            };
            $.ajax(options);
        });
    }
}
