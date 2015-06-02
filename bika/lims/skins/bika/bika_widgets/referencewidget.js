(function ($) {

	$(document).ready(function () {
		referencewidget_lookups();

		$(".reference_multi_item .deletebtn").live('click', function () {
			var fieldName = $(this).attr("fieldName");
			var uid = $(this).attr("uid");
			var existing_value = $("input[name^='" + fieldName + "_uid']").val()
			// It's true: the value may have been removed already, by another function
			if (existing_value) {
				var existing_uids = existing_value.split(",")
				destroy(existing_uids, uid);
				$("input[name^='" + fieldName + "_uid']").val(existing_uids.join(","));
				$("input[name='" + fieldName + "']").attr("uid", existing_uids.join(","));
				$(this).parent().remove();
			}
		});

		$(".ArchetypesReferenceWidget").bind("selected blur change", function () {
			var e = $(this).children("input.referencewidget");
			// multiValued fields always have empty values in the actual input widget:
			var multiValued = $(e).attr("multiValued") == "1"
			if (e.val() == '' && !multiValued) {
				fieldName = $(e).attr("name").split(":")[0];
				$(e).attr("uid", "");
				$("input[name^='" + fieldName + "_uid']").val("");
				$("div[name='" + fieldName + "-listing']").empty();
			}
		});
		save_UID_check();
		check_UID_check();
		load_addbutton_overlays();
		load_editbutton_overlays();
	});

}(jQuery));

function destroy(arr, val) {
	for (var i = 0; i < arr.length; i++) {
		if (arr[i] === val) {
			arr.splice(i, 1);
		}
	}
	return arr;
}

function referencewidget_lookups(elements) {
	// Any reference widgets that don't already have combogrid widgets
	var inputs;
	if (elements === undefined) {
		inputs = $(".ArchetypesReferenceWidget [combogrid_options]").not(".has_combogrid_widget");
	}
	else {
		inputs = elements;
	}
	for (var i = inputs.length - 1; i >= 0; i--) {
		var element = inputs[i];
		var options = $.parseJSON($(element).attr("combogrid_options"));
		if (!options) {
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

		options.select = function (event, ui) {
			event.preventDefault();
			var fieldName = $(this).attr("name");
			var skip;
			var uid_element = $(this).siblings("input[$='_uid']")
			var listing_div = $(this).siblings("div[id$='-listing']");
			if ($(listing_div).length > 0) {
				// Add selection to textfield value
				var existing_value = $(uid_element).val()
				var existing_uids = ""
				if (existing_value != undefined) {
					existing_uids = existing_value.split(",")
				}
				destroy(existing_uids, "");
				destroy(existing_uids, "[]");
				var selected_value = ui.item[$(this).attr("ui_item")];
				var selected_uid = ui.item.UID;
				if (existing_uids.indexOf(selected_uid) == -1) {
					existing_uids.push(selected_uid);
					$(this).val("");
					$(this).attr("uid", existing_uids.join(","));
					$(uid_element).val(existing_uids.join(","));
					// insert item to listing
					var del_btn_src = window.portal_url + "/++resource++bika.lims.images/delete.png";
					var del_btn = "<img class='deletebtn' data-contact-title='" + ui.item.Title + "' src='" + del_btn_src + "' fieldName='" + fieldName + "' uid='" + selected_uid + "'/>";
					var new_item = "<div class='reference_multi_item' uid='" + selected_uid + "'>" + del_btn + selected_value + "</div>";
					$(listing_div).append($(new_item));
				}

				// skip_referencewidget_lookup: a little cheat
				// it prevents this widget from falling over itself,
				// by allowing other JS to request that the "selected" action
				// is not triggered.
				skip = $(element).attr("skip_referencewidget_lookup");
				if (skip !== true) {
					// Pass the entire selected item through to the selected handler
					$(this).trigger("selected", ui.item);
				}
				$(element).removeAttr("skip_referencewidget_lookup");
				$(this).next("input").focus();
			}
			else {
				// Set value in activated element (must exist in colModel!)
				$(this).val(ui.item[$(this).attr("ui_item")]);
				$(this).attr("uid", ui.item.UID);
				$(uid_element).val(ui.item.UID);
				skip = $(element).attr("skip_referencewidget_lookup");
				if (skip !== true) {
					// Pass the entire selected item through to the selected handler
					$(this).trigger("selected", ui.item);
				}
				$(element).removeAttr("skip_referencewidget_lookup");
				$(this).next("input").focus();
			}
		};

		if (window.location.href.search("portal_factory") > -1) {
			options.url = window.location.href.split("/portal_factory")[0] + "/" + options.url;
		}
		options.url = options.url + "?_authenticator=" + $("input[name='_authenticator']").val();
		options.url = options.url + "&catalog_name=" + $(element).attr("catalog_name");
		options.url = options.url + "&base_query=" + $(element).attr("base_query");
		options.url = options.url + "&search_query=" + $(element).attr("search_query");
		options.url = options.url + "&colModel=" + $.toJSON($.parseJSON($(element).attr("combogrid_options")).colModel);
		options.url = options.url + "&search_fields=" + $.toJSON($.parseJSON($(element).attr("combogrid_options")).search_fields);
		options.url = options.url + "&discard_empty=" + $.toJSON($.parseJSON($(element).attr("combogrid_options")).discard_empty);
		options.url = options.url + "&force_all=" + $.toJSON($.parseJSON($(element).attr("combogrid_options")).force_all);
		$(element).combogrid(options);
		$(element).addClass("has_combogrid_widget");
		$(element).attr("search_query", "{}");
	}
}

function save_UID_check() {
	//Save the selected uid's item to avoid introduce non-listed
	//values inside the widget.
	$(".ArchetypesReferenceWidget").bind("selected", function () {
		// None of this stuff should take effect for multivalued widgets;
		// Right now, these must take care of themselves.
		var multiValued = $(this).attr("multiValued") == "1"
		if(multiValued){
			return
		}
		var uid = $(this).children("input.referencewidget").attr("uid");
		var val = $(this).children("input.referencewidget").val();
		$(this).children("input.referencewidget").attr("uid_check", uid);
		$(this).children("input.referencewidget").attr("val_check", val);
	});
}

function check_UID_check() {
	//Remove the necessary values to submit if the introduced data is
	//not correct.
	$(".ArchetypesReferenceWidget").children("input.referencewidget").bind("blur", function () {
		// None of this stuff should take effect for multivalued widgets;
		// Right now, these must take care of themselves.
		var multiValued = $(this).attr("multiValued") == "1"
		if(multiValued){
			return
		}
		var chk = $(this).attr("uid_check");
		var val_chk = $(this).attr("val_check");
		var value = $(this).val();
		//When is the first time you click on
		if ((chk == undefined || chk == false) && (value != "") && $(this).attr("uid")) {
			$(this).attr("uid_check", $(this).attr("uid"));
			$(this).attr("val_check", value);
		}
		//Write a non existent selection
		else if ((chk == undefined || chk == false) && (value != "")) {
			$(this).attr('uid', '');
			$(this).attr('value', '');
		}
		//UID is diferent from the checkUID, preventive option, maybe
		//never will be accomplished
		else if ($(this).attr("value") && (chk != undefined || chk != false) && (chk != $(this).attr("uid"))) {
			$(this).attr('uid', chk);
			$(this).attr('value', val_chk);
		}
		//Modified the value by hand and wrong, it restores the
		//previous option.
		else if ((val_chk != value) && value != '') {
			$(this).attr('uid', chk);
			$(this).attr('value', val_chk);
		}
	});
}

function apply_button_overlay(button) {
	/**
	 * Given an element (button), this function sets its overlay options.
	 * The overlay options to be applied are retrieved from the button's
	 * data_overlay attribute.
	 * Further info about jQuery overlay:
	 * http://jquerytools.github.io/documentation/overlay/
	 */
	// Obtain overlay options from html button attributes.
	var options = $.parseJSON($(button).attr('data_overlay'));
	options['subtype'] = 'ajax';
	var config = {};

	// overlay.OnLoad javascript snippet
	config['onLoad'] = function () {
		var triggerid = "[rel='#" + this.getTrigger().attr('id') + "']";
		// If there are defined some jsControllers, they'll be reloaded every time the overlay is loaded.
		var jscontrollers = $(triggerid).attr('data_jscontrollers');
		jscontrollers = $.parseJSON(jscontrollers);
		if (jscontrollers.length > 0) {
			window.bika.lims.loadControllers(false, jscontrollers);
		}
		// Check personalized onLoad functionalities.
		var handler = $(triggerid).attr('data_overlay_handler');
		if (handler != '') {
			var fn = window[handler];
			if (typeof fn === "function") {
				handler = new fn();
				if (typeof handler.onLoad === "function") {
					handler.onLoad(this);
				}
			}
		}
	};

	// overlay.OnBeforeClose javascript snippet
	config['onBeforeClose'] = function () {
		var triggerid = "[rel='#" + this.getTrigger().attr('id') + "']";
		var handler = $(triggerid).attr('data_overlay_handler');
		if (handler != '') {
			var fn = window[handler];
			if (typeof fn === "function") {
				handler = new fn();
				if (typeof handler.onBeforeClose === "function") {
					handler.onBeforeClose(this);
					// Done, exit
					return true;
				}
			}
		}
		var retfields = $.parseJSON($(triggerid).attr('data_returnfields'));
		if (retfields.length > 0) {
			// Default behaviour.
			// Set the value from the returnfields to the input
			// and select the first option.
			// This might be improved by finding a way to get the
			// uid of the object created/edited and assign directly
			// the value to the underlaying referencewidget
			var retvals = [];
			$.each(retfields, function (index, value) {
				var retval = $('div.overlay #' + value).val();
				if (retval != '') {
					retvals.push(retval);
				}
			});
			if (retvals.length > 0) {
				retvals = retvals.join(' ');
				$(triggerid).prev('input').val(retvals).focus();
				setTimeout(function () {
					$('.cg-DivItem').first().click();
				}, 500);
			}
		}
		return true;
	};
	options['config'] = config;
	$(button).prepOverlay(options);
}

function load_addbutton_overlays() {
	/**
	 * Add the overlay conditions for the AddButton.
	 */
	$('a.referencewidget-add-button').each(function (i) {
		apply_button_overlay('#' + $(this).attr('id'));
	});
}

function load_editbutton_overlay(button) {
	/**
	 * Given an element (button), show/hide the element depending on its trigger UID.
	 * No UID -> No object selected -> Noting to edit -> hide edit
	 * Yes UID -> Object selected -> Something to edit -> show edit.
	 */
	var element = '#' + $(button).attr('data_fieldid');
	var uid = $(element).attr('uid');
	// No UID found -> Hide Edit button
	if (!uid || uid == '') {
		$(button).hide();
	}
	else {
		// UID found -> Show Edit button & update href attribute
		$(button).show();
		// Get object's id
		var request_data = {
			catalog_name: "uid_catalog",
			UID: uid
		};
		window.bika.lims.jsonapi_read(request_data, function (data) {
			var root_href = $(button).attr('data_baseurl');
			var id = data.objects[0].id;
			$(button).attr('href', root_href + "/" + id + '/edit');
			apply_button_overlay(button);
		});
	}
}

function load_editbutton_overlays() {
	/**
	 * Add the overlay conditions for the EditButton.
	 */
	$('a.referencewidget-edit-button').each(function (i) {
		var button = '#' + $(this).attr('id');
		var fieldid = '#' + $(this).attr('data_fieldid');

		$(fieldid).bind("selected blur paste", function () {
			var button = '#' + $(this).siblings('a.referencewidget-edit-button').attr('id');
			load_editbutton_overlay(button);
		});

		load_editbutton_overlay(button);
	});
}

