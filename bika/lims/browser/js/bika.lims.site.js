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

        loadFilterByDepartment();
        //Date range controllers
        $('.date_range_start').bind("change", function () {
            date_range_controller_0(this);
        });
        $('.date_range_end').bind("change", function () {
            date_range_controller_1(this);
        });
    };

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
        /**
        This function defines a datepicker for a date range. Both input
        elements should be siblings and have the class 'date_range_start' and
        'date_range_end'.
        */
        $("input.datepicker_range").datepicker({
            showOn:"focus",
            showAnim:"",
            changeMonth:true,
            changeYear:true,
            dateFormat: dateFormat,
            yearRange: limitString
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


        $("input.datetimepicker_nofuture").live("click", function() {
            $(this).datetimepicker({
                showOn:"focus",
                showAnim:"",
                changeMonth:true,
                changeYear:true,
                maxDate: curDate,
                dateFormat: dateFormat,
                yearRange: limitString,
                timeFormat: "HH:mm",
                beforeShow: function() {
                        setTimeout(function(){
                            $('.ui-datepicker').css('z-index', 99999999999999);
                        }, 0);
                    }
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
        // autocomplete input controller
        var availableTags = $.parseJSON($("input.autocomplete").attr('voc'));
        function split( val ) {
            return val.split( /,\s*/ );
        }
        function extractLast( term ) {
            return split( term ).pop();
        }
        $("input.autocomplete")
            // don't navigate away from the field on tab when selecting an item
            .on( "keydown", function( event ) {
              if ( event.keyCode === $.ui.keyCode.TAB &&
                  $( this ).autocomplete( "instance" ).menu.active ) {
                event.preventDefault();
              }
            })
            .autocomplete({
                minLength: 0,
                source: function( request, response ) {
                    // delegate back to autocomplete, but extract the last term
                    response( $.ui.autocomplete.filter(
                        availableTags, extractLast( request.term ) ) );
                },
                focus: function() {
                    // prevent value inserted on focus
                    return false;
                },
                select: function( event, ui ) {
                    var terms = split( this.value );
                    // remove the current input
                    terms.pop();
                    // add the selected item
                    terms.push( ui.item.value );
                    // add placeholder to get the comma-and-space at the end
                    terms.push( "" );
                    this.value = terms.join( ", " );
                    return false;
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
    };

    function loadFilterByDepartment() {
        /**
        This function sets up the filter by department cookie value by chosen departments.
        Also it does auto-submit if admin wants to enable/disable the department filtering.
        */
        $('#department_filter_submit').click(function() {
          if(!($('#admin_dep_filter_enabled').is(":checked"))) {
            var deps =[];
            $.each($("input[name^=chb_deps_]:checked"), function() {
              deps.push($(this).val());
            });
            var cookiename = 'filter_by_department_info';
            if (deps.length===0) {
              deps.push($('input[name^=chb_deps_]:checkbox:not(:checked):visible:first').val());
            }
            createCookie(cookiename, deps.toString());
          }
          location.reload();
        });

        $('#admin_dep_filter_enabled').change(function() {
            var cookiename = 'filter_by_department_info';
            if($(this).is(":checked")) {
                var deps=[];
                $.each($("input[name^=chb_deps_]:checkbox"), function() {
                  deps.push($(this).val());
                });
                createCookie(cookiename, deps);
                createCookie('dep_filter_disabled','true');
                location.reload();
              }else{
                createCookie('dep_filter_disabled','false');
                location.reload();
              }
            });
          loadFilterByDepartmentCookie();
    }

    function loadFilterByDepartmentCookie(){
        /**
        This function checks if the cookie 'filter_by_department_info' is
        available. If the cookie exists, do nothing, if the cookie has not been
        created yet, checks the selected department in the checkbox group and creates the cookie with the UID of the first department.
        If cookie value "dep_filter_disabled" is true, it means the user is admin and filtering is disabled.
        */
        // Gettin the cookie
        var cookiename = 'filter_by_department_info';
        var cookie_val = readCookie(cookiename);
        if (cookie_val === null || document.cookie.indexOf(cookiename)<1){
            var dep_uid = $('input[name^=chb_deps_]:checkbox:visible:first').val();
            createCookie(cookiename, dep_uid);
        }
        var dep_filter_disabled=readCookie('dep_filter_disabled');
        if (dep_filter_disabled=="true" || dep_filter_disabled=='"true"'){
            $('#admin_dep_filter_enabled').prop("checked",true);
        }
    }


    /**
    This function updates the minimum selectable date of date_range_end
    @param {object} input_element is the <input> object for date_range_start
    */
    function date_range_controller_0(input_element){
        var date_element = $(input_element).datepicker("getDate");
        var brother = $(input_element).siblings('.date_range_end');
        $(brother).datepicker("option", "minDate", date_element );
    }
    /**
    This function updates the maximum selectable date of date_range_start
    @param {object} input_element is the <input> object for date_range_end
    */
    function date_range_controller_1(input_element){
        var date_element = $(input_element).datepicker("getDate");
        var brother = $(input_element).siblings('.date_range_start');
        $(brother).datepicker("option", "maxDate", date_element );
    }
}
