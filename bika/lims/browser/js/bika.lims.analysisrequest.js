/**
 * Controller class for Analysis Request View/s
 */
function AnalysisRequestView() {

    var that = this;

    /**
     * Entry-point method for AnalysisRequestView
     */
    that.load = function() {

        // fires for all AR workflow transitions fired using the plone contentmenu workflow actions
        $("a[id^='workflow-transition']").click(transition_with_publication_spec);

    }

    function transition_with_publication_spec(event) {
        // Pass the Publication Spec UID (if present) into the WorkflowAction handler
        // Force the transition to use the "workflow_action" url instead of content_status_modify.
        // TODO This should be using content_status_modify!  modifying the href is silly.
        event.preventDefault();
        var href = event.currentTarget.href.replace("content_status_modify", "workflow_action");
        var element = $("#PublicationSpecification_uid");
        if (element.length > 0) {
            href = href + "&PublicationSpecification=" + $(element).val();
        }
        window.location.href = href
    }

}

/**
 * Controller class for Analysis Request View View
 */
function AnalysisRequestViewView() {

    var that = this;

    /**
     * Entry-point method for AnalysisRequestView
     */
    that.load = function() {

        resultsinterpretation_move_below();
        filter_CCContacts();
        set_autosave_input();
        if (document.location.href.search('/clients/') >= 0
            && $("#archetypes-fieldname-SamplePoint #SamplePoint").length > 0) {

            var cid = document.location.href.split("clients")[1].split("/")[1];
            $.ajax({
                url: window.portal_url + "/clients/" + cid + "/getClientInfo",
                type: 'POST',
                data: {'_authenticator': $('input[name="_authenticator"]').val()},
                dataType: "json",
                success: function(data, textStatus, $XHR){
                    if (data['ClientUID'] != '') {
                        var spelement = $("#archetypes-fieldname-SamplePoint #SamplePoint");
                        var base_query=$.parseJSON($(spelement).attr("base_query"));
                        var setup_uid = $("#bika_setup").attr("bika_samplepoints");
                        base_query["getClientUID"] = [data['ClientUID'], setup_uid];
                        $(spelement).attr("base_query", $.toJSON(base_query));
                        var options = $.parseJSON($(spelement).attr("combogrid_options"));
                        options.url = window.location.href.split("/ar")[0] + "/" + options.url;
                        options.url = options.url + "?_authenticator=" + $("input[name='_authenticator']").val();
                        options.url = options.url + "&catalog_name=" + $(spelement).attr("catalog_name");
                        options.url = options.url + "&base_query=" + $.toJSON(base_query);
                        options.url = options.url + "&search_query=" + $(spelement).attr("search_query");
                        options.url = options.url + "&colModel=" + $.toJSON( $.parseJSON($(spelement).attr("combogrid_options")).colModel);
                        options.url = options.url + "&search_fields=" + $.toJSON($.parseJSON($(spelement).attr("combogrid_options")).search_fields);
                        options.url = options.url + "&discard_empty=" + $.toJSON($.parseJSON($(spelement).attr("combogrid_options")).discard_empty);
                        options.force_all="false";
                        $(spelement).combogrid(options);
                        $(spelement).addClass("has_combogrid_widget");
                        $(spelement).attr("search_query", "{}");
                    }
                }
            });
        }

    }

    function resultsinterpretation_move_below(){
        // By default show only the Results Interpretation for the whole AR, not Dept specific
        $('a.department-tab').click(function(e) {
            e.preventDefault();
            var uid = $(this).attr('data-uid');
            $('.department-area').not(':[id="'+uid+'"]').hide();
            $('.department-area:[id="'+uid+'"]').show();
            $('a.department-tab.selected').removeClass('selected');
            $(this).addClass('selected');
        });
        $('a.department-tab:[data-uid="ResultsInterpretationDepts-general"]').click();

        //Remove buttons from TinyMCE
        setTimeout(function() {
            $("div.arresultsinterpretation-container .fieldTextFormat").remove();
            $("table.mceToolbar a.mce_image").remove();
            $("table.mceToolbar a.mce_code").remove();
            $('table.mceToolbar a.mce_save').hide();
        }, 1500);
    }

    function filter_CCContacts(){
        /**
         * Filter the CCContacts dropdown list by the current client.
         */
        if ($('#CCContact').length > 0) {
            var element = $('#CCContact');
            var clientUID = getClientUID();
            filter_by_client(element, "getParentUID", clientUID);
        }
    }

    function getClientUID(){
        /**
         * Return the AR client's UID.
         */
        var clientid =  window.location.href.split("clients")[1].split("/")[1];
        // ajax petition to obtain the current client info
        var clientuid = "";
        $.ajax({
            url: window.portal_url + "/clients/" + clientid + "/getClientInfo",
            type: 'POST',
            async: false,
            data: {'_authenticator': $('input[name="_authenticator"]').val()},
            dataType: "json",
            success: function(data, textStatus, $XHR){
                if (data['ClientUID'] != '') {
                    clientuid = data['ClientUID'] != '' ? data['ClientUID'] : null;
                }
            }
        });
        return clientuid;
    }

    function filter_by_client(element, filterkey, filtervalue) {
        /**
         * Filter the dropdown's results (called element) by current client contacts.
         */
        // Get the base_query data in array format
        var base_query= $.parseJSON($(element).attr("base_query"));
        base_query[filterkey] = filtervalue;
        $(element).attr("base_query", $.toJSON(base_query));
        var options = $.parseJSON($(element).attr("combogrid_options"));
        $(element).attr("base_query", $.toJSON(base_query));
        $(element).attr("combogrid_options", $.toJSON(options));
        referencewidget_lookups($(element));
    }

    function set_autosave_input() {
        /**
         * Set an event for each input field in the AR header. After write something in the input field and
         * focus out it, the event automatically saves the change.
         */
        $("table.header_table input").not('[attr="referencewidget"').not('[type="hidden"]').each(function(i){
            // Save input fields
            $(this).change(function () {
                var pointer = this;
                build_typical_save_request(pointer);
            });
        });
        $("table.header_table select").not('[type="hidden"]').each(function(i) {
            // Save select fields
            $(this).change(function () {
                var pointer = this;
                build_typical_save_request(pointer);
            });
        });
        $("table.header_table input.referencewidget").not('[type="hidden"]').not('[id="CCContact"]').each(function(i) {
            // Save referencewidget inputs.
            $(this).bind("selected", (function() {
                var requestdata={};
                var pointer = this;
                var fieldvalue, fieldname;
                setTimeout(function() {
                        fieldname = $(pointer).closest('div[id^="archetypes-fieldname-"]').attr('data-fieldname');
                        fieldvalue = $(pointer).attr('uid');
                        // To search by uid, we should follow this array template:
                        // { SamplePoint = "uid:TheValueOfuid1|uid:TheValueOfuid2..." }
                        // This is the way how jsonapi/__init__.py/resolve_request_lookup() works.
                        requestdata[fieldname] = 'uid:' + fieldvalue;
                        save_elements(requestdata);
                    },
                    500);
            }));
        });
        $("table.header_table input#CCContact.referencewidget").not('[type="hidden"]').each(function(i) {
            // CCContact works different.
            $(this).bind("selected", (function() {
                var pointer = this;
                var fieldvalue, fieldname, requestdata = {};
                setTimeout(function() {
                        // To search by uid, we should follow this array template:
                        // { SamplePoint = "uid:TheValueOfuid1|uid:TheValueOfuid2..." }
                        // This is the way how jsonapi/__init__.py/resolve_request_lookup() works.
                        fieldname = $(pointer).closest('div[id^="archetypes-fieldname-"]').attr('data-fieldname');
                        fieldvalue = parse_CCClist();
                        requestdata[fieldname] = fieldvalue;
                        save_elements(requestdata);
                    },
                    500);
            }));
        });
        $('img[fieldname="CCContact"]').each(function() {
            // If a delete cross is clicked on CCContact-listing, we should update the saved list.
            var fieldvalue, requestdata = {}, fieldname;
            $(this).click(function() {
                fieldname = $(this).attr('fieldname');
                setTimeout(function() {
                    fieldvalue = parse_CCClist();
                    requestdata[fieldname] = fieldvalue;
                    save_elements(requestdata);
                });
            });
        });
    }

    function build_typical_save_request(pointer) {
        /**
         * Build an array with the data to be saved for the typical data fields.
         * @pointer is the object which has been modified and we want to save its new data.
         */
        var fieldvalue, fieldname, requestdata={};
        // Checkbox
        if ( $(pointer).attr('type') == "checkbox" ) {
            // Checkboxes name is located in its parent div, but its value is located inside the input.
            fieldvalue = $(pointer).prop('checked');
            fieldname = $(pointer).closest('div[id^="archetypes-fieldname-"]').attr('data-fieldname');
        }
        // Other input
        else {
            fieldvalue = $(pointer).val();
            fieldname = $(pointer).closest('div[id^="archetypes-fieldname-"]').attr('data-fieldname');
        }
        requestdata[fieldname] = fieldvalue;
        save_elements(requestdata);
    }

    function save_elements(requestdata) {
        /**
         * Given a dict with a fieldname and a fieldvalue, save this data via ajax petition.
         * @requestdata should has the format  {fieldname=fieldvalue} ->  { ReportDryMatter=false}.
         */
        var url = window.location.href.replace('/base_view', '');
        var obj_path = url.replace(window.portal_url, '');
        // Staff for the notification
        var element,name = $.map(requestdata, function(element,index) {return element, index});
        name = $.trim($('[data-fieldname="' + name + '"]').closest('td').prev().text());
        var ar = $.trim($('.documentFirstHeading').text());
        var anch =  "<a href='"+ url + "'>" + ar + "</a>";
        // Needed fot the ajax petition
        requestdata['obj_path']= obj_path;
        $.ajax({
            type: "POST",
            url: window.portal_url+"/@@API/update",
            data: requestdata
        })
        .done(function(data) {
            //success alert
            if (data != null && data['success'] == true) {
                bika.lims.SiteView.notificationPanel(anch + ': ' + name + ' updated successfully', "succeed");
            } else {
                bika.lims.SiteView.notificationPanel('Error while updating ' + name + ' for '+ anch, "error");
                var msg = '[bika.lims.analysisrequest.js] Error while updating ' + name + ' for '+ ar;
                console.warn(msg);
                window.bika.lims.error(msg);
            }
        })
        .fail(function(){
            //error
            bika.lims.SiteView.notificationPanel('Error while updating ' + name + ' for '+ anch, "error");
            var msg = '[bika.lims.analysisrequest.js] Error while updating ' + name + ' for '+ ar;
            console.warn(msg);
            window.bika.lims.error(msg);
        });
    }

    function parse_CCClist() {
        /**
         * It parses the CCContact-listing, where are located the CCContacts, and build the fieldvalue list.
         * @return: the builed field value -> "uid:TheValueOfuid1|uid:TheValueOfuid2..."
         */
        var fieldvalue = '';
        $('#CCContact-listing').children('.reference_multi_item').each(function (ii) {
            if (fieldvalue.length < 1) {
                fieldvalue = 'uid:' + $(this).attr('uid');
            }
            else {
                fieldvalue = fieldvalue + '|uid:' + $(this).attr('uid');
            }
        });
        return fieldvalue;
    }
}

/**
 * Controller class for Analysis Request Manage Results view
 */
function AnalysisRequestManageResultsView() {

    var that = this;

    /**
     * Entry-point method for AnalysisRequestManageResultsView
     */
    that.load = function() {

        // Set the analyst automatically when selected in the picklist
        $('.portaltype-analysisrequest .bika-listing-table td.Analyst select').change(function() {
            var analyst = $(this).val();
            var key = $(this).closest('tr').attr('keyword');
            var obj_path = window.location.href.replace(window.portal_url, '');
            var obj_path_split = obj_path.split('/');
            if (obj_path_split.length > 4) {
                obj_path_split[obj_path_split.length-1] = key;
            } else {
                obj_path_split.push(key);
            }
            obj_path = obj_path_split.join('/');
            $.ajax({
                type: "POST",
                url: window.portal_url+"/@@API/update",
                data: {"obj_path": obj_path,
                       "Analyst":  analyst}
            });
        });

    }
}


/**
 * Controller class for Analysis Request Analyses view
 */
function AnalysisRequestAnalysesView() {

    var that = this;

    /**
     * Entry-point method for AnalysisRequestAnalysesView
     */
    that.load = function() {

        $("[name^='min\\.'], [name^='max\\.'], [name^='error\\.']").live("change", function(){
            validate_spec_field_entry(this);
        });

        ////////////////////////////////////////
        // disable checkboxes for eg verified analyses.
        $.each($("[name='uids:list']"), function(x,cb){
            var service_uid = $(cb).val();
            var row_data = $.parseJSON($("#"+service_uid+"_row_data").val());
            if (row_data.disabled === true){
                // disabled fields must be shadowed by hidden fields,
                // or they don't appear in the submitted form.
                $(cb).prop("disabled", true);
                var cbname = $(cb).attr("name");
                var cbid = $(cb).attr("id");
                $(cb).removeAttr("name").removeAttr("id");
                $(cb).after("<input type='hidden' name='"+cbname+"' value='"+service_uid+"' id='"+cbid+"'/>");

                var el = $("[name='Price."+service_uid+":records']");
                var elname = $(el).attr("name");
                var elval = $(el).val();
                $(el).after("<input type='hidden' name='"+elname+"' value='"+elval+"'/>");
                $(el).prop("disabled", true);

                el = $("[name='Partition."+service_uid+":records']");
                elname = $(el).attr("name");
                elval = $(el).val();
                $(el).after("<input type='hidden' name='"+elname+"' value='"+elval+"'/>");
                $(el).prop("disabled", true);

                var specfields = ["min", "max", "error"];
                for(var i in specfields) {
                    var element = $("[name='"+specfields[i]+"."+service_uid+":records']");
                    var new_element = "" +
                        "<input type='hidden' field='"+specfields[i]+"' value='"+element.val()+"' " +
                        "name='"+specfields[i]+"."+service_uid+":records' uid='"+service_uid+"'>";
                    $(element).replaceWith(new_element);
                }
            }
        });

        ////////////////////////////////////////
        // checkboxes in services list
        $("[name='uids:list']").live("click", function(){
            calcdependencies([this]);
            var service_uid = $(this).val();
            if ($(this).prop("checked")){
                check_service(service_uid);
            } else {
                uncheck_service(service_uid);
            }
        });

    }

    function validate_spec_field_entry(element) {
        var uid = $(element).attr("uid");
        // no spec selector here yet!
        // $("[name^='ar\\."+sb_col+"\\.Specification']").val("");
        // $("[name^='ar\\."+sb_col+"\\.Specification_uid']").val("");
        var min_element = $("[name='min\\."+uid+"\\:records']");
        var max_element = $("[name='max\\."+uid+"\\:records']");
        var error_element = $("[name='error\\."+uid+"\\:records']");
        var min = parseFloat($(min_element).val(), 10);
        var max = parseFloat($(max_element).val(), 10);
        var error = parseFloat($(error_element).val(), 10);

        if($(element).attr("name") == $(min_element).attr("name")){
            if(isNaN(min)) {
                $(min_element).val("");
            } else if ((!isNaN(max)) && min > max) {
                $(max_element).val("");
            }
        } else if($(element).attr("name") == $(max_element).attr("name")){
            if(isNaN(max)) {
                $(max_element).val("");
            } else if ((!isNaN(min)) && max < min) {
                $(min_element).val("");
            }
        } else if($(element).attr("name") == $(error_element).attr("name")){
            if(isNaN(error) || error < 0 || error > 100){
                $(error_element).val("");
            }
        }
    }

    function check_service(service_uid){
        var new_element, element;

        // Add partition dropdown
        element = $("[name='Partition."+service_uid+":records']");
        new_element = "" +
            "<select class='listing_select_entry' "+
            "name='Partition."+service_uid+":records' "+
            "field='Partition' uid='"+service_uid+"' "+
            "style='font-size: 100%'>";
        $.each($("td.PartTitle"), function(i,v){
            var partid = $($(v).children()[1]).text();
            new_element = new_element + "<option value='"+partid+"'>"+partid+"</option>";
        });
        new_element = new_element + "</select>";
        $(element).replaceWith(new_element);

        // Add price field
        var logged_in_client = $("input[name='logged_in_client']").val();
        if (logged_in_client != "1") {
            element = $("[name='Price."+service_uid+":records']");
            new_element = "" +
                "<input class='listing_string_entry numeric' "+
                "name='Price."+service_uid+":records' "+
                "field='Price' type='text' uid='"+service_uid+"' "+
                "autocomplete='off' style='font-size: 100%' size='5' "+
                "value='"+$(element).val()+"'>";
            $($(element).siblings()[1]).remove();
            $(element).replaceWith(new_element);
        }

        // spec fields
        var specfields = ["min", "max", "error"];
        for(var i in specfields) {
            element = $("[name='"+specfields[i]+"."+service_uid+":records']");
            new_element = "" +
                "<input class='listing_string_entry numeric' type='text' size='5' " +
                "field='"+specfields[i]+"' value='"+$(element).val()+"' " +
                "name='"+specfields[i]+"."+service_uid+":records' " +
                "uid='"+service_uid+"' autocomplete='off' style='font-size: 100%'>";
            $(element).replaceWith(new_element);
        }

    }

    function uncheck_service(service_uid){
        var new_element, element;

        element = $("[name='Partition."+service_uid+":records']");
        new_element = "" +
            "<input type='hidden' name='Partition."+service_uid+":records' value=''/>";
        $(element).replaceWith(new_element);

        var logged_in_client = $("input[name='logged_in_client']").val();
        if (logged_in_client != "1") {
            element = $("[name='Price."+service_uid+":records']");
            $($(element).siblings()[0])
                .after("<span class='state-active state-active '>"+$(element).val()+"</span>");
            new_element = "" +
                "<input type='hidden' name='Price."+service_uid+":records' value='"+$(element).val()+"'/>";
            $(element).replaceWith(new_element);
        }

        var specfields = ["min", "max", "error"];
        for(var i in specfields) {
            element = $("[name='"+specfields[i]+"."+service_uid+":records']");
            new_element = "" +
                "<input type='hidden' field='"+specfields[i]+"' value='"+element.val()+"' " +
                "name='"+specfields[i]+"."+service_uid+":records' uid='"+service_uid+"'>";
            $(element).replaceWith(new_element);
        }

    }

    function add_Yes(dlg, element, dep_services){
        for(var i = 0; i<dep_services.length; i++){
            var service_uid = dep_services[i].Service_uid;
            if(! $("#list_cb_"+service_uid).prop("checked") ){
                check_service(service_uid);
                $("#list_cb_"+service_uid).prop("checked",true);
            }
        }
        $(dlg).dialog("close");
        $("#messagebox").remove();
    }

    function add_No(dlg, element){
        if($(element).prop("checked") ){
            uncheck_service($(element).attr("value"));
            $(element).prop("checked",false);
        }
        $(dlg).dialog("close");
        $("#messagebox").remove();
    }

    function calcdependencies(elements, auto_yes) {
        /*jshint validthis:true */
        auto_yes = auto_yes || false;
        jarn.i18n.loadCatalog('bika');
        var _ = window.jarn.i18n.MessageFactory("bika");

        var dep;
        var i, cb;

        var lims = window.bika.lims;

        for(var elements_i = 0; elements_i < elements.length; elements_i++){
            var dep_services = [];  // actionable services
            var dep_titles = [];
            var element = elements[elements_i];
            var service_uid = $(element).attr("value");
            // selecting a service; discover dependencies
            if ($(element).prop("checked")){
                var Dependencies = lims.AnalysisService.Dependencies(service_uid);
                for(i = 0; i<Dependencies.length; i++) {
                    dep = Dependencies[i];
                    if ($("#list_cb_"+dep.Service_uid).prop("checked") ){
                        continue; // skip if checked already
                    }
                    dep_services.push(dep);
                    dep_titles.push(dep.Service);
                }
                if (dep_services.length > 0) {
                    if (auto_yes) {
                        add_Yes(this, element, dep_services);
                    } else {
                        var html = "<div id='messagebox' style='display:none' title='" + _("Service dependencies") + "'>";
                        html = html + _("<p>${service} requires the following services to be selected:</p>"+
                                                        "<br/><p>${deps}</p><br/><p>Do you want to apply these selections now?</p>",
                                                        {
                                                            service: $(element).attr("title"),
                                                            deps: dep_titles.join("<br/>")
                                                        });
                        html = html + "</div>";
                        $("body").append(html);
                        $("#messagebox").dialog({
                            width:450,
                            resizable:false,
                            closeOnEscape: false,
                            buttons:{
                                yes: function(){
                                    add_Yes(this, element, dep_services);
                                },
                                no: function(){
                                    add_No(this, element);
                                }
                            }
                        });
                    }
                }
            }
            // unselecting a service; discover back dependencies
            else {
                var Dependants = lims.AnalysisService.Dependants(service_uid);
                for (i=0; i<Dependants.length; i++){
                    dep = Dependants[i];
                    cb = $("#list_cb_" + dep.Service_uid);
                    if (cb.prop("checked")){
                        dep_titles.push(dep.Service);
                        dep_services.push(dep);
                    }
                }
                if(dep_services.length > 0){
                    if (auto_yes) {
                        for(i=0; i<dep_services.length; i+=1) {
                            dep = dep_services[i];
                            service_uid = dep.Service_uid;
                            cb = $("#list_cb_" + dep.Service_uid);
                            uncheck_service(dep.Service_uid);
                            $(cb).prop("checked", false);
                        }
                    } else {
                        $("body").append(
                            "<div id='messagebox' style='display:none' title='" + _("Service dependencies") + "'>"+
                            _("<p>The following services depend on ${service}, and will be unselected if you continue:</p><br/><p>${deps}</p><br/><p>Do you want to remove these selections now?</p>",
                                {service:$(element).attr("title"),
                                deps: dep_titles.join("<br/>")})+"</div>");
                        $("#messagebox").dialog({
                            width:450,
                            resizable:false,
                            closeOnEscape: false,
                            buttons:{
                                yes: function(){
                                    for(i=0; i<dep_services.length; i+=1) {
                                        dep = dep_services[i];
                                        service_uid = dep.Service_uid;
                                        cb = $("#list_cb_" + dep.Service_uid);
                                        $(cb).prop("checked", false);
                                        uncheck_service(dep.Service_uid);
                                    }
                                    $(this).dialog("close");
                                    $("#messagebox").remove();
                                },
                                no:function(){
                                    service_uid = $(element).attr("value");
                                    check_service(service_uid);
                                    $(element).prop("checked", true);
                                    $("#messagebox").remove();
                                    $(this).dialog("close");
                                }
                            }
                        });
                    }
                }
            }
        }
    }
}
