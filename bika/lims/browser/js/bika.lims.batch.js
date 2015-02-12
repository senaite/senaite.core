/**
 * Controller class for Batch Folder View
 */
function BatchFolderView() {

    var that = this;

    that.load = function() {

        /**
         * Modal confirmation when user clicks on 'cancel' active button.
         * Used on batch folder views
         */
        $(".portaltype-batchfolder").append("" +
                "<div id='batch-cancel-dialog' title='"+_("Cancel batch/es?")+"'>" +
                "    <p style='padding:10px'>" +
                "        <span class='ui-icon ui-icon-alert' style=''float: left; margin: 0 7px 30px 0;'><br/></span>" +
                "        "+_("All linked Analysis Requests will be cancelled too.") +
                "    </p>" +
                "    <p style='padding:0px 10px'>" +
                "       "+_("Are you sure?") +
                "    </p>" +
                "</div>" +
                "<input id='batch-cancel-resp' type='hidden' value='false'/>");

        $("#batch-cancel-dialog").dialog({
            autoOpen:false,
            resizable: false,
            height:200,
            width:400,
            modal: true,
            buttons: {
                "Cancel selected batches": function() {
                    $(this).dialog("close");
                    $("#batch-cancel-resp").val('true');
                    $(".portaltype-batchfolder #cancel_transition").click();
                },
                Cancel: function() {
                    $("#batch-cancel-resp").val('false');
                    $(this).dialog("close");
                }
            }
        });

        $("#cancel_transition").click(function(event){
           if ($(".bika-listing-table input[type='checkbox']:checked").length) {
               if ($("#batch-cancel-resp").val() == 'true') {
                   return true;
               } else {
                   event.preventDefault();
                   $("#batch-cancel-dialog").dialog("open");
                   return false;
               }
           } else {
               return false;
           }
        });
    }
}

/**
 * Controller class for Batch View
 */
function BatchView() {

    var that = this;

    that.load = function() {
		function applyComboFilter(element, filterkey, filtervalue) {
			// If the element is not visible it is probably not worth creating a dropdown query.
			if (!$(element).is(':visible')){
				return;
			}
			var base_query=$.parseJSON($(element).attr("base_query"));
			base_query[filterkey] = filtervalue;
			$(element).attr("base_query", $.toJSON(base_query));
			var options = $.parseJSON($(element).attr("combogrid_options"));
			// TODO this code should be using $.query for query string handling
			options.url = portal_url + "/" + options.url;
			options.url = options.url + "?_authenticator=" + $("input[name='_authenticator']").val();
			options.url = options.url + "&catalog_name=" + $(element).attr("catalog_name");
			options.url = options.url + "&base_query=" + $.toJSON(base_query);
			options.url = options.url + "&search_query=" + $(element).attr("search_query");
			options.url = options.url + "&colModel=" + $.toJSON( $.parseJSON($(element).attr("combogrid_options")).colModel);
			options.url = options.url + "&search_fields=" + $.toJSON($.parseJSON($(element).attr("combogrid_options")).search_fields);
			options.url = options.url + "&discard_empty=" + $.toJSON($.parseJSON($(element).attr("combogrid_options")).discard_empty);
			options.force_all="false";
			$(element).combogrid(options);
			$(element).addClass("has_combogrid_widget");
			$(element).attr("search_query", "{}");
		}

		// Clear and re-set the filter when Client is selected
		function client_field_modified(){
			$("#Contact").val('');
			$("#Contact_uid").val('');
			$("#CCContact").val('');
			$("#CCContact_uid").val('');
			$("#CCContact-listing > .reference_multi_item").remove();
			$("#InvoiceContact").val('');
			applyComboFilter($("#Contact"), "getParentUID", $("#Client_uid").val());
			applyComboFilter($("#CCContact"), "getParentUID", $("#Client_uid").val());
			applyComboFilter($("#InvoiceContact"), "getParentUID", $("#Client_uid").val());
		}
		$("#Client").bind("selected", client_field_modified);
		$("#Client").bind("unselected", client_field_modified);
		// We do this once on page-load, also.
		// We need a delay to be sure this code runs after the widget is configured.
		setTimeout(function() {
			applyComboFilter($("#Contact"), "getParentUID", $("#Client_uid").val());
			applyComboFilter($("#CCContact"), "getParentUID", $("#Client_uid").val());
			applyComboFilter($("#InvoiceContact"), "getParentUID", $("#Client_uid").val());
		}, 250)

		$("#Analysts").change(function (event) {
			$("#LeadAnalyst").empty();
			$.each($("#Analysts > option").filter(":selected"), function (k, v) {
				$("#LeadAnalyst").append('<option value="' + v.value + '">' + v.innerHTML + '</option>');
			});
		});

		$("#Contact").live("selected copy", function (event, item) {
		cc_contacts_set()
		});
		function cc_contacts_set() {
			/* Setting the CC Contacts after a Contact was set
			 *
			 * Contact.CCContact may contain a list of Contact references.
			 * So we need to select them in the form with some fakey html,
			 * and set them in the state.
			 */
			var contact_element = $("#Contact")
			var contact_uid = $(contact_element).attr("uid")
			// clear the CC selector widget and listing DIV
			var cc_div = $("#archetypes-fieldname-CCContact .multiValued-listing")
			var cc_uids = $("input[name='CCContact_uid']")
			$(cc_div).empty()
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
						$(cc_uids).val(cc_uids.join(","))
						for (var i = 0; i < cc_uids.length; i++) {
							var title = cc_titles[i]
							var uid = cc_uids[i]
							var del_btn_src = window.portal_url + "/++resource++bika.lims.images/delete.png"
							var del_btn =
							  "<img class='deletebtn' src='" + del_btn_src + "' fieldname='CCContact' uid='" + uid + "'/>"
							var new_item = "<div class='reference_multi_item' uid='" + uid + "'>" + del_btn + title + "</div>"
							$(cc_div).append($(new_item))
						}
					}
				})
			}
		}

		// can only have one of Profile or Template seleted
		$("#Template").bind("selected", function(event, item){
			$("#Profile").val("");
			$("#Profile").attr("uid", "");
			$("#Profile_uid").val("");
		});
		$("#Profile").bind("selected", function(event, item){
			$("#Template").val("");
			$("#Template").attr("uid", "");
			$("#Template_uid").val("");
		});

    }
}
