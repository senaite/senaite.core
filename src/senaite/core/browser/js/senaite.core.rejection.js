/**
 * Controller class for Rejection process in Analysis Request View View and Sample View View
 */
 function RejectionKickOff() {

     var that = this;
     that.load = function() {
        // If rejection workflow is disabled, hide the state link
        var request_data = {
            catalog_name: "portal_catalog",
            portal_type: "BikaSetup",
            include_fields: [
                "RejectionReasons"]
        };
        window.bika.lims.jsonapi_read(request_data, function (data) {
            if (data.success &&
                data.total_objects > 0) {
                var rejection_reasons = data.objects[0].RejectionReasons;
                var reasons_state;
                if(rejection_reasons.length > 0) {
                    reasons_state = rejection_reasons[0].checkbox;
                }
                if (reasons_state === undefined || reasons_state != 'on'){
                    $('a#workflow-transition-reject').closest('li').hide();
                }
            }
        });
        reject_widget_semioverlay_setup();
    };

     function reject_widget_semioverlay_setup() {
         "use strict";
         /*This function creates a hidden div element to insert the rejection
           widget there while the analysis request state is not rejected yet.
           So we can overlay the widget when the user clicks on the reject button.
         */
         if($('div#archetypes-fieldname-RejectionWidget').length > 0){
             // binding a new click action to state's rejection button
             $("a#workflow-transition-reject").unbind();
             $("a#workflow-transition-reject").bind("click", function(e){
                 // Overlays the rejection widget when the user tryes to reject the ar and
                 // defines all the ovelay functionalities
                 e.preventDefault();
                 //$('#semioverlay').fadeIn(500);
                 $('#semioverlay').show();
                 $('input[id="RejectionReasons.checkbox"]').click().prop('disabled', true);
             });
             // Getting widget's td and label
             var td = $('#archetypes-fieldname-RejectionWidget').parent('td');
             var label = "<div class='semioverlay-head'>"+$(td).prev('td').html().trim()+"</div>";
             // Creating the div element
             $('#content').prepend(
                "<div id='semioverlay' style='display:none'>" +
                " <div class='semioverlay-back'> </div>" +
                " <div class='semioverlay-panel'>" +
                " <div class='semioverlay-content'></div>" +
                " <div class='semioverlay-buttons'>" +
                " <input type='button'" +
                " name='semioverlay.reject' value='reject'/>" +
                " <input type='button' name='semioverlay.cancel'" +
                " value='cancel'/></div></div></div>");
             // Moving the widget there
             $('#archetypes-fieldname-RejectionWidget').detach().prependTo('#semioverlay .semioverlay-content');
             // hidding the widget's td and moving the label
             $(td).hide();
             $(label).detach().insertBefore('.semioverlay-content');
             // binding close actions
             $("div#semioverlay input[name='semioverlay.cancel']").bind('click',
                 function(){
                 $('#semioverlay').hide();
                 // Clear all data fields
                 $('input[id="RejectionReasons.checkbox"]').prop('checked', false).prop('disabled', false);
                 $('input[id="RejectionReasons.checkbox.other"]').prop('checked', false);
                 $('input[id="RejectionReasons.textfield.other"]').val('');
                 var options = $('.rejectionwidget-multiselect').find('option');
                 for (var i=0;options.length>i; i++){
                     $(options[i]).attr('selected',false);
                 }
             });
             // binding reject actions
             $("div#semioverlay input[name='semioverlay.reject']").bind('click',function(){
                 $('div#semioverlay .semioverlay-panel').fadeOut();
                 reject_ar_sample();
             });
         }
     }

     function getRejectionWidgetValues(){
         "use strict";
         // Retuns the rejection reason widget's values in JSON format to
         // be used in jsonapi's update function
         var ch_val=0,multi_val = [],other_ch_val=0,other_val='',option;
         ch_val = $('.rejectionwidget-checkbox').prop('checked');
         if (ch_val){
             ch_val=1;
             var selected_options = $('.rejectionwidget-multiselect').find('option');
             for (var i=0;selected_options.length>i; i++){
                 option = selected_options[i];
                 if (option.selected){
                     multi_val.push($(option).val());
                 }
             }
             other_ch_val = $('.rejectionwidget-checkbox-other').prop('checked');
             if (other_ch_val){
                 other_ch_val = 1;
                 other_val = $('.rejectionwidget-input-other').val();
             }
             else{other_ch_val=0;}
         }else{
            // Just set ch_val '0' if it is false.
            ch_val=0;
         }
         // Gathering all values
         var rej_widget_state = {
             checkbox:ch_val,
             selected:multi_val,
             checkbox_other:other_ch_val,
             other:other_val
         };
         return $.toJSON(rej_widget_state);
     }

     function reject_ar_sample(){
         "use strict";
         // Makes all the steps needed to reject the ar or sample
         var requestdata = {};
         //save the rejection widget's values
         var url = window.location.href
            .replace('/base_view', '')
            .replace('/analyses', '')
            .replace('/manage_results', '')
            .replace('/not_requested', '')
            .replace('/log', '');
         var obj_path = url.replace(window.portal_url, '');
         var redirect_state = $("a#workflow-transition-reject").attr('href');
         // requestdata should has the format  {fieldname=fieldvalue}
         requestdata.obj_path= obj_path;
         //fieldvalue data will be something like:
         // [{'checkbox': u'on', 'textfield-2': u'b', 'textfield-1': u'c', 'textfield-0': u'a'}]
         var fieldvalue = getRejectionWidgetValues();
         requestdata.RejectionReasons = fieldvalue;
         var msg = '';
         $.ajax({
             type: "POST",
             url: window.portal_url+"/@@API/update",
             data: requestdata
         })
         .done(function(data) {
            //trigger reject workflow action
            if (data !== null && data.success === true) {
                bika.lims.SiteView.notificationPanel('Rejecting', "succeed");
                // the behaviour for samples is different
                if($('body').hasClass('portaltype-sample')) {
                    // We need to get the authenticator
                    var autentification = $('input[name="_authenticator"]').val();
                    $.ajax({
                        url: window.location.href + '/doActionForSample?workflow_action=reject&_authenticator=' + autentification,
                        type: 'POST',
                        dataType: "json",
                    })
                    .done(function(data2) {
                        if (data2 !== null && data2.success == "true") {
                            window.location.href = window.location.href;
                        } else {
                            bika.lims.SiteView.notificationPanel('Error while updating object state', "error");
                            var msg = '[bika.lims.analysisrequest.js] Error while updating object state';
                            console.warn(msg);
                            window.bika.lims.error(msg);
                            $('#semioverlay input[name="semioverlay.cancel"]').click();
                        }
                    });
                } else {
                    // Redirecting to the same page using the rejection's url
                    bika.lims.SiteView.notificationPanel('Rejecting', "succeed");
                    window.location.href = redirect_state;
                }
            } else if (data.success === false) {
                bika.lims.SiteView.notificationPanel('Error while rejecting the analysis request. Unsuccesful AJAX call.', 'error');
                msg = '[bika.lims.analysisrequest.js] Error while rejecting the analysis request. Unsuccesful AJAX call.';
                console.warn(msg);
                window.bika.lims.error(msg);
                $('#semioverlay input[name="semioverlay.cancel"]').click();
            } else {
                bika.lims.SiteView.notificationPanel('Error while rejecting the analysis request. No data returned.', 'error');
                msg = '[bika.lims.analysisrequest.js] Error while rejecting the analysis request. No data returned.';
                console.warn(msg);
                window.bika.lims.error(msg);
                $('#semioverlay input[name="semioverlay.cancel"]').click();
            }
         })
         .fail(function(){
             bika.lims.SiteView.notificationPanel('Error while rejection the analysis request. AJAX POST failed.','error');
             var msg = '[bika.lims.analysisrequest.js] Error while rejection the analysis request. AJAX POST failed.';
             console.warn(msg);
             window.bika.lims.error(msg);
             $('#semioverlay input[name="semioverlay.cancel"]').click();
         });
     }
 }
