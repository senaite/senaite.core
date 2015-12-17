/* Controller class for AnalysisRequestAddView - column layout.
 *
 * The form elements are not submitted.  Instead, their values are inserted
 * into bika.lims.ar_add.state, and this variable is submitted as a json
 * string.
 *
 *
 * Regarding checkboxes: JQuery recommends using .prop() instead of .attr(),
 * but selenium/xpath cannot discover the state of such inputs.  I use
 * .attr("checked",true) and .removeAttr("checked") to set their values,
 * although .prop("checked") is still the correct way to check state of
 * a particular element from JS.
 */

function AnalysisRequestAddByCol() {
    "use strict";

    var that = this

    that.load = function () {

        // disable browser autocomplete
        $('input[type=text]').prop('autocomplete', 'off')

        // load-time form configuration
        form_init()

        //// Handy for the debugging; alerts when a certain selector's 'value' is changed
        // var selector = input[id*='0_uid']
        // Object.defineProperty(document.querySelector(selector), 'value', {
        //  set: function (value) {
        //      if(!value || value.length < 2)
        //      {
        //          debugger;
        //      }
        //  }
        //})

        /*
         The state variable is fully populated when the form is submitted,
         but in many cases it must be updated on the fly, to allow the form
         to change behaviour based on some selection.  To help with this,
         there are some generic state-setting handlers below, but these must
         be augmented with specific handlers for difficult cases.
         */
        checkbox_change()
        referencewidget_change()
        select_element_change()
        textinput_change()
        copybutton_selected()

        client_selected()
        contact_selected()
        cc_contacts_deletebtn_click()
        spec_field_entry()
        spec_selected()
        samplepoint_selected()
        sampletype_selected()
        profile_selected();
        profile_unset_trigger();
        template_selected()
        drymatter_selected()
        sample_selected()

        singleservice_dropdown_init()
        singleservice_deletebtn_click()
        analysis_cb_click()

        category_header_clicked()

        //      sample_selected()

        form_submit()

        fix_table_layout();
        from_sampling_round();
    };

    /*
     * Exposes the filter_combogrid method publicly.
     * Accessible through window.bika.lims.AnalysisRequestAddByCol.filter_combogrid
     */
    that.filter_combogrid = function(element, filterkey, filtervalue, querytype) {
        filter_combogrid(element,filterkey,filtervalue,querytype);
    };

    // Form management, and utility functions //////////////////////////////////
    /* form_init - load time form config
     * state_set - should be used when setting fields in the state var
     * filter_combogrid - filter an existing dropdown (referencewidget)
     * filter_by_client - Grab the client UID and filter all applicable dropdowns
     * get_arnum(element) - convenience to compensate for different form layouts.
     */

    function form_init() {
        /* load-time form configuration
         *
         * - Create empty state var
         * - fix generated elements
         * - clear existing values (on page reload)
         * - filter fields based on the selected Client
         */
        // Create empty state var
        // We include initialisation for a couple of special fields that
        // do not directly tie to specific form controls
        bika.lims.ar_add = {}
        bika.lims.ar_add.state = {}
        var nr_ars = parseInt($('input[id="ar_count"]').val(), 10)
        for (var arnum = 0; arnum < nr_ars; arnum++) {
            bika.lims.ar_add.state[arnum] = {
                'Analyses': []
            }
        }
        // Remove "required" attribute; we will manage this manually, later.
        var elements = $("input[type!='hidden']").not("[disabled]")
        for (var i = elements.length - 1; i >= 0; i--) {
            var element = elements[i]
            $(element).removeAttr("required")
        }
        // All Archetypes generated elements are given an ID <fieldname>, and
        // this means there are duplicated IDs in the form.  I will change
        // their IDs to <fieldname>_<arnum> to prevent this.
        $.each($("[id^='archetypes-fieldname']"), function (i, div) {
            var arnum = $(div).parents("[arnum]").attr("arnum")
            var fieldname = $(div).parents("[fieldname]").attr("fieldname")
            var e
            // first rename the HTML elements
            if ($(div).hasClass('ArchetypesSelectionWidget')) {
                e = $(div).find('select')[0]
                $(e).attr('id', fieldname + '-' + arnum)
                $(e).attr('name', fieldname + '-' + arnum)
            }
            if ($(div).hasClass('ArchetypesReferenceWidget')) {
                e = $(div).find('[type="text"]')[0]
                $(e).attr('id', $(e).attr('id') + '-' + arnum)
                $(e).attr('name', $(e).attr('name') + '-' + arnum)
                e = $(div).find('[id$="_uid"]')[0]
                $(e).attr('id', fieldname + '-' + arnum + '_uid')
                $(e).attr('name', fieldname + '-' + arnum + '_uid')
                e = $(div).find('[id$="-listing"]')
                if (e.length > 0) {
                    $(e).attr('id', fieldname + '-' + arnum + '-listing')
                }
            }
            if ($(div).hasClass('ArchetypesStringWidget')
                || $(div).hasClass('ArchetypesDateTimeWidget')) {
                e = $(div).find('[type="text"]')[0]
                $(e).attr('id', $(e).attr('id') + '-' + arnum)
                $(e).attr('name', $(e).attr('name') + '-' + arnum)
            }
            if ($(div).hasClass('ArchetypesBooleanWidget')) {
                e = $(div).find('[type="checkbox"]')[0]
                $(e).attr('id', $(e).attr('id') + '-' + arnum)
                $(e).attr('name', $(e).attr('name') + '-' + arnum + ':boolean')
                e = $(div).find('[type="hidden"]')[0]
                $(e).attr('name', $(e).attr('name') + '-' + arnum + ':boolean:default')
            }
            // then change the ID of the containing div itself
            $(div).attr('id', 'archetypes-fieldname-' + fieldname + '-' + arnum)
        })

        // clear existing values (on page reload).
        $("#singleservice").val("")
        $("#singleservice").attr("uid", "new")
        $("#singleservice").attr("title", "")
        $("#singleservice").parents("[uid]").attr("uid", "new")
        $("#singleservice").parents("[keyword]").attr("keyword", "")
        $("#singleservice").parents("[title]").attr("title", "")
        $("input[type='checkbox']").removeAttr("checked")
        $(".min,.max,.error").val("")

        // filter fields based on the selected Client
        // we need a little delay here to be sure the elements have finished
        // initialising before we attempt to filter them
        setTimeout(function () {
            var nr_ars = parseInt($("#ar_count").val(), 10)
            for (arnum = 0; arnum < nr_ars; arnum++) {
                filter_by_client(arnum)
            }
        }, 250);
    }

    function state_set(arnum, fieldname, value) {
        /* Use this function to set values in the state variable.
         */
        var arnum_i = parseInt(arnum, 10)
        if (fieldname && value !== undefined) {
            // console.log("arnum=" + arnum + ", fieldname=" + fieldname + ", value=" + value)
            bika.lims.ar_add.state[arnum_i][fieldname] = value
        }
    }

    function from_sampling_round(){
        // Checking if the request comes from a sampling round
        var sPageURL = decodeURIComponent(window.location.search.substring(1)),
        sURLVariables = sPageURL.split('&'),
        sParameterName;
        for (var i = 0; i < sURLVariables.length; i++) {
            sParameterName = sURLVariables[i].split('=');
            if (sParameterName[0] === 'samplinground') {
                // If the request comes from a sampling round, we have to set up the form with the sampling round info
                var samplinground_UID = sParameterName[1];
                setupSamplingRoundInfo(samplinground_UID);
            }
        }
    }

    function setupSamplingRoundInfo(samplinground_UID){
        /**
         * This function sets up the sampling round information such as the sampling round to use and the
         * different analysis request templates needed.
         * :samplinground_uid: a string with the sampling round uid
         */
        var request_data = {
            catalog_name: "portal_catalog",
            portal_type: "SamplingRound",
            UID: samplinground_UID,
            include_fields: ["Title", "UID", "analysisRequestTemplates", "samplingRoundSamplingDate"]
        };
        window.bika.lims.jsonapi_read(request_data, function (data) {
            if (data.objects.length > 0) {
                var spec = data.objects[0];
                // Selecting the sampling round
                var sr = $('input[id^="SamplingRound-"]');
                // Filling out and halting the sampling round fields
                sr.attr('uid', spec['UID'])
                    .val(spec['Title'])
                    .attr('uid_check', spec['UID'])
                    .attr('val_check', spec['Title'])
                    .attr('disabled','disabled');
                $('[id^="SamplingRound-"][id$="_uid"]').val(spec['UID']);
                // Filling out and halting the analysis request templates fields
                var ar_templates = $('input[id^="Template-"]:visible');
                ar_templates.each(function(index, element){
                    $(element).attr('uid', spec['analysisRequestTemplates'][index][1])
                    .val(spec['analysisRequestTemplates'][index][0])
                    .attr('uid_check', spec['analysisRequestTemplates'][index][1])
                    .attr('val_check', spec['analysisRequestTemplates'][index][1])
                    .attr('disabled','disabled');
                    $('input#Template-' + index + '_uid').val(spec['analysisRequestTemplates'][index][1]);
                    template_set(index);
                });
                // Writing the sampling date
                $('input[id^="SamplingDate-"]:visible').val(spec['samplingRoundSamplingDate']);
                // Hiding all fields which depends on the sampling round
                var to_disable = ['Specification', 'SamplePoint', 'ReportDryMatter', 'Sample', 'Batch',
                    'SubGroup', 'SamplingDate', 'Composite', 'Profiles', 'DefaultContainerType', 'AdHoc'];
                for (var i=0; to_disable.length > i; i++) {
                    $('tr[fieldname="' + to_disable[i] + '"]').hide();
                }
                var sampleTypes = $('input[id^="SampleType-"]');
                sampleTypes.each(function(index, element){
                        // We have to hide the field
                        if ($(element).attr('uid')){
                            $(element).attr('disabled','disabled')
                        }
                    }
                );
                // Hiding prices
                $('table.add tfoot').hide();
                // Hiding not needed services
                $('th.collapsed').hide();
                // Disabling service checkboxes
                setTimeout(function () {
                    // Some function enables the services checkboxes with a lot of delay caused by AJAX, so we
                    // need this setTimeout
                    $('input[selector^="bika_analysisservices"]').attr("disabled", true);
                    $('input[selector^="ar."][type="checkbox"]').attr("disabled", true);
                    $('input.min, input.max, input.error').attr("disabled", true);
                }, 1000);
            }
        });
    }

    function filter_combogrid(element, filterkey, filtervalue, querytype) {
        /* Apply or modify a query filter for a reference widget.
         *
         *  This will set the options, then re-create the combogrid widget
         *  with the new filter key/value.
         *
         *  querytype can be 'base_query' or 'search_query'.
         */
        if (!$(element).is(':visible')) {
            return
        }
        if (!querytype) {
            querytype = 'base_query'
        }
        var query = $.parseJSON($(element).attr(querytype))
        query[filterkey] = filtervalue
        $(element).attr(querytype, $.toJSON(query))
        var options = $.parseJSON($(element).attr("combogrid_options"))
        options.url = window.location.href.split("/ar_add")[0] + "/" + options.url
        options.url = options.url + "?_authenticator=" + $("input[name='_authenticator']").val()
        options.url = options.url + "&catalog_name=" + $(element).attr("catalog_name")
        if (querytype == 'base_query') {
            options.url = options.url + "&base_query=" + $.toJSON(query)
            options.url = options.url + "&search_query=" + $(element).attr("search_query")
        }
        else {
            options.url = options.url + "&base_query=" + $(element).attr("base_query")
            options.url = options.url + "&search_query=" + $.toJSON(query)
        }
        options.url = options.url + "&colModel=" + $.toJSON($.parseJSON($(element).attr("combogrid_options")).colModel)
        options.url = options.url + "&search_fields=" + $.toJSON($.parseJSON($(element).attr("combogrid_options"))['search_fields'])
        options.url = options.url + "&discard_empty=" + $.toJSON($.parseJSON($(element).attr("combogrid_options"))['discard_empty'])
        options.force_all = "false"
        $(element).combogrid(options)
        $(element).attr("search_query", "{}")
    }

    function filter_by_client(arnum) {
        /***
         * Filter all Reference fields that reference Client items
         *
         * Some reference fields can select Lab or Client items.  In these
         * cases, the 'getParentUID' or 'getClientUID' index is used
         * to filter against Lab and Client folders.
         */
        var element, uids
        var uid = $($("tr[fieldname='Client'] td[arnum='" + arnum + "'] input")[0]).attr("uid")
        element = $("tr[fieldname=Contact] td[arnum=" + arnum + "] input")[0]
        filter_combogrid(element, "getParentUID", uid)
        element = $("tr[fieldname=CCContact] td[arnum=" + arnum + "] input")[0]
        filter_combogrid(element, "getParentUID", uid)
        element = $("tr[fieldname=InvoiceContact] td[arnum=" + arnum + "] input")[0]
        filter_combogrid(element, "getParentUID", uid)
        uids = [uid, $("#bika_setup").attr("bika_samplepoints_uid")]
        element = $("tr[fieldname=SamplePoint] td[arnum=" + arnum + "] input")[0]
        filter_combogrid(element, "getClientUID", uids)
        uids = [uid, $("#bika_setup").attr("bika_artemplates_uid")]
        element = $("tr[fieldname=Template] td[arnum=" + arnum + "] input")[0]
        filter_combogrid(element, "getClientUID", uids)
        uids = [uid, $("#bika_setup").attr("bika_analysisprofiles_uid")]
        element = $("tr[fieldname=Profiles] td[arnum=" + arnum + "] input")[0]
        filter_combogrid(element, "getClientUID", uids)
        uids = [uid, $("#bika_setup").attr("bika_analysisspecs_uid")]
        element = $("tr[fieldname=Specification] td[arnum=" + arnum + "] input")[0]
        filter_combogrid(element, "getClientUID", uids)
    }

    function hashes_to_hash(hashlist, key) {
        /* Convert a list of hashes to a hash, by one of their keys.
         *
         * This will return a single hash: the key that will be used must
         * of course exist in all hashes in hashlist.
         */
        var ret = {}
        for (var i = 0; i < hashlist.length; i++) {
            ret[hashlist[i][key]] = hashlist[i]
        }
        return ret
    }

    function hash_to_hashes(hash) {
        /* Convert a single hash into a list of hashes
         *
         * Basically, this just returns the keys, unmodified.
         */
        var ret = []
        $.each(hash, function (i, v) {
            ret.push(v)
        })
        return ret
    }

    function get_arnum(element) {
        // Should be able to deduce the arnum of any form element
        var arnum
        // Most AR schema field widgets have [arnum=<arnum>] on their parent TD
        arnum = $(element).parents("[arnum]").attr("arnum")
        if (arnum) {
            return arnum
        }
        // analysisservice checkboxes have an ar.<arnum> class on the parent TD
        var td = $(element).parents("[class*='ar\\.']")
        if (td.length > 0) {
            var arnum = $(td).attr("class").split('ar.')[1].split()[0]
            if (arnum) {
                return arnum
            }
        }
        console.error("No arnum found for element " + element)
    }

    function destroy(arr, val) {
        for (var i = 0; i < arr.length; i++) {
            if (arr[i] === val) {
                arr.splice(i, 1);
            }
        }
        return arr;
    }

    // Generic handlers for more than one field  ///////////////////////////////
    /*
     checkbox_change - applies to all except analysis services
     checkbox_change_handler
     referencewidget_change - applies to all except #singleservice
     referencewidget_change_handler
     select_element_change - select elements are a bit different
     select_element_change_handler
     textinput_change - all except referencwidget text elements
     textinput_change_handler
     */

    function checkbox_change_handler(element) {
        var arnum = get_arnum(element)
        var fieldname = $(element).parents('[fieldname]').attr('fieldname')
        var value = $(element).prop("checked")
        state_set(arnum, fieldname, value)
    }

    function checkbox_change() {
        /* Generic state-setter for AR field checkboxes
         * The checkboxes used to select analyses are handled separately.
         */
        $('tr[fieldname] input[type="checkbox"]')
            .live('change copy', function () {
                checkbox_change_handler(this)
            })
            .each(function (i, e) {
                // trigger copy on form load
                $(e).trigger('copy')
            })
    }

    function referencewidget_change_handler(element, item) {
        var arnum = get_arnum(element)
        var fieldname = $(element).parents('[fieldname]').attr('fieldname')
        var multiValued = $(element).attr("multiValued") == "1"
        var value = item.UID
        if (multiValued) {
            // modify existing values
            var uid_element = $(element).siblings("input[name*='_uid']")
            var existing_values = $(uid_element).val()
            if (existing_values.search(value) == -1) {
                value = existing_values + "," + value
            } else {
                value = existing_values
            }
        }
        state_set(arnum, fieldname, value)
    }

    function referencewidget_change() {
        /* Generic state-setter for AR field referencewidgets
         */
        $('tr[fieldname] input.referencewidget')
            .live('selected', function (event, item) {
                referencewidget_change_handler(this, item)
            })
        // we must create a fake 'item' for this handler
        $('tr[fieldname] input.referencewidget')
            .live('copy', function (event) {
                var item = {UID: $(this).attr('uid')}
                referencewidget_change_handler(this, item)
            })
    }

    function select_element_change_handler(element) {
        var arnum = get_arnum(element)
        var fieldname = $(element).parents('[fieldname]').attr('fieldname')
        var value = $(element).val()
        state_set(arnum, fieldname, value)
    }

    function select_element_change() {
        /* Generic state-setter for SELECT inputs
         */
        $('tr[fieldname] select')
            .live('change copy', function (event, item) {
                select_element_change_handler(this)
            })
            .each(function (i, e) {
                // trigger copy on form load
                $(e).trigger('copy')
            })
    }

    function textinput_change_handler(element) {
        var arnum = get_arnum(element)
        var fieldname = $(element).parents('[fieldname]').attr('fieldname')
        var value = $(element).val()
        state_set(arnum, fieldname, value)
    }

    function textinput_change() {
        /* Generic state-setter for SELECT inputs
         */
        $('tr[fieldname] input[type="text"]')
            .not("#singleservice")
            .not(".referencewidget")
            .live('change copy', function () {
                textinput_change_handler(this)
            })
            .each(function (i, e) {
                if ($(e).val()) {
                    // trigger copy on form load
                    $(e).trigger('copy')
                }
            })
    }

    function copybutton_selected() {
        $('img.copybutton').live('click', function () {
            var nr_ars = parseInt($('input[id="ar_count"]').val(), 10);
            var tr = $(this).parents('tr')[0];
            var fieldname = $(tr).attr('fieldname');
            var td1 = $(tr).find('td[arnum="0"]')[0];
            var e, td, html;
            // ReferenceWidget cannot be simply copied, the combogrid dropdown widgets
            // don't cooperate and the multiValued div must be copied.
            if ($(td1).find('.ArchetypesReferenceWidget').length > 0) {
                var val1 = $(td1).find('input[type="text"]').val();
                var uid1 = $(td1).find('input[type="text"]').attr("uid");
                var multi_div = $("#" + fieldname + "-0-listing");
                for (var arnum = 1; arnum < nr_ars; arnum++) {
                    td = $(tr).find('td[arnum="' + arnum + '"]')[0];
                    e = $(td).find('input[type="text"]');
                    // First we copy the attributes of the text input:
                    $(e).val(val1);
                    $(e).attr('uid', uid1);
                    // then the hidden *_uid shadow field
                    $(td).find('input[id$="_uid"]').val(uid1);
                     // then the multiValued div
                    var multi_divX = multi_div.clone(true);
                    $(multi_divX).attr("id", fieldname + "-" + arnum + "-listing");
                    $("#" + fieldname + "-" + arnum + "-listing").replaceWith(multi_divX)
                    $(e).trigger('copy')
                }
            }
            // select element
            else if ($(td1).find('select').length > 0) {
                var val1 = $(td1).find('select').val()
                for (var arnum = 1; arnum < nr_ars; arnum++) {
                    td = $(tr).find('td[arnum="' + arnum + '"]')[0]
                    e = $(td).find('select')[0]
                    $(e).val(val1)
                    $(e).trigger('copy')
                }
            }
            // text input
            else if ($(td1).find('input[type="text"]').length > 0) {
                var val1 = $(td1).find('input').val()
                for (var arnum = 1; arnum < nr_ars; arnum++) {
                    td = $(tr).find('td[arnum="' + arnum + '"]')[0]
                    e = $(td).find('input')[0]
                    $(e).val(val1)
                    $(e).trigger('copy')
                }
            }
            // checkbox input
            else if ($(td1).find('input[type="checkbox"]').length > 0) {
                var val1 = $(td1).find('input[type="checkbox"]').prop('checked')
                for (var arnum = 1; arnum < nr_ars; arnum++) {
                    td = $(tr).find('td[arnum="' + arnum + '"]')[0]
                    e = $(td).find('input[type="checkbox"]')[0]
                    if (val1) {
                        $(e).attr('checked', true)
                    }
                    else {
                        $(e).removeAttr('checked')
                    }
                    $(e).trigger('copy')
                }
            }
        })
    }

    // Specific handlers for fields requiring special actions  /////////////////
    /*
     --- These configure the jquery bindings for different fields ---
     client_selected        -
     contact_selected       -
     spec_selected          -
     samplepoint_selected   -
     sampletype_selected    -
     profile_selected       -
     template_selected      -
     drymatter_selected     -
     --- These are called by the above bindings, or by other javascript ---
     cc_contacts_set            - when contact is selected, apply CC Contacts
     spec_field_entry           - min/max/error field
     specification_refetch      - lookup ajax spec and apply to min/max/error
     specification_apply        - just re-apply the existing spec
     spec_from_sampletype       - sampletype selection may set the current spec
     spec_filter_on_sampletype  - there may be >1 allowed specs for a sampletype.
     samplepoint_set            - filter with sampletype<->samplepoint relation
     sampletype_set             - filter with sampletype<->samplepoint relation
     profile_set                - apply profile
     profile_unset_trigger      - Unset the deleted profile and its analyses
     template_set               - apply template
     template_unset             - empty template field in form and state
     drymatter_set              - select the DryMatterService and set state
     drymatter_unset            - unset state
     */

    function client_selected() {
        /* Client field is visible and a client has been selected
         */
        $('tr[fieldname="Client"] input[type="text"]')
            .live('selected copy', function (event, item) {
                // filter any references that search inside the Client.
                var arnum = get_arnum(this)
                filter_by_client(arnum)
            })
            .each(function (i, e) {
                if ($(e).val()) {
                    // trigger copy on form load
                    $(e).trigger('copy')
                }
            })
    }

    function contact_selected() {
        /* Selected a Contact: retrieve and complete UI for CC Contacts
         */
        $('tr[fieldname="Contact"] input[type="text"]')
            .live('selected copy', function (event, item) {
                var arnum = get_arnum(this)
                cc_contacts_set(arnum)
            })
        // We do not trigger copy event on load for Contact because doing so would
        // clear any default value supplied for the CCContact field.
    }

    function cc_contacts_set(arnum) {
        /* Setting the CC Contacts after a Contact was set
         *
         * Contact.CCContact may contain a list of Contact references.
         * So we need to select them in the form with some fakey html,
         * and set them in the state.
         */
        var td = $("tr[fieldname='Contact'] td[arnum='" + arnum + "']")
        var contact_element = $(td).find("input[type='text']")[0]
        var contact_uid = $(contact_element).attr("uid")
        // clear the CC selector widget and listing DIV
        var cc_div = $("tr[fieldname='CCContact'] td[arnum='" + arnum + "'] .multiValued-listing")
        var cc_uid_element = $("#CCContact-" + arnum + "_uid")
        $(cc_div).empty()
        $(cc_uid_element).empty()
        if (contact_uid) {
            var request_data = {
                catalog_name: "portal_catalog",
                UID: contact_uid
            }
            window.bika.lims.jsonapi_read(request_data, function (data) {
                if (data.objects && data.objects.length > 0) {
                    var ob = data.objects[0]
                    var cc_titles = ob['CCContact']
                    var cc_uids = ob['CCContact_uid']
                    if (!cc_uids) {
                        return
                    }
                    $(cc_uid_element).val(cc_uids.join(","))
                    for (var i = 0; i < cc_uids.length; i++) {
                        var title = cc_titles[i]
                        var uid = cc_uids[i]
                        var del_btn_src = window.portal_url + "/++resource++bika.lims.images/delete.png"
                        var del_btn = "<img class='deletebtn' data-contact-title='" + title + "' src='" + del_btn_src + "' fieldname='CCContact' uid='" + uid + "'/>"
                        var new_item = "<div class='reference_multi_item' uid='" + uid + "'>" + del_btn + title + "</div>"
                        $(cc_div).append($(new_item))
                    }
                    state_set(arnum, 'CCContact', cc_uids.join(","))
                }
            })
        }
    }

    function cc_contacts_deletebtn_click() {
        $("tr[fieldname='CCContact'] .reference_multi_item .deletebtn").unbind()
        $("tr[fieldname='CCContact'] .reference_multi_item .deletebtn").live('click', function () {
            var arnum = get_arnum(this)
            var fieldname = $(this).attr('fieldname');
            var uid = $(this).attr('uid');
            var existing_uids = $('td[arnum="' + arnum + '"] input[name$="_uid"]').val().split(',');
            destroy(existing_uids, uid);
            $('td[arnum="' + arnum + '"] input[name$="_uid"]').val(existing_uids.join(','));
            $('td[arnum="' + arnum + '"] input[type="text"]').attr('uid', existing_uids.join(','));
            $(this).parent('div').remove();
        });
    }

    function spec_selected() {
        /* Configure handler for the selection of a Specification
         *
         */
        $("[id*='_Specification']")
            .live('selected copy',
            function (event, item) {
                var arnum = $(this).parents('td').attr('arnum')
                specification_refetch(arnum)
            })
            .each(function (i, e) {
                if ($(e).val()) {
                    // trigger copy on form load
                    $(e).trigger('copy')
                }
            })
    }

    function spec_field_entry() {
        /* Validate entry into min/max/error fields, and save them
         * to the state.
         *
         * If min>max or max<min, or error<>0,100, correct the values directly
         * in the field by setting one or the other to a "" value to indicate
         * an error
         */
        $('.min, .max, .error').live('change', function () {
            var td = $(this).parents('td')
            var tr = $(td).parent()
            var arnum = $(td).attr('arnum')
            var uid = $(tr).attr('uid')
            var keyword = $(tr).attr('keyword')
            var min_element = $(td).find(".min")
            var max_element = $(td).find(".max")
            var error_element = $(td).find(".error")
            var min = parseInt(min_element.val(), 10)
            var max = parseInt(max_element.val(), 10)
            var error = parseInt(error_element.val(), 10)

            if ($(this).hasClass("min")) {
                if (isNaN(min)) {
                    $(min_element).val("")
                }
                else if ((!isNaN(max)) && min > max) {
                    $(max_element).val("")
                }
            }
            else if ($(this).hasClass("max")) {
                if (isNaN(max)) {
                    $(max_element).val("")
                }
                else if ((!isNaN(min)) && max < min) {
                    $(min_element).val("")

                }
            }
            else if ($(this).hasClass("error")) {
                if (isNaN(error) || error < 0 || error > 100) {
                    $(error_element).val("")
                }
            }

            var arnum_i = parseInt(arnum, 10)
            var state = bika.lims.ar_add.state[arnum_i]
            var hash = hashes_to_hash(state['ResultsRange'], 'uid')
            hash[uid] = {
                'min': min_element.val(),
                'max': max_element.val(),
                'error': error_element.val(),
                'uid': uid,
                'keyword': keyword
            }
            var hashes = hash_to_hashes(hash)
            state_set(arnum, 'ResultsRange', hashes)
        })
    }

    function specification_refetch(arnum) {
        /* Lookup the selected specification with ajax, then set all
         * min/max/error fields in all columns to match.
         *
         * If the specification does not define values for a particular service,
         * the form values will not be cleared.
         */
        var d = $.Deferred()
        var arnum_i = parseInt(arnum, 10)
        var state = bika.lims.ar_add.state[arnum_i]
        var spec_uid = state['Specification_uid']
        if (!spec_uid) {
            d.resolve()
            return d.promise()
        }
        var request_data = {
            catalog_name: 'bika_setup_catalog',
            UID: spec_uid
        }
        window.bika.lims.jsonapi_read(request_data, function (data) {
            if (data.success && data.objects.length > 0) {
                var rr = data.objects[0]['ResultsRange']
                if (rr && rr.length > 0) {
                    state_set(arnum, 'ResultsRange', rr)
                    specification_apply()
                }
            }
            d.resolve()
        })
        return d.promise()
    }

    function specification_apply() {
        var nr_ars = parseInt($('input[id="ar_count"]').val(), 10)
        for (var arnum = 0; arnum < nr_ars; arnum++) {
            var hashlist = bika.lims.ar_add.state[arnum]['ResultsRange']
            if (hashlist) {
                var spec = hashes_to_hash(hashlist, 'uid')
                $.each($("tr.service_selector td[class*='ar\\." + arnum + "']"),
                    function (i, td) {
                        var uid = $(td).parents("[uid]").attr("uid")
                        if (uid && uid != "new" && uid in spec) {
                            var min = $(td).find(".min")
                            var max = $(td).find(".max")
                            var error = $(td).find(".error")
                            $(min).attr("value", (spec[uid].min))
                            $(max).attr("value", (spec[uid].max))
                            $(error).attr("value", (spec[uid].error))
                        }
                    })
            }
        }
    }

    function set_spec_from_sampletype(arnum) {
        /* Look for Specifications with the selected SampleType.
         *
         * 1) Set the value of the Specification field
         * 2) Fetch the spec from the server, and set all the spec field values
         * 3) Set the partition indicator numbers.
         */
        var st_uid = $("tr[fieldname='SampleType'] " +
            "td[arnum='" + arnum + "'] " +
            "input[type='text']").attr("uid")
        if (!st_uid) {
            return
        }
        spec_filter_on_sampletype(arnum)
        var spec_element = $("tr[fieldname='Specification'] " +
            "td[arnum='" + arnum + "'] " +
            "input[type='text']")
        var spec_uid_element = $("tr[fieldname='Specification'] " +
            "td[arnum='" + arnum + "'] " +
            "input[id$='_uid']")
        var request_data = {
            catalog_name: "bika_setup_catalog",
            portal_type: "AnalysisSpec",
            getSampleTypeUID: st_uid,
            include_fields: ["Title", "UID", "ResultsRange"]
        }
        window.bika.lims.jsonapi_read(request_data, function (data) {
            if (data.objects.length > 0) {
                // If there is one Lab and one Client spec defined, the
                // client spec will be objects[0]
                var spec = data.objects[0]
                // set spec values for this arnum
                $(spec_element).val(spec["Title"])
                $(spec_element).attr("uid", spec["UID"])
                $(spec_uid_element).val(spec['UID'])
                state_set(arnum, 'Specification', spec['UID'])
                // set ResultsRange here!
                var rr = data.objects[0]['ResultsRange']
                if (rr && rr.length > 0) {
                    state_set(arnum, 'ResultsRange', rr)
                    specification_apply()
                }
            }
        })
    }

    function spec_filter_on_sampletype(arnum) {
        /* Possibly filter the Specification dropdown when SampleType selected
         *
         * when a SampleType is selected I will allow only specs to be
         * selected which have a matching SampleType value, or which
         * have no sampletype set.
         */
        var arnum_i = parseInt(arnum, 10)
        var sampletype_uid = bika.lims.ar_add.state[arnum_i]['SampleType']
        var spec_element = $("tr[fieldname='Specification'] td[arnum='" + arnum + "'] input[type='text']")
        var query_str = $(spec_element).attr("search_query")
        var query = $.parseJSON(query_str)
        if (query.hasOwnProperty("getSampleTypeUID")) {
            delete query.getSampleTypeUID
        }
        query.getSampleTypeUID = [encodeURIComponent(sampletype_uid), ""]
        query_str = $.toJSON(query)
        $(spec_element).attr("search_query", query_str)
    }

    function samplepoint_selected() {
        $("tr[fieldname='SamplePoint'] td[arnum] input[type='text']")
            .live('selected copy', function (event, item) {
                var arnum = get_arnum(this)
                samplepoint_set(arnum)
            })
            .each(function (i, e) {
                if ($(e).val()) {
                    // trigger copy on form load
                    $(e).trigger('copy')
                }
            })
    }

    function samplepoint_set(arnum) {
        /***
         * Sample point and Sample type can set each other.
         */
        var spe = $("tr[fieldname='SamplePoint'] td[arnum='" + arnum + "'] input[type='text']")
        var ste = $("tr[fieldname='SampleType'] td[arnum='" + arnum + "'] input[type='text']")
        filter_combogrid(ste, "getSamplePointTitle", $(spe).val(),
            'search_query')
    }

    function sampletype_selected() {
        $("tr[fieldname='SampleType'] td[arnum] input[type='text']")
            .live('selected copy', function (event, item) {
                var arnum = get_arnum(this)
                sampletype_set(arnum)
            })
            .each(function (i, e) {
                if ($(e).val()) {
                    // trigger copy on form load
                    $(e).trigger('copy')
                }
            })
    }

    function sampletype_set(arnum) {
        // setting the Sampletype - Fix the SamplePoint filter:
        // 1. Can select SamplePoint which does not link to any SampleType
        // 2. Can select SamplePoint linked to This SampleType.
        // 3. Cannot select SamplePoint linked to other sample types (and not to this one)
        var spe = $("tr[fieldname='SamplePoint'] td[arnum='" + arnum + "'] input[type='text']")
        var ste = $("tr[fieldname='SampleType'] td[arnum='" + arnum + "'] input[type='text']")
        filter_combogrid(spe, "getSampleTypeTitle", $(ste).val(),
            'search_query')
        set_spec_from_sampletype(arnum)
        partition_indicators_set(arnum)
    }

    function profile_selected() {
        /* A profile is selected.
         * - Set the profile's analyses (existing analyses will be cleared)
         * - Set the partition number indicators
         */
        $("tr[fieldname='Profiles'] td[arnum] input[type='text']")
            .live('selected', function (event, item) {
                var arnum = $(this).parents('td').attr('arnum');
                // We'll use this array to get the new added profile
                var uids_array = $("#Profiles-" + arnum).attr('uid').split(',');
                template_unset(arnum);
                profile_set(arnum, uids_array[uids_array.length - 1])
                    .then(function () {
                        specification_apply();
                        partition_indicators_set(arnum)
                    })
            })
            // On copy we have to set all profiles
            .live('copy', function (event, item) {
                var arnum = $(this).parents('td').attr('arnum');
                // We'll use this array to get the ALL profiles
                var uids_array = $("#Profiles-" + arnum).attr('uid').split(',');
                template_unset(arnum);
                for (var i = 0; i < uids_array.length; i++) {
                    profile_set(arnum, uids_array[i])
                        .then(function () {
                            specification_apply();
                            partition_indicators_set(arnum)
                        })
                }
                recalc_prices(arnum);
            })
            .each(function (i, e) {
                if ($(e).val()) {
                    // trigger copy on form load
                    $(e).trigger('copy')
                }
            })
    }

    function profile_set(arnum, profile_uid) {
        /* Set the profile analyses for the AR in this column
         *  also clear the AR Template field.
         */
        var d = $.Deferred();
        var request_data = {
            catalog_name: "bika_setup_catalog",
            portal_type: "AnalysisProfile",
            UID: profile_uid
        };
        bika.lims.jsonapi_read(request_data, function (data) {
            var profile_objects = data['objects'][0];
            // Set the services from the template into the form
            var profile = $("div.reference_multi_item[uid='" + profile_objects.UID + "']");
            var defs = [];
            var service_data = profile_objects['service_data'];
            var arprofile_services_uid = [];
            profile.attr("price", profile_objects['AnalysisProfilePrice']);
            profile.attr("useprice", profile_objects['UseAnalysisProfilePrice']);
            profile.attr("VATAmount", profile_objects['VATAmount']);
            // I'm not sure about unset dry matter, but it was done in 318
            drymatter_unset(arnum);
            // Adding the services uids inside the analysis profile div, so we can get its analyses quickly
            if (service_data.length != 0) {
                for (var i = 0; i < service_data.length; i++) {
                    arprofile_services_uid.push(service_data[i].UID);
                }
            }
            profile.attr('services', arprofile_services_uid);
            // Setting the services checkboxes
            if ($('#singleservice').length > 0) {
                defs.push(expand_services_singleservice(arnum, service_data))
            }
            else {
                defs.push(expand_services_bika_listing(arnum, service_data))
            }
            // Call $.when with all deferreds
            $.when.apply(null, defs).then(function () {
                d.resolve()
            })
        });
        return d.promise()
    }

    function profiles_unset_all(arnum) {
        /**
         * This function remove all the selected analysis profiles
         */
        if ($("#Profiles-" + arnum).attr('uid') !== "") {
            $("#Profiles-" + arnum).attr("price", "");
            $("#Profiles-" + arnum).attr("services", $.toJSON([]));
            $("#Profiles-" + arnum + "_uid").val("");
            // Getting all ar-arnum-Profiles-listing divisions to obtain their analysis services and uncheck them
            var profiles = $("div#Profiles-" + arnum + "-listing").children();
            var i;
            for (i = profiles.length - 1; i >= 0; i--) {
                unset_profile_analysis_services(profiles[i], arnum)
            }
            // Removing all Profiles-arnum-listing divisions
            profiles.children().remove();
            recalc_prices(arnum);
        }
    }

    function profile_unset_trigger() {
        /***
         After deleting an analysis profile we have to uncheck their associated analysis services, so we need to bind
         the analyses service unseting function. Ever since this binding should be done on the delete image and
         (that is inserted dynamically), we need to settle the the event on the first ancestor element which doesn't
         load dynamically
         */
        $("div[id^='archetypes-fieldname-Profiles-']")
            .on('click', "div.reference_multi_item .deletebtn", function () {
                var profile_object = $(this).parent();
                var arnum = get_arnum(profile_object);
                unset_profile_analysis_services(profile_object, arnum);
                recalc_prices(arnum);
            });
    }

    function unset_profile_analysis_services(profile, arnum) {
        /**
         * The function unsets the selected analyses services related with the removed analysis profile.
         * :profile: the profile DOM division
         * :arnum: the number of the column
         **/
        var service_uids = $(profile).attr('services').split(',');
        var i;
        for (i = service_uids.length -1; i >=0; i--) {
            analysis_cb_uncheck(arnum, service_uids[i]);
        }
    }

    function composite_selected(arnum) {
        $("input#Composite-" + arnum)
          .live('change', function (event, item) {
                template_unset(arnum);
                // Removing composite bindings
                $("input#Composite-" + arnum).unbind()
                })
    }

    function template_selected() {
        $("tr[fieldname='Template'] td[arnum] input[type='text']")
          .live('selected copy', function (event, item) {
                    var arnum = $(this).parents('td').attr('arnum')
                    template_set(arnum)
                })
          .each(function (i, e) {
                    if ($(e).val()) {
                        // trigger copy on form load
                        $(e).trigger('copy')
                    }
                })
    }

    function template_set(arnum) {
        var d = $.Deferred();
        uncheck_all_services(arnum);
        var td = $("tr[fieldname='Template'] " +
                   "td[arnum='" + arnum + "'] ");
        var title = $(td).find("input[type='text']").val();
        var request_data = {
            catalog_name: "bika_setup_catalog",
            title: title,
            include_fields: [
                "SampleType",
                "SampleTypeUID",
                "SamplePoint",
                "SamplePointUID",
                "ReportDryMatter",
                "Composite",
                "AnalysisProfile",
                "Partitions",
                "Analyses",
                "Prices"]
        };
        window.bika.lims.jsonapi_read(request_data, function (data) {

            if (data.success && data.objects.length > 0){
                var template = data.objects[0]
                var td

                // set SampleType
                td = $("tr[fieldname='SampleType'] td[arnum='" + arnum + "']")
                $(td).find("input[type='text']")
                  .val(template['SampleType'])
                  .attr("uid", template['SampleTypeUID'])
                $(td).find("input[id$='_uid']")
                  .val(template['SampleTypeUID'])
                state_set(arnum, 'SampleType', template['SampleTypeUID'])

                // set Specification from selected SampleType
                set_spec_from_sampletype(arnum)

                // set SamplePoint
                td = $("tr[fieldname='SamplePoint'] td[arnum='" + arnum + "']")
                $(td).find("input[type='text']")
                  .val(template['SamplePoint'])
                  .attr("uid", template['SamplePointUID'])
                $(td).find("input[id$='_uid']")
                  .val(template['SamplePointUID'])
                state_set(arnum, 'SamplePoint', template['SamplePointUID'])

                // Set the ARTemplate's AnalysisProfile
                td = $("tr[fieldname='Profile'] td[arnum='" + arnum + "']")
                if (template['AnalysisProfile']) {
                    $(td).find("input[type='text']")
                      .val(template['AnalysisProfile'])
                      .attr("uid", template['AnalysisProfileUID'])
                    $(td).find("input[id$='_uid']")
                      .val(template['AnalysisProfileUID'])
                    state_set(arnum, 'Profile', template['AnalysisProfileUID'])
                }
                else {
                    profiles_unset_all(arnum)
                }

                // Set the services from the template into the form
                var defs = []
                if ($('#singleservice').length > 0) {
                    defs.push(expand_services_singleservice(arnum, template['service_data']))
                }
                else {
                    defs.push(expand_services_bika_listing(arnum, template['service_data']))
                }
                // Set the composite checkbox if needed
                td = $("tr[fieldname='Composite'] td[arnum='" + arnum + "']");
                if (template['Composite']) {
                    $(td).find("input[type='checkbox']").attr("checked", true);
                    state_set(arnum, 'Composite', template['Composite']);
                    composite_selected(arnum)
                }
                else{
                    $(td).find("input[type='checkbox']").attr("checked", false);
                }
                // Call $.when with all deferreds
                $.when.apply(null, defs).then(function () {
                    // Dry Matter checkbox.  drymatter_set will calculate it's
                    // dependencies and select them, and apply specs
                    td = $("tr[fieldname='ReportDryMatter'] td[arnum='" + arnum + "']")
                    if (template['ReportDryMatter']) {
                        $(td).find("input[type='checkbox']").attr("checked", true)
                        drymatter_set(arnum, true)
                    }
                    // Now apply the Template's partition information to the form.
                    // If the template doesn't specify partition information,
                    // calculate it like normal.
                    if (template['Partitions']) {
                        // Stick the current template's partition setup into the state
                        // though it were sent there by a the deps calculating ajax
                        state_set(arnum, 'Partitions', template['Partitions'])
                    }
                    else {
                        // ajax request to calculate the partitions from the form
                        partnrs_calc(arnum)
                    }
                    _partition_indicators_set(arnum)
                    d.resolve()
                })
            }
        });
        return d.promise()
    }

    function template_unset(arnum) {
        var td = $("tr[fieldname='Template'] td[arnum='" + arnum + "']")
        $(td).find("input[type='text']").val("").attr("uid", "")
        $(td).find("input[id$='_uid']").val("")
    }

    function drymatter_selected() {
        $("tr[fieldname='ReportDryMatter'] td[arnum] input[type='checkbox']")
          .live('click copy', function (event) {
                    var arnum = get_arnum(this)
                    if ($(this).prop("checked")) {
                        drymatter_set(arnum)
                        partition_indicators_set(arnum)
                    }
                    else {
                        drymatter_unset(arnum)
                    }
                })
          .each(function (i, e) {
                    // trigger copy on form load
                    $(e).trigger('copy')
                })
    }

    function drymatter_set(arnum) {
        /* set the Dry Matter service, dependencies, etc

         skip_indicators should be true if you want to prevent partition
         indicators from being set.  This is useful if drymatter is being
         checked during the application of a Template to this column.
         */
        var dm_service = $("#getDryMatterService");
        var uid = $(dm_service).val();
        var cat = $(dm_service).attr("cat");
        var poc = $(dm_service).attr("poc");
        var keyword = $(dm_service).attr("keyword");
        var title = $(dm_service).attr("title");
        var price = $(dm_service).attr("price");
        var vatamount = $(dm_service).attr("vatamount");
        var element = $("tr[fieldname='ReportDryMatter'] " +
                        "td[arnum='" + arnum + "'] " +
                        "input[type='checkbox']");
        // set drymatter service IF checkbox is checked
        if ($(element).attr("checked")) {
            var checkbox = $("tr[uid='" + uid + "'] " +
                             "td[class*='ar\\." + arnum + "'] " +
                             "input[type='checkbox']");
            // singleservice selection gets some added attributes.
            // singleservice_duplicate will apply these to the TR it creates
            if ($("#singleservice").length > 0) {
                if ($(checkbox).length > 0) {
                    $("#ReportDryMatter-" + arnum).prop("checked", true);
                }
                else {
                    $("#singleservice").attr("uid", uid);
                    $("#singleservice").attr("keyword", keyword);
                    $("#singleservice").attr("title", title);
                    $("#singleservice").attr("price", price);
                    $("#singleservice").attr("vatamount", vatamount);
                    singleservice_duplicate(uid, title, keyword, price,
                                            vatamount);
                    $("#ReportDryMatter-" + arnum).prop("checked", true);
                }
                state_analyses_push(arnum, uid)
            }
            // in case of bika_listing service selector, some attributes
            // must be applied manually to each TR.  bika_listing already
            // hacks in a lot of what we need (keyword, uid etc).
            else {
                $("#ReportDryMatter-" + arnum).prop("checked", true);
                state_analyses_push(arnum, uid);
            }
            deps_calc(arnum, [uid], true, _("Dry Matter"));
            recalc_prices(arnum);
            state_set(arnum, 'ReportDryMatter', true);
            specification_apply()
        }
    }

    function drymatter_unset(arnum) {
        // if disabling, then we must still update the state var
        state_set(arnum, 'ReportDryMatter', false)
    }

    function sample_selected() {
        $("tr[fieldname='Sample'] td[arnum] input[type='text']")
          .live('selected copy', function (event, item) {
                    var arnum = get_arnum(this)
                    sample_set(arnum)
                })
          .each(function (i, e) {
                    if ($(e).val()) {
                        // trigger copy on form load
                        $(e).trigger('copy')
                    }
                })
        $("tr[fieldname='Sample'] td[arnum] input[type='text']")
          .live('blur', function (event, item) {
                    // This is weird, because the combogrid causes 'blur' when an item
                    // is selected, also - but no harm done.
                    var arnum = get_arnum(this)
                    if (!$(this).val()) {
                        $('td[arnum="' + arnum + '"]').find(":disabled").prop('disabled', false)
                    }
                })
    }

    function sample_set(arnum) {
        // Selected a sample to create a secondary AR.
        $.getJSON(window.location.href.split('/ar_add')[0] + '/secondary_ar_sample_info',
                  {
                      'Sample_uid': $('#Sample-' + arnum).attr('uid'),
                      '_authenticator': $('input[name="_authenticator"]').val()
                  },
                  function (data) {
                      for (var i = 0; i < data.length; i++) {
                          var fieldname = data[i][0];
                          var fieldvalue = data[i][1];
                          if (fieldname.search('_uid') > -1) {
                              // If this fieldname ends with _uid, then we consider it a reference,
                              // and set the HTML elements accordingly
                              fieldname = fieldname.split('_uid')[0];
                              var element = $('#' + fieldname + '-' + arnum)[0]
                              $(element).attr('uid', fieldvalue)
                              $(element).val(fieldvalue)
                          }
                          // This
                          else {
                              var element = $('#' + fieldname + '-' + arnum)[0]
                              // In cases where the schema has been made weird, this JS
                              // must protect itself against non-existing form elements
                              if (!element) {
                                  console.log('Selector #' + fieldname + '-' + arnum + ' not present in form')
                                  continue
                              }
                              // here we go
                              switch (element.type) {
                                  case 'text':
                                  case 'select-one':
                                      $(element).val(fieldvalue)
                                      if (fieldvalue) {
                                          $(element).trigger('copy')
                                      }
                                      $(element).prop('disabled', true)
                                      break
                                  case 'checkbox':
                                      if (fieldvalue) {
                                          $(element).attr('checked', true)
                                          $(element).trigger('copy')
                                      }
                                      else {
                                          $(element).removeAttr('checked')
                                      }
                                      $(element).prop('disabled', true)
                                      break
                                  default:
                                      console.log('Unhandled field type for field ' + fieldname + ': ' + element.type)
                              }
                              state_set(arnum, fieldname, fieldvalue)
                          }
                      }
                  })
    }


// Functions related to the service_selector forms.  ///////////////////////
    /*
     singleservice_dropdown_init    - configure the combogrid (includes handler)
     singleservice_duplicate        - create new service row
     singleservice_deletebtn_click  - remove a service from the form
     expand_services_singleservice  - add a list of services (single-service)
     expand_services_bika_listing   - add a list of services (bika_listing)
     uncheck_all_services           - unselect all from form and state
     */

    function singleservice_dropdown_init() {
        /*
         * Configure the single-service selector combogrid
         */
        var authenticator = $("[name='_authenticator']").val()
        var url = window.location.href.split("/portal_factory")[0] +
          "/service_selector?_authenticator=" + authenticator
        var options = {
            url: url,
            width: "700px",
            showOn: false,
            searchIcon: true,
            minLength: "2",
            resetButton: false,
            sord: "asc",
            sidx: "Title",
            colModel: [
                {
                    "columnName": "Title",
                    "align": "left",
                    "label": "Title",
                    "width": "50"
                },
                {
                    "columnName": "Identifiers",
                    "align": "left",
                    "label": "Identifiers",
                    "width": "35"
                },
                {
                    "columnName": "Keyword",
                    "align": "left",
                    "label": "Keyword",
                    "width": "15"
                },
                {"columnName": "Price", "hidden": true},
                {"columnName": "VAT", "hidden": true},
                {"columnName": "UID", "hidden": true}
            ],
            select: function (event, ui) {
                // Set some attributes on #singleservice to assist the
                // singleservice_duplicate function in it's work
                $("#singleservice").attr("uid", ui['item']['UID'])
                $("#singleservice").attr("keyword", ui['item']['Keyword'])
                $("#singleservice").attr("title", ui['item']['Title'])
                singleservice_duplicate(ui['item']['UID'],
                                        ui['item']['Title'],
                                        ui['item']['Keyword'],
                                        ui['item']['Price'],
                                        ui['item']['VAT'])
            }
        }
        $("#singleservice").combogrid(options)
    }

    function singleservice_duplicate(new_uid, new_title, new_keyword,
                                     new_price, new_vatamount) {
        /*
         After selecting a service from the #singleservice combogrid,
         this function is reponsible for duplicating the TR.  This is
         factored out so that template, profile etc, can also duplicate
         rows.

         Clobber the old row first, set all it's attributes to look like
         bika_listing version of itself.

         The attributes are a little wonky perhaps.  They should mimic the
         attributes that bika_listing rows get, so that the event handlers
         don't have to care.  In some cases though, we need functions for
         both.

         does not set any checkbox values
         */

        // Grab our operating parameters from wherever
        var uid = new_uid || $("#singleservice").attr("uid")
        var keyword = new_keyword || $("#singleservice").attr("keyword")
        var title = new_title || $("#singleservice").attr("title")
        var price = new_price || $("#singleservice").attr("price")
        var vatamount = new_vatamount || $("#singleservice").attr("vatamount")

        // If this service already exists, abort
        var existing = $("tr[uid='" + uid + "']")
        if (existing.length > 0) {
            return
        }

        // clone tr before anything else
        var tr = $("#singleservice").parents("tr")
        var new_tr = $(tr).clone()

        // store row attributes on TR
        $(tr).attr("uid", uid)
        $(tr).attr("keyword", keyword)
        $(tr).attr("title", title)
        $(tr).attr("price", price)
        $(tr).attr("vatamount", vatamount)

        // select_all
        $(tr).find("input[name='uids:list']").attr('value', uid)
        // alert containers
        $(tr).find('.alert').attr('uid', uid)
        // Replace the text widget with a label, delete btn etc:
        var service_label = $(
          "<a href='#' class='deletebtn'><img src='" + portal_url +
          "/++resource++bika.lims.images/delete.png' uid='" + uid +
          "' style='vertical-align: -3px;'/></a>&nbsp;" +
          "<span>" + title + "</span>")
        $(tr).find("#singleservice").replaceWith(service_label)

        // Set spec values manually for the row xyz
        // Configure and insert new row
        $(new_tr).find("[type='checkbox']").removeAttr("checked")
        $(new_tr).find("[type='text']").val("")
        $(new_tr).find("#singleservice").attr("uid", "new")
        $(new_tr).find("#singleservice").attr("keyword", "")
        $(new_tr).find("#singleservice").attr("title", "")
        $(new_tr).find("#singleservice").attr("price", "")
        $(new_tr).find("#singleservice").attr("vatamount", "")
        $(new_tr).find("#singleservice").removeClass("has_combogrid_widget")
        $(tr).after(new_tr)
        specification_apply()
        singleservice_dropdown_init()
    }

    function singleservice_deletebtn_click() {
        /* Remove the service row.
         */
        $(".service_selector a.deletebtn").live('click', function (event) {
            event.preventDefault()
            var tr = $(this).parents("tr[uid]")
            var checkboxes = $(tr).find("input[type='checkbox']").not("[name='uids:list']")
            for (var i = 0; i < checkboxes.length; i++) {
                var element = checkboxes[i]
                var arnum = get_arnum(element)
                var uid = $(element).parents('[uid]').attr("uid")
                state_analyses_remove(arnum, uid)
            }
            $(tr).remove()
        })
    }

    function expand_services_singleservice(arnum, service_data) {
        /*
         When the single-service serviceselector is in place,
         this function is called to select services for setting a bunch
         of services in one AR, eg Profiles and Templates.

         service_data is included from the JSONReadExtender of Profiles and
         Templates.
         */
        // First Select services which are already present
        var uid, keyword, title, price, vatamount
        var not_present = []
        var sd = service_data
        for (var i = 0; i < sd.length; i++) {
            uid = sd[i]["UID"]
            keyword = sd[i]["Keyword"]
            price = sd[i]["Price"]
            vatamount = sd[i]["VAT"]
            var e = $("tr[uid='" + uid + "'] td[class*='ar\\." + arnum + "'] " +
                      "input[type='checkbox']")
            e.length > 0
              ? analysis_cb_check(arnum, sd[i]["UID"])
              : not_present.push(sd[i])
        }
        // Insert services which are not yet present
        for (var i = 0; i < not_present.length; i++) {
            title = not_present[i]["Title"]
            uid = not_present[i]["UID"]
            keyword = not_present[i]["Keyword"]
            price = not_present[i]["Price"]
            vatamount = not_present[i]["VAT"]
            $("#singleservice").val(title)
            $("#singleservice").attr("uid", uid)
            $("#singleservice").attr("keyword", keyword)
            $("#singleservice").attr("title", title)
            $("#singleservice").attr("price", price)
            $("#singleservice").attr("vatamount", vatamount)
            singleservice_duplicate(uid, title, keyword, price, vatamount)
            analysis_cb_check(arnum, uid)
        }
        recalc_prices(arnum)
    }

    function expand_services_bika_listing(arnum, service_data) {
        // When the bika_listing serviceselector is in place,
        // this function is called to select services for Profiles and Templates.
        var d = $.Deferred()
        var services = []
        var defs = []
        var expanded_categories = []
        for (var si = 0; si < service_data.length; si++) {
            // Expand category
            var service = service_data[si]
            services.push(service)
            var th = $("table[form_id='" + service['PointOfCapture'] + "'] " +
                       "th[cat='" + service['CategoryTitle'] + "']")
            if(expanded_categories.indexOf(th) < 0) {
                expanded_categories.push(th)
                var def = $.Deferred()
                def = category_header_expand_handler(th)
                defs.push(def)
            }
        }
        // Call $.when with all deferreds
        $.when.apply(null, defs).then(function () {
            // select services
            for (var si = 0; si < services.length; si++) {
                analysis_cb_check(arnum, services[si]['UID'])
            }
            recalc_prices(arnum)
            d.resolve()
        })
        return d.promise()
    }

    function uncheck_all_services(arnum) {
        // Can't have dry matter without any services
        drymatter_unset(arnum)
        // Remove checkboxes for all existing services in this column
        var cblist = $("tr[uid] td[class*='ar\\." + arnum + "'] " +
                       "input[type='checkbox']").filter(":checked")
        for (var i = 0; i < cblist.length; i++) {
            var e = cblist[i]
            var arnum = get_arnum(e)
            var uid = $(e).parents("[uid]").attr("uid")
            analysis_cb_uncheck(arnum, uid)
        }
    }

    function category_header_clicked() {
        // expand/collapse categorised rows
        var ajax_categories = $("input[name='ajax_categories']")
        $(".bika-listing-table th.collapsed")
          .unbind()
          .live("click", function (event) {
                    category_header_expand_handler(this)
                })
        $(".bika-listing-table th.expanded")
          .unbind()
          .live("click", function () {
            // After ajax_category expansion, collapse and expand work as they would normally.
            $(this).parent().nextAll("tr[cat='" + $(this).attr("cat") + "']").toggle(false)
            // Set collapsed class on TR
            $(this).removeClass("expanded").addClass("collapsed")
        })
    }

    function category_header_expand_handler(element) {
        /* Deferred function to expand the category with ajax (or not!!)
         on first expansion.  duplicated from bika.lims.bikalisting.js, this code
         fires when categories are expanded automatically (eg, when profiles or templates require
         that the category contents are visible for selection)

         Also, this code returns deferred objects, not their promises.

         :param: element - The category header TH element which normally receives 'click' event
         */
        var def = $.Deferred()
        // with form_id allow multiple ajax-categorised tables in a page
        var form_id = $(element).parents("[form_id]").attr("form_id")
        var cat_title = $(element).attr('cat')
        var ar_count = parseInt($("#ar_count").val(), 10)
        // URL can be provided by bika_listing classes, with ajax_category_url attribute.
        var url = $("input[name='ajax_categories_url']").length > 0
          ? $("input[name='ajax_categories_url']").val()
          : window.location.href.split('?')[0]
        // We will replace this element with downloaded items:
        var placeholder = $("tr[data-ajax_category='" + cat_title + "']")

        // If it's already been expanded, ignore
        if ($(element).hasClass("expanded")) {
            def.resolve()
            return def
        }

        // If ajax_categories are enabled, we need to go request items now.
        var ajax_categories_enabled = $("input[name='ajax_categories']")
        if (ajax_categories_enabled.length > 0 && placeholder.length > 0) {
            var options = {}
            // this parameter allows the receiving view to know for sure what's expected
            options['ajax_category_expand'] = 1
            options['cat'] = cat_title
            options['ar_count'] = ar_count
            options['form_id'] = form_id
            if ($('.review_state_selector a.selected').length > 0) {
                // review_state must be kept the same after items are loaded
                // (TODO does this work?)
                options['review_state'] = $('.review_state_selector a.selected')[0].id
            }
            $.ajax({url: url, data: options})
              .done(function (data) {
                    // LIMS-1970 Analyses from AR Add form not displayed properly
                    var rows = $("<table>"+data+"</table>").find("tr");
                    $("[form_id='" + form_id + "'] tr[data-ajax_category='" + cat_title + "']").replaceWith(rows);
                    $(element).removeClass("collapsed").addClass("expanded");
                    def.resolve();
                })
        }
        else {
            // When ajax_categories are disabled, all cat items exist as TR elements:
            $(element).parent().nextAll("tr[cat='" + cat_title + "']").toggle(true)
            $(element).removeClass("collapsed").addClass("expanded")
            def.resolve()
        }
        return def
    }

// analysis service checkboxes /////////////////////////////////////////////
    /* - analysis_cb_click   user interaction with form (select, unselect)
     * - analysis_cb_check   performs the same action, but from code (no .click)
     * - analysis_cb_uncheck does the reverse
     * - analysis_cb_after_change  always runs when service checkbox changes.
     * - state_analyses_push        add selected service to state
     * - state_analyses_remove      remove service uid from state
     */

    function analysis_cb_click() {
        /* configures handler for click event on analysis checkboxes
         * and their associated select-all checkboxes.
         *
         * As far as possible, the bika_listing and single-select selectors
         * try to emulate each other's HTML structure in each row.
         *
         */
        // regular analysis cb
        $(".service_selector input[type='checkbox'][name!='uids:list']")
          .live('click', function () {
                    var arnum = get_arnum(this)
                    var uid = $(this).parents("[uid]").attr("uid")
                    analysis_cb_after_change(arnum, uid)
                    // Now we will manually decide if we should add or
                    // remove the service UID from state['Analyses'].
                    if ($(this).prop("checked")) {
                        state_analyses_push(arnum, uid)
                    }
                    else {
                        state_analyses_remove(arnum, uid)
                    }
                    // If the click is on "new" row, focus the selector
                    if (uid == "new") {
                        $("#singleservice").focus()
                    }
                    var title = $(this).parents("[title]").attr("title")
                    deps_calc(arnum, [uid], false, title)
                    partition_indicators_set(arnum)
                    recalc_prices(arnum)
                })
        // select-all cb
        $(".service_selector input[type='checkbox'][name='uids:list']")
          .live('click', function () {
                    var nr_ars = parseInt($('#ar_count').val(), 10)
                    var tr = $(this).parents("tr")
                    var uid = $(this).parents("[uid]").attr("uid")
                    var checked = $(this).prop("checked")
                    var checkboxes = $(tr).find("input[type=checkbox][name!='uids:list']")
                    for (var i = 0; i < checkboxes.length; i++) {
                        if (checked) {
                            analysis_cb_check(i, uid)
                        }
                        else {
                            analysis_cb_uncheck(i, uid)
                        }
                        recalc_prices(i)
                    }
                    var title = $(this).parents("[title]").attr("title")
                    for (i = 0; i < nr_ars; i++) {
                        deps_calc(i, [uid], true, title)
                        partition_indicators_set(i)
                    }
                    // If the click is on "new" row, focus the selector
                    if (uid == "new") {
                        $("#singleservice").focus()
                    }
                })
    }

    function analysis_cb_check(arnum, uid) {
        /* Called to un-check an Analysis' checkbox as though it were clicked.
         */
        var cb = $("tr[uid='" + uid + "'] " +
                   "td[class*='ar\\." + arnum + "'] " +
                   "input[type='checkbox']")
        $(cb).attr("checked", true)
        analysis_cb_after_change(arnum, uid)
        state_analyses_push(arnum, uid)
        specification_apply()
    }

    function analysis_cb_uncheck(arnum, uid) {
        /* Called to un-check an Analysis' checkbox as though it were clicked.
         */
        var cb = $("tr[uid='" + uid + "'] " +
                   "td[class*='ar\\." + arnum + "'] " +
                   "input[type='checkbox']")
        $(cb).removeAttr("checked")
        analysis_cb_after_change(arnum, uid)
        state_analyses_remove(arnum, uid)
    }

    function analysis_cb_after_change(arnum, uid) {
        /* If changed by click or by other trigger, all analysis checkboxes
         * must invoke this function.
         */
        var cb = $("tr[uid='" + uid + "'] " +
                   "td[class*='ar\\." + arnum + "'] " +
                   "input[type='checkbox']")
        var tr = $(cb).parents("tr")
        var checked = $(cb).prop("checked")
        var checkboxes = $(tr).find("input[type=checkbox][name!='uids:list']")
        // sync the select-all checkbox state
        var nr_checked = $(checkboxes).filter(":checked")
        if (nr_checked.length == checkboxes.length) {
            $(tr).find("[name='uids:list']").attr("checked", true)
        }
        else {
            $(tr).find("[name='uids:list']").removeAttr("checked")
        }
        // Unselecting Dry Matter Service unsets 'Report Dry Matter'
        if (uid == $("#getDryMatterService").val() && !checked) {
            var dme = $("#ReportDryMatter-" + arnum);
            $(dme).removeAttr("checked")
        }
    }

    function state_analyses_push(arnum, uid) {
        arnum = parseInt(arnum, 10)
        var analyses = bika.lims.ar_add.state[arnum]['Analyses']
        if (analyses.indexOf(uid) == -1) {
            analyses.push(uid)
            state_set(arnum, 'Analyses', analyses)
        }
    }

    function state_analyses_remove(arnum, uid) {
        // This function removes the analysis services checkbox's uid from the astate's analysis list.
        arnum = parseInt(arnum, 10);
        var analyses = bika.lims.ar_add.state[arnum]['Analyses'];
        if (analyses.indexOf(uid) > -1) {
            analyses.splice(analyses.indexOf(uid), 1);
            state_set(arnum, 'Analyses', analyses);
            // Ever since this is the last function invoked on the analysis services uncheck process, we'll
            // remove the analysis profile related with the unset services here.
                        // Unselecting the related analysis profiles
            var profiles = $("div#Profiles-" + arnum + "-listing").children();
            $.each(profiles, function(i, profile) {
                // If the profile has the attribute services
                if (typeof $(profile).attr('services') !== typeof undefined && $(profile).attr('services') !== false) {
                    var service_uids = $(profile).attr('services').split(',');
                    if ($.inArray(uid, service_uids) != -1) {
                        var profile_uid = $(profile).attr('uid');
                        $(profile).remove();
                        // Removing the profile's uid from the profiles widget
                        var p = $("#Profiles-" + arnum).attr('uid').split(',');
                        p = $.grep(p, function(value) {
                            return value != profile_uid;
                        });
                        var i;
                        var p_str = '';
                        for (i = p.length - 1; i >= 0; i--) { p_str = p_str + ',' + p[i]}
                        $("#Profiles-" + arnum).attr('uid', p_str);
                        $("#Profiles-" + arnum).attr('uid_check', p_str);
                        $("#Profiles-" + arnum + "_uid").val(p_str);
                    }
                }
            });
            recalc_prices(arnum);
        }
    }

// dependencies ////////////////////////////////////////////////////////////
    /*
     deps_calc                  - the main routine for dependencies/dependants
     dependencies_add_confirm   - adding dependancies to the form/state: confirm
     dependancies_add_yes       - clicked yes
     dependencies_add_no        - clicked no
     */

    function deps_calc(arnum, uids, skip_confirmation, initiator) {
        /* Calculate dependants and dependencies.
         *
         * arnum - the column number.
         * uids - zero or more service UIDs to calculate
         * skip_confirmation - assume yes instead of confirmation dialog
         * initiator - the service or control that initiated this check.
         *             used for a more pretty dialog box header.
         */
        jarn.i18n.loadCatalog('bika')
        var _ = window.jarn.i18n.MessageFactory("bika")

        var Dep
        var i, cb, dep_element
        var lims = window.bika.lims
        var dep_services = []  // actionable services
        var dep_titles = []    // pretty titles

        for (var n = 0; n < uids.length; n++) {
            var uid = uids[n]
            if (uid == "new") {
                continue
            }
            var element = $("tr[uid='" + uids[n] + "'] " +
                            "td[class*='ar\\." + arnum + "'] " +
                            "input[type='checkbox']")
            var initiator = $(element).parents("[title]").attr("title")

            // selecting a service; discover dependencies
            if ($(element).prop("checked")) {
                var Dependencies = lims.AnalysisService.Dependencies(uid)
                for (i = 0; i < Dependencies.length; i++) {
                    var Dep = Dependencies[i]
                    dep_element = $("tr[uid='" + Dep['Service_uid'] + "'] " +
                                    "td[class*='ar\\." + arnum + "'] " +
                                    "input[type='checkbox']")
                    if (!$(dep_element).prop("checked")) {
                        dep_titles.push(Dep['Service'])
                        dep_services.push(Dep)
                    }
                }
                if (dep_services.length > 0) {
                    if (skip_confirmation) {
                        dependancies_add_yes(arnum, dep_services)
                    }
                    else {
                        dependencies_add_confirm(initiator, dep_services,
                                                 dep_titles)
                          .done(function (data) {
                                    dependancies_add_yes(arnum,
                                                         dep_services)
                                })
                          .fail(function (data) {
                                    dependencies_add_no(arnum, uid)
                                })
                    }
                }
            }
            // unselecting a service; discover back dependencies
            // this means, services which employ calculations, which in turn
            // require these other services' results in order to be calculated.
            else {
                var Dependants = lims.AnalysisService.Dependants(uid)
                for (i = 0; i < Dependants.length; i++) {
                    Dep = Dependants[i]
                    dep_element = $("tr[uid='" + Dep['Service_uid'] + "'] " +
                                    "td[class*='ar\\." + arnum + "'] " +
                                    "input[type='checkbox']")
                    if ($(dep_element).prop("checked")) {
                        dep_titles.push(Dep['Service'])
                        dep_services.push(Dep)
                    }
                }
                if (dep_services.length > 0) {
                    if (skip_confirmation) {
                        dependants_remove_yes(arnum, dep_services)
                    }
                    else {
                        dependants_remove_confirm(initiator, dep_services,
                                                  dep_titles)
                          .done(function (data) {
                                    dependants_remove_yes(arnum,
                                                          dep_services)
                                })
                          .fail(function (data) {
                                    dependants_remove_no(arnum, uid)
                                })
                    }
                }
            }

        }
    }

    function dependants_remove_confirm(initiator, dep_services,
                                       dep_titles) {
        var d = $.Deferred()
        $("body").append(
          "<div id='messagebox' style='display:none' title='" + _("Service dependencies") + "'>" +
          _("<p>The following services depend on ${service}, and will be unselected if you continue:</p><br/><p>${deps}</p><br/><p>Do you want to remove these selections now?</p>",
            {
                service: initiator,
                deps: dep_titles.join("<br/>")
            }) + "</div>")
        $("#messagebox")
          .dialog(
          {
              width: 450,
              resizable: false,
              closeOnEscape: false,
              buttons: {
                  yes: function () {
                      d.resolve()
                      $(this).dialog("close");
                      $("#messagebox").remove();
                  },
                  no: function () {
                      d.reject()
                      $(this).dialog("close");
                      $("#messagebox").remove();
                  }
              }
          })
        return d.promise()
    }

    function dependants_remove_yes(arnum, dep_services) {
        for (var i = 0; i < dep_services.length; i += 1) {
            var Dep = dep_services[i]
            var uid = Dep['Service_uid']
            analysis_cb_uncheck(arnum, uid)
        }
        _partition_indicators_set(arnum)
    }

    function dependants_remove_no(arnum, uid) {
        analysis_cb_check(arnum, uid)
        _partition_indicators_set(arnum)
    }

    function dependencies_add_confirm(initiator_title, dep_services,
                                      dep_titles) {
        /*
         uid - this is the analysisservice checkbox which was selected
         dep_services and dep_titles are the calculated dependencies
         initiator_title is the dialog title, this could be a service but also could
         be "Dry Matter" or some other name
         */
        var d = $.Deferred()
        var html = "<div id='messagebox' style='display:none' title='" + _("Service dependencies") + "'>"
        html = html + _("<p>${service} requires the following services to be selected:</p>" +
                        "<br/><p>${deps}</p><br/><p>Do you want to apply these selections now?</p>",
                        {
                            service: initiator_title,
                            deps: dep_titles.join("<br/>")
                        })
        html = html + "</div>"
        $("body").append(html)
        $("#messagebox")
          .dialog(
          {
              width: 450,
              resizable: false,
              closeOnEscape: false,
              buttons: {
                  yes: function () {
                      d.resolve()
                      $(this).dialog("close");
                      $("#messagebox").remove();
                  },
                  no: function () {
                      d.reject()
                      $(this).dialog("close");
                      $("#messagebox").remove();
                  }
              }
          })
        return d.promise()
    }

    function dependancies_add_yes(arnum, dep_services) {
        /*
         Adding required analyses to this AR - Clicked "yes" to confirmation,
         or if confirmation dialog is skipped, this function is called directly.
         */
        for (var i = 0; i < dep_services.length; i++) {
            var Dep = dep_services[i]
            var uid = Dep['Service_uid']
            var dep_cb = $("tr[uid='" + uid + "'] " +
                           "td[class*='ar\\." + arnum + "'] " +
                           "input[type='checkbox']")
            if (dep_cb.length > 0) {
                // row already exists
                if ($(dep_cb).prop("checked")) {
                    // skip if checked already
                    continue
                }
            }
            else {
                // create new row for all services we may need
                singleservice_duplicate(Dep['Service_uid'],
                                        Dep["Service"],
                                        Dep["Keyword"],
                                        Dep["Price"],
                                        Dep["VAT"])
            }
            // finally check the service
            analysis_cb_check(arnum, uid);
        }
        recalc_prices(arnum)
        _partition_indicators_set(arnum)
    }

    function dependencies_add_no(arnum, uid) {
        /*
         Adding required analyses to this AR - clicked "no" to confirmation.
         This is just responsible for un-checking the service that was
         used to invoke this routine.
         */
        var element = $("tr[uid='" + uid + "'] td[class*='ar\\." + arnum + "'] input[type='checkbox']")
        if ($(element).prop("checked")) {
            analysis_cb_uncheck(arnum, uid);
        }
        _partition_indicators_set(arnum)
    }

// form/UI functions: not related to specific fields ///////////////////////
    /* partnrs_calc calls the ajax url, and sets the state variable
     * partition_indicators_set calls partnrs_calc, and modifies the form.
     * partition_indicators_from_template set state partnrs from template
     * _partition_indicators_set actually does the form/ui work
     */

    function partnrs_calc(arnum) {
        /* Configure the state partition data with an ajax call
         * - calls to /calculate_partitions json url
         *
         */
        var d = $.Deferred()
        arnum = parseInt(arnum, 10)

        //// Template columns are not calculated - they are set manually.
        //// I have disabled this behaviour, to simplify the action of adding
        //// a single extra service to a Template column.
        //var te = $("tr[fieldname='Template'] td[arnum='" + arnum + "'] input[type='text']")
        //if (!$(te).val()) {
        //  d.resolve()
        //  return d.promise()
        //}

        var st_uid = bika.lims.ar_add.state[arnum]['SampleType']
        var service_uids = bika.lims.ar_add.state[arnum]['Analyses']

        // if no sampletype or no selected analyses:  remove partition markers
        if (!st_uid || !service_uids) {
            d.resolve()
            return d.promise()
        }
        var request_data = {
            services: service_uids.join(","),
            sampletype: st_uid,
            _authenticator: $("input[name='_authenticator']").val()
        }
        window.jsonapi_cache = window.jsonapi_cache || {}
        var cacheKey = $.param(request_data)
        if (typeof window.jsonapi_cache[cacheKey] === "undefined") {
            $.ajax({
                       type: "POST",
                       dataType: "json",
                       url: window.portal_url + "/@@API/calculate_partitions",
                       data: request_data,
                       success: function (data) {
                           // Check if calculation succeeded
                           if (data.success == false) {
                               bika.lims.log('Error while calculating partitions: ' + data.message)
                           }
                           else {
                               window.jsonapi_cache[cacheKey] = data
                               bika.lims.ar_add.state[arnum]['Partitions'] = data['parts']
                           }
                           d.resolve()
                       }
                   })
        }
        else {
            var data = window.jsonapi_cache[cacheKey]
            bika.lims.ar_add.state[arnum]['Partitions'] = data['parts']
            d.resolve()
        }
        return d.promise()
    }

    function _partition_indicators_set(arnum) {
        // partnrs_calc (or some template!) should have already set the state.

        // Be aware here, that some services may not have part info, eg if a
        // template was applied with only partial info.  This function literally
        // uses "part-1" as a default

        arnum = parseInt(arnum, 10)
        var parts = bika.lims.ar_add.state[arnum]['Partitions']
        if (!parts) {
            return
        }
        // I'll be looping all the checkboxes currently visible in this column
        var checkboxes = $("tr[uid] td[class*='ar\\." + arnum + "'] " +
                           "input[type='checkbox'][name!='uids:list']")
        // the UIDs of services which are not found in any partition should
        // be indicated.  anyway there should be some default applied, or
        // selection allowed.
        for (var n = 0; n < checkboxes.length; n++) {
            var cb = checkboxes[n]
            var span = $(cb).parents("[class*='ar\\.']").find(".partnr")
            var uid = $(cb).parents("[uid]").attr("uid")
            if ($(cb).prop("checked")) {
                // this service is selected - locate a partnr for it
                var partnr = 1
                for (var p = 0; p < parts.length; p++) {
                    if (parts[p]['services'].indexOf(uid) > -1) {
                        if (parts[p]["part_id"]) {
                            partnr = parts[p]["part_id"].split("-")[1]
                        }
                        else {
                            partnr = p + 1
                        }
                        break
                    }
                }
                // print the new partnr into the span
                $(span).html(partnr)
            }
            else {
                // this service is not selected - remove the partnr
                $(span).html("&nbsp;")
            }
        }
    }

    function partition_indicators_set(arnum, skip_calculation) {
        /* Calculate and Set partition indicators
         * set skip_calculation if the state variable already contains
         * calculated partitions (eg, when setting template)
         */
        if (skip_calculation) {
            _partition_indicators_set(arnum)
        }
        else {
            partnrs_calc(arnum).done(function () {
                _partition_indicators_set(arnum)
            })
        }
    }

    function recalc_prices(arnum) {
        var ardiscount_amount = 0.00;
        var arservices_price = 0.00;
        // Getting all checked analysis services
        var checked = $("tr[uid] td[class*='ar\\." + arnum + "'] input[type='checkbox']:checked");
        var member_discount = parseFloat($("#bika_setup").attr("MemberDiscount"));
        var profiles = $("div#Profiles-" + arnum + "-listing").children();
        var arprofiles_price = 0.00;
        var arprofiles_vat_amount = 0.00;
        var arservice_vat_amount = 0.00;
        var services_from_priced_profile = [];

        /* ANALYSIS PROFILES PRICE */
        $.each(profiles, function(i, profile) {
            // Getting available analysis profiles' prices and vat amounts
            if ($(profile).attr('useprice') === 'true') {
                var profile_service_uids = $(profile).attr('services').split(',');
                var profile_price = parseFloat($(profile).attr('price'));
                var profile_vat = parseFloat($(profile).attr('VATAmount'));
                arprofiles_price += profile_price;
                arprofiles_vat_amount += profile_vat;
                // We don't want repeated analysis services because of two profiles with the same analysis, so we'll
                // check if the analysis is contained in the array before adding it
                $.each(profile_service_uids, function (i, el) {
                    if($.inArray(el, services_from_priced_profile) === -1) {
                        services_from_priced_profile.push(el)
                    }
                });
            }
        });
        /* ANALYSIS SERVICES PRICE*/
        // Compute the price for each checked analysis service. We have to look for profiles which have set
        // "use price" attribute and sum the profile's price to the total instead of using their individual
        // services prices
        for (var i = 0; i < checked.length; i++) {
            var cb = checked[i];
            // For some browsers, checkbox `attr` is undefined; for others, its false. Check for both.
            if ($(cb).prop("checked")
                && !$(cb).prop("disabled")
                && typeof $(cb).prop("disabled") !== "undefined"
                && services_from_priced_profile.indexOf($(cb).attr('uid')) < 0)
            {
                var service_price = parseFloat($(cb).parents("[price]").attr("price"));
                var service_vat_amount = parseFloat($(cb).parents("[vat_percentage]").attr("vat_percentage"));
                arservice_vat_amount += service_price * service_vat_amount / 100;
                arservices_price += service_price;
            }
        }
        var base_price = arservices_price + arprofiles_price;
        if (member_discount) {
            ardiscount_amount = base_price * member_discount / 100;
        }
        var subtotal = base_price - ardiscount_amount;
        var vat_amount = arprofiles_vat_amount + arservice_vat_amount;
        var total = subtotal + vat_amount;
        $("td[arnum='" + arnum + "'] span.price.discount").html(ardiscount_amount.toFixed(2));
        $("td[arnum='" + arnum + "'] span.price.subtotal").html(subtotal.toFixed(2));
        $("td[arnum='" + arnum + "'] span.price.vat").html(vat_amount.toFixed(2));
        $("td[arnum='" + arnum + "'] span.price.total").html(total.toFixed(2));
    }

    function set_state_from_form_values() {
        var nr_ars = parseInt($("#ar_count").val(), 10)
        // Values flagged as 'hidden' in the AT schema widget visibility
        // attribute, are flagged so that we know they contain only "default"
        // values, and do not constitute data entry.
        $.each($('td[arnum][hidden] input[type="hidden"]'),
               function (i, e) {
                   var arnum = get_arnum(e)
                   var fieldname = $(e).parents("[fieldname]").attr("fieldname")
                   var value = $(e).attr("uid")
                     ? $(e).attr("uid")
                     : $(e).val()
                   if (fieldname) {
                       state_set(arnum, fieldname, value)
                       // To avoid confusion with other hidden inputs, these have a
                       // 'hidden' attribute on their td.
                       state_set(arnum, fieldname + "_hidden", true)
                   }
               })
        // other field values which are handled similarly:
        $.each($('td[arnum] input[type="text"], td[arnum] input.referencewidget'),
               function (i, e) {
                   var arnum = $(e).parents("[arnum]").attr("arnum")
                   var fieldname = $(e).parents("[fieldname]").attr("fieldname")
                   var value = $(e).attr("uid")
                     ? $(e).attr("uid")
                     : $(e).val()
                   state_set(arnum, fieldname, value)
               })
        // checkboxes inside ar_add_widget table.
        $.each($('[ar_add_ar_widget] input[type="checkbox"]'),
               function (i, e) {
                   var arnum = get_arnum(e)
                   var fieldname = $(e).parents("[fieldname]").attr("fieldname")
                   var value = $(e).prop('checked')
                   state_set(arnum, fieldname, value)
               })
        // select widget values
        $.each($('td[arnum] select'),
               function (i, e) {
                   var arnum = get_arnum(e)
                   var fieldname = $(e).parents("[fieldname]").attr("fieldname")
                   var value = $(e).val()
                   state_set(arnum, fieldname, value)
               })
        // services
        var uid, arnum, services
        for (arnum = 0; arnum < nr_ars; arnum++) {
            services = [] // list of UIDs
            var cblist = $('.service_selector td[class*="ar\\.' + arnum + '"] input[type="checkbox"]').filter(":checked")
            $.each(cblist, function (i, e) {
                uid = $(e).parents("[uid]").attr("uid")
                services.push(uid)
            })
            state_set(arnum, "Analyses", services)
        }
        // ResultsRange + specifications from UI
        var rr, specs, min, max, error
        for (arnum = 0; arnum < nr_ars; arnum++) {
            rr = bika.lims.ar_add.state[arnum]['ResultsRange']
            if (rr != undefined) {
                specs = hashes_to_hash(rr, 'uid')
                $.each($(".service_selector td[class*='ar\\." + arnum + "'] .after"),
                       function (i, e) {
                           uid = $(e).parents("[uid]").attr("uid")
                           var keyword = $(e).parents("[keyword]").attr("keyword")
                           if (uid != "new" && uid != undefined) {
                               min = $(e).find(".min")
                               max = $(e).find(".max")
                               error = $(e).find(".error")
                               if (specs[uid] == undefined) {
                                   specs[uid] = {
                                       'min': $(min).val(),
                                       'max': $(max).val(),
                                       'error': $(error).val(),
                                       'uid': uid,
                                       'keyword': keyword
                                   }
                               }
                               else {
                                   specs[uid].min = $(min)
                                     ? $(min).val()
                                     : specs[uid].min
                                   specs[uid].max = $(max)
                                     ? $(max).val()
                                     : specs[uid].max
                                   specs[uid].error = $(error)
                                     ? $(error).val()
                                     : specs[uid].error
                               }
                           }
                       })
                state_set(arnum, "ResultsRange", hash_to_hashes(specs))
            }
        }
    }

    function form_submit() {
        $("[name='save_button']").click(
          function (event) {
              event.preventDefault()
              set_state_from_form_values()
              var request_data = {
                  _authenticator: $("input[name='_authenticator']").val(),
                  state: $.toJSON(bika.lims.ar_add.state)
              }
              $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    url: window.location.href.split("/portal_factory")[0] + "/analysisrequest_submit",
                    data: request_data,
                    success: function (data) {
                        /*
                         * data contains the following useful keys:
                         * - errors: any errors which prevented the AR from being created
                         *   these are displayed immediately and no further ation is taken
                         * - destination: the URL to which we should redirect on success.
                         *   This includes GET params for printing labels, so that we do not
                         *   have to care about this here.
                         */
                        if (data['errors']) {
                            var msg = ""
                            for (var error in data.errors) {
                                var x = error.split(".")
                                var e
                                if (x.length == 2) {
                                    e = x[1] + ", AR " + (+x[0]) + ": "
                                }
                                else if (x.length == 1) {
                                    e = x[0] + ": "
                                }
                                else {
                                    e = ""
                                }
                                msg = msg + e + data.errors[error] + "<br/>"
                            }
                            window.bika.lims.portalMessage(msg)
                            window.scroll(0, 0)
                        }
                        else if (data['labels']) {
                            var destination = window.location.href.split("/portal_factory")[0]
                            var ars = data['labels']
                            var labelsize = data['labelsize']
                            var q = "/sticker?size=" + labelsize + "&items=" + ars.join(",")
                            window.location.replace(destination + q)
                        }
                        else {
                            var destination = window.location.href.split("/portal_factory")[0]
                            window.location.replace(destination)
                        }
                    }
                })
          })
    }

    function fix_table_layout() {
        "use strict";

        // Apply to header column
        var headcolwidth = $('table.analysisrequest.add tr:first th').width();
        headcolwidth += $('table.analysisrequest.add tr:first td:first').width();
        $('table tr th input[id*="_toggle_cols"]').closest("th").css('width', 24);
        $('table tr th[id="foldercontents-Title-column"]').css('width', headcolwidth);
        $('table tr[id^="folder-contents-item-"] td[class*="Title"]').css('width', headcolwidth);

        // Apply to Analyses columns
        var arcolswidth = $('table.analysisrequest td[arnum]').width();
        $('table tr th[id^="foldercontents-ar."]').css({'width':arcolswidth, 'text-align':'center'});
        $('table tr[id^="folder-contents-item-"] td[class*="ar"]').css({'width':arcolswidth, 'text-align':'center'});
    }
}
