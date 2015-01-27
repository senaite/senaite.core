'use strict;'

/**
 * Controller class for all site views
 */
function SiteView() {

    var that = this;

    that.load = function() {

        loadCommonEvents();

        loadClientEvents();

        loadReferenceDefinitionEvents();

    }

    function loadClientEvents() {

        // Client creation overlay
        $('a.add_client').prepOverlay({
                subtype: 'ajax',
                filter: 'head>*,#content>*:not(div.configlet),dl.portalMessage.error,dl.portalMessage.info',
                formselector: '#client-base-edit',
                closeselector: '[name="form.button.cancel"]',
                width:'70%',
                noform:'close',
                config: {
                    closeOnEsc: false,
                    onLoad: function() {
                        // manually remove remarks
                        this.getOverlay().find("#archetypes-fieldname-Remarks").remove();
                    },
                    onClose: function(){
                        // here is where we'd populate the form controls, if we cared to.
                    }
                }
        });

        // Client combogrid searches by ID
        $("input[id*='ClientID']").combogrid({
            colModel: [{'columnName':'ClientUID','hidden':true},
                       {'columnName':'ClientID','width':'20','label':_('Client ID')},
                       {'columnName':'Title','width':'80','label':_('Title')}],
            showOn: true,
            width: '450px',
            url: window.portal_url + "/getClients?_authenticator=" + $('input[name="_authenticator"]').val(),
            select: function( event, ui ) {
                $(this).val(ui.item.ClientID);
                $(this).change();
                return false;
            }
        });

        // Display add Client button next to Client ID input for all
        // views except from Client View
        if($(".portaltype-client").length == 0){
            $("input[id='ClientID']")
                .after('<a style="border-bottom:none !important;margin-left:.5;"' +
                       ' class="add_client"' +
                       ' href="'+window.portal_url+'/clients/portal_factory/Client/new/edit"' +
                       ' rel="#overlay">' +
                       ' <img style="padding-bottom:1px;" src="'+window.portal_url+'/++resource++bika.lims.images/add.png"/>' +
                       '</a>');
        }

        // Confirm before resetting client specs to default lab specs
        $("a[href*='set_to_lab_defaults']").click(function(event){
            // always prevent default/
            // url is activated manually from 'Yes' below.
            url = $(this).attr("href");
            event.preventDefault();
            yes = _('Yes');
            no = _('No');
            var $confirmation = $("<div></div>")
                .html(_("This will remove all existing client analysis specifications "+
                        "and create copies of all lab specifications. "+
                        "Are you sure you want to do this?"))
                .dialog({
                    resizable:false,
                    title: _('Set to lab defaults'),
                    buttons: {
                        yes: function(event){
                            $(this).dialog("close");
                            window.location.href = url;
                        },
                        no: function(event){
                            $(this).dialog("close");
                        }
                    }
                });
        });
    }

    function loadReferenceDefinitionEvents() {

        // a reference definition is selected from the dropdown
        // (../../skins/bika/bika_widgets/referenceresultswidget.js)
        $('#ReferenceDefinition\\:list').change(function(){
            authenticator = $('input[name="_authenticator"]').val();
            uid = $(this).val();
            option = $(this).children(":selected").html();

            if (uid == '') {
                // No reference definition selected;
                // render empty widget.
                $("#Blank").prop('checked',false);
                $("#Hazardous").prop('checked',false);
                $('.bika-listing-table')
                    .load('referenceresults', {'_authenticator': authenticator});
                return;
            }

            if(option.search(_("(Blank)")) > -1){
                $("#Blank").prop('checked',true);
            } else {
                $("#Blank").prop('checked',false);
            }

            if(option.search(_("(Hazardous)")) > -1){
                $("#Hazardous").prop('checked',true);
            } else {
                $("#Hazardous").prop('checked',false);
            }

            $('.bika-listing-table')
                .load('referenceresults',
                    {'_authenticator': authenticator,
                     'uid':uid});
        });

        // If validation failed, and user is returned to page - requires reload.
        if ($('#ReferenceDefinition\\:list').val() != ''){
            $('#ReferenceDefinition\\:list').change();
        }
    }

    function loadCommonEvents() {

        var curDate = new Date();
        var y = curDate.getFullYear();
        var limitString = "1900:" + y;
        var dateFormat = _("date_format_short_datepicker");
        if (dateFormat == 'date_format_short_datepicker'){
            dateFormat = 'yy-mm-dd';
        }

        $("input.datepicker").live("click", function() {
            $(this).datepicker({
                showOn:"focus",
                showAnim:"",
                changeMonth:true,
                changeYear:true,
                dateFormat: dateFormat,
                yearRange: limitString
            })
            .click(function(){$(this).attr("value", "");})
            .focus();

        });

        $("input.datepicker_nofuture").live("click", function() {
            $(this).datepicker({
                showOn:"focus",
                showAnim:"",
                changeMonth:true,
                changeYear:true,
                maxDate: curDate,
                dateFormat: dateFormat,
                yearRange: limitString
            })
            .click(function(){$(this).attr("value", "");})
            .focus();
        });

        $("input.datepicker_2months").live("click", function() {
            $(this).datepicker({
                showOn:"focus",
                showAnim:"",
                changeMonth:true,
                changeYear:true,
                maxDate: "+0d",
                numberOfMonths: 2,
                dateFormat: dateFormat,
                yearRange: limitString
            })
            .click(function(){$(this).attr("value", "");})
            .focus();
        });

        // Analysis Service popup trigger
        $('.service_title span:not(.before)').live("click", function(){
            var dialog = $("<div></div>");
            dialog
                .load(window.portal_url + "/analysisservice_popup",
                    {'service_title':$(this).closest('td').find("span[class^='state']").html(),
                    "analysis_uid":$(this).parents("tr").attr("uid"),
                    "_authenticator": $("input[name='_authenticator']").val()}
                )
                .dialog({
                    width:450,
                    height:450,
                    closeText: _("Close"),
                    resizable:true,
                    title: $(this).text()
                });
        });

        $('.numeric').live('paste', function(event){
            // Wait (next cycle) for value popluation and replace commas.
            var $self = $(this);
            window.setTimeout(function() {
                $self.val($self.val().replace(',','.'));
            }, 0);
        });


        $(".numeric").live("keypress", function(event) {
            var allowedKeys = [
                8,   // backspace
                9,   // tab
                13,  // enter
                35,  // end
                36,  // home
                37,  // left arrow
                39,  // right arrow
                46,  // delete - We don't support the del key in Opera because del == . == 46.
                44,  // ,
                60,  // <
                62,  // >
                45,  // -
                69,  // E
                101, // e,
                61   // =
            ];
            var isAllowedKey = allowedKeys.join(",").match(new RegExp(event.which)); // IE doesn't support indexOf
            // Some browsers just don't raise events for control keys. Easy. e.g. Safari backspace.
            if (!event.which || // Control keys in most browsers. e.g. Firefox tab is 0
                (48 <= event.which && event.which <= 57) || // Always 0 through 9
                isAllowedKey) { // Opera assigns values for control keys.
                // Wait (next cycle) for value popluation and replace commas.
                var $self = $(this);
                window.setTimeout(function() {
                    $self.val($self.val().replace(',','.'));
                }, 0);
                return;
            } else {
                event.preventDefault();
            }
        });

        // Archetypes :int and IntegerWidget inputs get filtered
        $("input[name*='\\:int'], .ArchetypesIntegerWidget input").keyup(function(e) {
            if (/\D/g.test(this.value)) {
                this.value = this.value.replace(/\D/g, "");
            }
        });

        // Archetypes :float and DecimalWidget inputs get filtered
        $("input[name*='\\:float'], .ArchetypesDecimalWidget input").keyup(function(e) {
            if (/[^.\d]/g.test(this.value)) {
                this.value = this.value.replace(/[^.\d]/g, "");
            }
        });

        /* Replace kss-bbb spinner with a quieter one */
        var timer, spinner, counter = 0;
        $(document).unbind("ajaxStart");
        $(document).unbind("ajaxStop");
        $('#ajax-spinner').remove();
        spinner = $('<div id="bika-spinner"><img src="' + portal_url + '/spinner.gif" alt=""/></div>');
        spinner.appendTo('body').hide();
        $(document).ajaxStart(function () {
            counter++;
            setTimeout(function () {
                if (counter > 0) {
                    spinner.show('fast');
                }
            }, 500);
        });
        function stop_spinner(){
            counter--;
            if (counter < 0){ counter = 0; }
            if (counter == 0) {
                clearTimeout(timer);
                spinner.stop();
                spinner.hide();
            }
        }
        $(document).ajaxStop(function () {
            stop_spinner();
        });
        $( document ).ajaxError(function( event, jqxhr, settings, thrownError ) {
            stop_spinner();
            window.bika.lims.log("Error at " + settings.url + ": " + thrownError);
        });
    }

    function portalAlert(html) {
        if ($('#portal-alert').length == 0) {
            $('#portal-header').append("<div id='portal-alert' style='display:none'><div class='portal-alert-item'>" + html + "</div></div>");
        } else {
            $('#portal-alert').append("<div class='portal-alert-item'>" + html + "</div>");
        }
        $('#portal-alert').fadeIn();
    }

    that.notificationPanel = function(data, mode) {
    /**
     * Render an alert inside the content panel. Used for autosave in ARView, for example.
     */
    $('#panel-notification').remove();
        $('div#viewlet-above-content-title').append(
            "<div id='panel-notification' style='display:none'>" +
            "<div class='"+mode+"-notification-item'>"
            + data +
            "</div></div>");

        $('#panel-notification').fadeIn("slow","linear", function(){
            setTimeout(function() {
                $('#panel-notification').fadeOut("slow","linear")
            }, 3000)
        });
    }
}
