/**
 * Controller class for all site views
 */
function SiteView() {

    var that = this;

    that.load = function() {

        loadCommonEvents();

        loadClientEvents();

        loadReferenceDefinitionEvents();

        // TODO: Provisional method, needs its own controller?
        loadAnalysisRequestLayout();

    }

    // TODO Provisional method. needs its own controller?
    function loadAnalysisRequestLayout() {
        $('#layout').change(function(){
            var address = $(".context_action_link").attr('href');
            var href = addParam(address, 'layout', $(this).val())
            $(".context_action_link").attr('href', href);
        });
        $('#ar_count').each(function() {
            var elem = $(this);

            // Save current value of element
            elem.data('oldVal', elem.val());

            // Look for changes in the value
            elem.bind("propertychange keyup input paste", function(event){
                var new_val = elem.val();
                // If value has changed...
                if (new_val != '' && elem.data('oldVal') != new_val) {
                    // Updated stored value
                    elem.data('oldVal', new_val);
                    var address = $(".context_action_link").attr('href');
                    var href = addParam(address, 'ar_count', $(this).val())
                    $(".context_action_link").attr('href', href);
                }
            });
        });

        function addParam(address, param, val){
            var argparts;
            var parts = address.split("?");
            var url = parts[0];
            var args = [];
            if (parts.length > 1) {
                var found = false;
                args = parts[1].split("&");
                for (var arg=0; arg<args.length; arg++) {
                    argparts = args[arg].split('=');
                    if (argparts[0] == param) {
                        args[arg] = param + '=' + val;
                        found = true;
                    }
                };
                if (found == false) {
                    args.push(param + '=' + val);
                };
            } else {
                args.push(param + '=' + val);
            };
            return url + "?" + args.join('&');
        };
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

        if ($('input[name="_authenticator"]').length > 0) {
            // Look for updates at pypi
            $.ajax({
                url: window.portal_url + "/get_product_version",
                type: 'POST',
                dataType: 'json',
                data: {'_authenticator': $('input[name="_authenticator"]').val() },
            }).done(function(data) {
                var bv = data['bika.lims'];
                if (bv != undefined) {
                    // Look at pypi
                    var pypiurl = "http://pypi.python.org/pypi/bika.lims";
                    $.getJSON(pypiurl+'/json?callback=?', function(data) {
                        var ver = data.info.version;
                        var date = data.releases[ver][0].upload_time;
                        var html = "<p class='title'>"+_("New Bika LIMS release available")+"</p><p>&nbsp;"+ver+"&nbsp;&nbsp;("+date+")<br/>";
                        if (!bv.startsWith(ver)) {
                            // Newer version in pypi!
                            html += _("Your current version is")+" "+bv+"</p>";
                            html += '<p>';
                            html += '<a class="button" href="'+pypiurl+'">'+_("Release notes")+'</a>&nbsp;&nbsp;';
                            html += '<input id="hide-release-notifications" type="button" value="'+_("Dismiss")+'"><p>';
                            portalAlert(html);

                            $('#hide-release-notifications').click(function(e) {
                                e.preventDefault();
                                $.ajax({
                                    url: window.portal_url + "/hide_new_releasesinfo",
                                    type: 'POST',
                                    data: {'_authenticator': $('input[name="_authenticator"]').val() },
                                }).done(function(data) {
                                    $('#ShowNewReleasesInfo').attr('checked', false);
                                    $('#hide-release-notifications').closest('div.portal-alert-item').html("<p class='title'>"+_("Notifications about new releases have been disabled. You can enable this option again in Bika Setup > Security")+"</p>");
                                });
                            });
                        }
                     });
                }
            });

            // Check if new upgrade-steps
            $.ajax({
                url: window.portal_url + "/prefs_install_products_form",
                type: 'POST',
                data: {'_authenticator': $('input[name="_authenticator"]').val() },
            }).done(function(htmldata) {
                if ($(htmldata).find('input[name="prefs_reinstallProducts:method"]').length > 0) {
                    // Needs an upgrade!
                    var html = '<form method="post" action="' + window.portal_url + '/portal_quickinstaller">';
                    html += "<p class='title'>"+_("Upgrade step available:")+"</p>";
                    var products = $(htmldata).find('input[name="prefs_reinstallProducts:method"]');
                    $.each(products, function(index, product){
                        // <input class="context" type="submit" name="prefs_reinstallProducts:method" value="bika.lims">
                        html += "<p>";
                        html += $(product).closest('ul.configletDetails').parent().find('label').first().html().trim()+"&nbsp;&nbsp;&nbsp;";
                        html += _("Click to upgrade: ") + $(product).parent().html().trim()+"</span>";
                        html += "</p>";

                    });
                    html += "</form>";
                    portalAlert(html);
                }
            });

            // Check instrument validity and add an alert if needed
            $.ajax({
                url: window.portal_url + "/get_instruments_alerts",
                type: 'POST',
                data: {'_authenticator': $('input[name="_authenticator"]').val() },
                dataType: 'json'
            }).done(function(data) {
                if (data['out-of-date'].length > 0
                    || data['qc-fail'].length > 0
                    || data['next-test'].length > 0) {
                    var html = "";
                    var outofdate = data['out-of-date'];
                    if (outofdate.length > 0) {
                        // Out of date alert
                        html += "<p class='title'>"+outofdate.length+_(" instruments are out-of-date")+":</p>";
                        html += "<p>";
                        $.each(outofdate, function(index, value){
                            var hrefinstr = value['url']+"/certifications";
                            var titleinstr = value['title'];
                            var anchor = "<a href='"+hrefinstr+"'>"+titleinstr+"</a>";
                            if (index == 0) {
                                html += anchor;
                            } else {
                                html += ", "+anchor;
                            }
                        })
                        html += "</p>";
                    }
                    var qcfail = data['qc-fail'];
                    if (qcfail.length > 0) {
                        // QC Fail alert
                        html += "<p class='title'>"+qcfail.length+_(" instruments with QC Internal Calibration Tests failed")+":</p>";
                        html += "<p>";
                        $.each(qcfail, function(index, value){
                            var hrefinstr = value['url']+"/referenceanalyses";
                            var titleinstr = value['title'];
                            var anchor = "<a href='"+hrefinstr+"'>"+titleinstr+"</a>";
                            if (index == 0) {
                                html += anchor;
                            } else {
                                html += ", "+anchor;
                            }
                        })
                        html += "</p>";
                    }
                    var nexttest = data['next-test'];
                    if (nexttest.length > 0) {
                        // QC Fail alert
                        html += "<p class='title'>"+nexttest.length+_(" instruments disposed until new calibration tests being done")+":</p>";
                        html += "<p>";
                        $.each(nexttest, function(index, value){
                            var hrefinstr = value['url']+"/referenceanalyses";
                            var titleinstr = value['title'];
                            var anchor = "<a href='"+hrefinstr+"'>"+titleinstr+"</a>";
                            if (index == 0) {
                                html += anchor;
                            } else {
                                html += ", "+anchor;
                            }
                        })
                        html += "</p>";
                    }
                    portalAlert(html);
                }
            });
        }

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
}