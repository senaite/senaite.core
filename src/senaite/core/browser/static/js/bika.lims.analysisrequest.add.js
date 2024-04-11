
/* Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.analysisrequest.add.coffee
 */

(function() {
  var bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
    slice = [].slice,
    hasProp = {}.hasOwnProperty,
    indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  window.AnalysisRequestAdd = (function() {
    function AnalysisRequestAdd() {
      this.init_service_conditions = bind(this.init_service_conditions, this);
      this.copy_service_conditions = bind(this.copy_service_conditions, this);
      this.set_service_conditions = bind(this.set_service_conditions, this);
      this.init_file_fields = bind(this.init_file_fields, this);
      this.on_form_submit = bind(this.on_form_submit, this);
      this.on_cancel = bind(this.on_cancel, this);
      this.on_ajax_end = bind(this.on_ajax_end, this);
      this.on_ajax_start = bind(this.on_ajax_start, this);
      this.ajax_post_form = bind(this.ajax_post_form, this);
      this.native_set_value = bind(this.native_set_value, this);
      this.on_copy_button_click = bind(this.on_copy_button_click, this);
      this.on_service_category_click = bind(this.on_service_category_click, this);
      this.on_service_listing_header_click = bind(this.on_service_listing_header_click, this);
      this.on_analysis_checkbox_click = bind(this.on_analysis_checkbox_click, this);
      this.on_analysis_profile_removed = bind(this.on_analysis_profile_removed, this);
      this.on_analysis_profile_selected = bind(this.on_analysis_profile_selected, this);
      this.on_analysis_template_removed = bind(this.on_analysis_template_removed, this);
      this.on_analysis_template_selected = bind(this.on_analysis_template_selected, this);
      this.on_analysis_lock_button_click = bind(this.on_analysis_lock_button_click, this);
      this.on_analysis_details_click = bind(this.on_analysis_details_click, this);
      this.on_referencefield_value_changed = bind(this.on_referencefield_value_changed, this);
      this.hide_all_service_info = bind(this.hide_all_service_info, this);
      this.get_service = bind(this.get_service, this);
      this.set_service = bind(this.set_service, this);
      this.set_template = bind(this.set_template, this);
      this.get_reference_field_value = bind(this.get_reference_field_value, this);
      this.set_reference_field_records = bind(this.set_reference_field_records, this);
      this.set_reference_field_query = bind(this.set_reference_field_query, this);
      this.reset_reference_field_query = bind(this.reset_reference_field_query, this);
      this.get_base_url = bind(this.get_base_url, this);
      this.get_portal_url = bind(this.get_portal_url, this);
      this.update_form = bind(this.update_form, this);
      this.recalculate_prices = bind(this.recalculate_prices, this);
      this.recalculate_records = bind(this.recalculate_records, this);
      this.get_flush_settings = bind(this.get_flush_settings, this);
      this.get_global_settings = bind(this.get_global_settings, this);
      this.render_template = bind(this.render_template, this);
      this.template_dialog = bind(this.template_dialog, this);
      this.debounce = bind(this.debounce, this);
      this.bind_eventhandler = bind(this.bind_eventhandler, this);
      this.load = bind(this.load, this);
    }

    AnalysisRequestAdd.prototype.load = function() {
      console.debug("AnalysisRequestAdd::load");
      $('input[type=text]').prop('autocomplete', 'off');
      this.global_settings = {};
      this.flush_settings = {};
      this.records_snapshot = {};
      this.applied_templates = {};
      this.deselected_uids = {};
      $(".blurrable").removeClass("blurrable");
      this.bind_eventhandler();
      this.init_file_fields();
      this.get_global_settings();
      this.get_flush_settings();
      this.recalculate_records();
      this.init_service_conditions();
      this.recalculate_prices();
      return this;
    };


    /* METHODS */

    AnalysisRequestAdd.prototype.bind_eventhandler = function() {

      /*
       * Binds callbacks on elements
       *
       * N.B. We attach all the events to the body and refine the selector to
       * delegate the event: https://learn.jquery.com/events/event-delegation/
       *
       */
      console.debug("AnalysisRequestAdd::bind_eventhandler");
      $("body").on("click", ".service-listing-header", this.on_service_listing_header_click);
      $("body").on("click", "tr.category", this.on_service_category_click);
      $("body").on("click", "tr[fieldname=Composite] input[type='checkbox']", this.recalculate_records);
      $("body").on("click", "tr[fieldname=InvoiceExclude] input[type='checkbox']", this.recalculate_records);
      $("body").on("click", "tr[fieldname=Analyses] input[type='checkbox'].analysisservice-cb", this.on_analysis_checkbox_click);
      $("body").on("click", ".service-lockbtn", this.on_analysis_lock_button_click);
      $("body").on("click", ".service-infobtn", this.on_analysis_details_click);
      $("body").on("click", "img.copybutton", this.on_copy_button_click);
      $("body").on("select deselect", "div.uidreferencefield textarea", this.on_referencefield_value_changed);
      $("body").on("select", "tr[fieldname=Template] textarea", this.on_analysis_template_selected);
      $("body").on("deselect", "tr[fieldname=Template] textarea", this.on_analysis_template_removed);
      $("body").on("select", "tr[fieldname=Profiles] textarea", this.on_analysis_profile_selected);
      $("body").on("deselect", "tr[fieldname=Profiles] textarea", this.on_analysis_profile_removed);
      $("body").on("click", "[name='save_button']", this.on_form_submit);
      $("body").on("click", "[name='save_and_copy_button']", this.on_form_submit);
      $("body").on("click", "[name='cancel_button']", this.on_cancel);

      /* internal events */
      $(this).on("form:changed", this.debounce(this.recalculate_records, 1000));
      $(this).on("services:changed", this.debounce(this.recalculate_prices, 2000));
      $(this).on("data:updated", this.debounce(this.update_form));
      $(this).on("data:updated", this.debounce(this.hide_all_service_info));
      $(this).on("ajax:start", this.on_ajax_start);
      return $(this).on("ajax:end", this.on_ajax_end);
    };

    AnalysisRequestAdd.prototype.debounce = function(func, threshold, execAsap) {

      /*
       * Debounce a function call
       * See: https://coffeescript-cookbook.github.io/chapters/functions/debounce
       */
      var timeout;
      timeout = null;
      return function() {
        var args, delayed, obj;
        args = 1 <= arguments.length ? slice.call(arguments, 0) : [];
        obj = this;
        delayed = function() {
          if (!execAsap) {
            func.apply(obj, args);
          }
          return timeout = null;
        };
        if (timeout) {
          clearTimeout(timeout);
        } else if (execAsap) {
          func.apply(obj, args);
        }
        return timeout = setTimeout(delayed, threshold || 300);
      };
    };

    AnalysisRequestAdd.prototype.template_dialog = function(template_id, context, buttons) {

      /*
       * Render the content of a Handlebars template in a jQuery UID dialog
         [1] http://handlebarsjs.com/
         [2] https://jqueryui.com/dialog/
       */
      var content;
      if (buttons == null) {
        buttons = {};
        buttons[_t("Yes")] = function() {
          $(this).trigger("yes");
          return $(this).dialog("close");
        };
        buttons[_t("No")] = function() {
          $(this).trigger("no");
          return $(this).dialog("close");
        };
      }
      content = this.render_template(template_id, context);
      return $(content).dialog({
        width: 450,
        resizable: false,
        closeOnEscape: false,
        buttons: buttons,
        open: function(event, ui) {
          return $(".ui-dialog-titlebar-close").hide();
        }
      });
    };

    AnalysisRequestAdd.prototype.render_template = function(template_id, context) {

      /*
       * Render Handlebars JS template
       */
      var content, source, template;
      source = $("#" + template_id).html();
      if (!source) {
        return;
      }
      template = Handlebars.compile(source);
      content = template(context);
      return content;
    };

    AnalysisRequestAdd.prototype.get_global_settings = function() {

      /*
       * Fetch global settings from the setup, e.g. show_prices
       */
      return this.ajax_post_form("get_global_settings").done(function(settings) {
        console.debug("Global Settings:", settings);
        this.global_settings = settings;
        return $(this).trigger("settings:updated", settings);
      });
    };

    AnalysisRequestAdd.prototype.get_flush_settings = function() {

      /*
       * Retrieve the flush settings mapping (field name -> list of other fields to flush)
       */
      return this.ajax_post_form("get_flush_settings").done(function(settings) {
        console.debug("Flush settings:", settings);
        this.flush_settings = settings;
        return $(this).trigger("flush_settings:updated", settings);
      });
    };

    AnalysisRequestAdd.prototype.recalculate_records = function() {

      /*
       * Submit all form values to the server to recalculate the records
       */
      return this.ajax_post_form("recalculate_records").done(function(records) {
        console.debug("Recalculate Analyses: Records=", records);
        this.records_snapshot = records;
        return $(this).trigger("data:updated", records);
      });
    };

    AnalysisRequestAdd.prototype.recalculate_prices = function() {

      /*
       * Submit all form values to the server to recalculate the prices of all columns
       */
      if (this.global_settings.show_prices === false) {
        console.debug("*** Skipping Price calculation ***");
        return;
      }
      return this.ajax_post_form("recalculate_prices").done(function(data) {
        var arnum, prices;
        console.debug("Recalculate Prices Data=", data);
        for (arnum in data) {
          if (!hasProp.call(data, arnum)) continue;
          prices = data[arnum];
          $("#discount-" + arnum).text(prices.discount);
          $("#subtotal-" + arnum).text(prices.subtotal);
          $("#vat-" + arnum).text(prices.vat);
          $("#total-" + arnum).text(prices.total);
        }
        return $(this).trigger("prices:updated", data);
      });
    };

    AnalysisRequestAdd.prototype.update_form = function(event, records) {

      /*
       * Update form according to the server data
       *
       * Records provided from the server (see ajax_recalculate_records)
       */
      var me;
      console.debug("*** update_form ***");
      me = this;
      $(".service-lockbtn").hide();
      return $.each(records, function(arnum, record) {
        var discard;
        discard = ["service_metadata", "template_metadata"];
        $.each(record, function(name, metadata) {
          if (indexOf.call(discard, name) >= 0 || !name.endsWith("_metadata")) {
            return;
          }
          return $.each(metadata, function(uid, obj_info) {
            return me.apply_field_value(arnum, obj_info);
          });
        });
        $.each(record.service_metadata, function(uid, metadata) {
          var lock;
          lock = $("#" + uid + "-" + arnum + "-lockbtn");
          if (uid in record.service_to_profiles) {
            lock.show();
          }
          return me.set_service(arnum, uid, true);
        });
        $.each(record.template_metadata, function(uid, template) {
          return me.set_template(arnum, template);
        });
        return $.each(record.unmet_dependencies, function(uid, dependencies) {
          var context, dialog, service;
          service = record.service_metadata[uid];
          context = {
            "service": service,
            "dependencies": dependencies
          };
          dialog = me.template_dialog("dependency-add-template", context);
          dialog.on("yes", function() {
            $.each(dependencies, function(index, service) {
              return me.set_service(arnum, service.uid, true);
            });
            return $(me).trigger("form:changed");
          });
          dialog.on("no", function() {
            me.set_service(arnum, uid, false);
            return $(me).trigger("form:changed");
          });
          return false;
        });
      });
    };

    AnalysisRequestAdd.prototype.get_portal_url = function() {

      /*
       * Return the portal url (calculated in code)
       */
      var url;
      url = $("input[name=portal_url]").val();
      return url;
    };

    AnalysisRequestAdd.prototype.get_base_url = function() {

      /*
       * Return the current (relative) base url
       */
      var base_url;
      base_url = window.location.href;
      if (base_url.search("/portal_factory") >= 0) {
        return base_url.split("/portal_factory")[0];
      }
      return base_url.split("/ar_add")[0];
    };

    AnalysisRequestAdd.prototype.apply_field_value = function(arnum, record) {

      /*
       * Applies the value for the given record, by setting values and applying
       * search filters to dependents
       */
      var me, title;
      me = this;
      title = record.title;
      console.debug("apply_field_value: arnum=" + arnum + " record=" + title);
      me.apply_dependent_values(arnum, record);
      return me.apply_dependent_filter_queries(record, arnum);
    };

    AnalysisRequestAdd.prototype.apply_dependent_values = function(arnum, record) {

      /*
       * Set default field values to dependents
       */
      var me;
      me = this;
      return $.each(record.field_values, function(field_name, values) {
        return me.apply_dependent_value(arnum, field_name, values);
      });
    };

    AnalysisRequestAdd.prototype.apply_dependent_value = function(arnum, field_name, values) {

      /*
       * Set values on field
       */
      var field, manually_deselected, me, uid, uids, values_json;
      if (!Array.isArray(values)) {
        values = [values];
      }
      me = this;
      values_json = JSON.stringify(values);
      field = $("#" + field_name + ("-" + arnum));
      console.debug("apply_dependent_value: field_name=" + field_name + " field_values=" + values_json);
      if (this.is_reference_field(field)) {
        manually_deselected = this.deselected_uids[field_name] || [];
        values = values.filter(function(value) {
          var ref;
          return ref = value.uid, indexOf.call(manually_deselected, ref) < 0;
        });
        uids = values.map(function(value) {
          return value.uid;
        });
        values.forEach((function(_this) {
          return function(value) {
            return _this.set_reference_field_records(field, value);
          };
        })(this));
        if (field.data("multi_valued") === 1) {
          return this.set_multi_reference_field(field, uids);
        } else {
          uid = uids.length > 0 ? uids[0] : "";
          return this.set_reference_field(field, uid);
        }
      } else {
        return values.forEach(function(value, index) {
          if ((value.if_empty != null) && value.if_empty === true) {
            if (field.val()) {
              return;
            }
          }
          if (value.value != null) {
            if (typeof value.value === "boolean") {
              return field.prop("checked", value.value);
            } else {
              return field.val(value.value);
            }
          }
        });
      }
    };

    AnalysisRequestAdd.prototype.apply_dependent_filter_queries = function(record, arnum) {

      /*
       * Apply search filters to dependents
       */
      var me;
      me = this;
      return $.each(record.filter_queries, function(field_name, query) {
        var field;
        field = $("#" + field_name + ("-" + arnum));
        return me.set_reference_field_query(field, query);
      });
    };

    AnalysisRequestAdd.prototype.flush_fields_for = function(field_name, arnum) {

      /*
       * Flush dependant fields
       */
      var field_ids, me;
      me = this;
      field_ids = this.flush_settings[field_name];
      return $.each(this.flush_settings[field_name], function(index, id) {
        var field;
        console.debug("flushing: id=" + id);
        field = $("#" + id + "-" + arnum);
        return me.flush_reference_field(field);
      });
    };

    AnalysisRequestAdd.prototype.is_reference_field = function(field) {

      /*
       * Checks if the given field is a reference field
       */
      field = $(field);
      if (field.hasClass("senaite-uidreference-widget-input")) {
        return true;
      }
      if (field.hasClass("ArchetypesReferenceWidget")) {
        return true;
      }
      return false;
    };

    AnalysisRequestAdd.prototype.flush_reference_field = function(field) {

      /*
       * Empty the reference field and restore the search query
       */
      if (!(field.length > 0)) {
        return;
      }
      this.reset_reference_field_query(field);
      return this.set_reference_field(field, "");
    };

    AnalysisRequestAdd.prototype.reset_reference_field_query = function(field) {

      /*
       * Restores the catalog search query for the given reference field
       */
      if (!(field.length > 0)) {
        return;
      }
      return this.set_reference_field_query(field, {});
    };

    AnalysisRequestAdd.prototype.set_reference_field_query = function(field, query) {

      /*
       * Set the catalog search query for the given reference field
       */
      var search_query;
      if (!(field.length > 0)) {
        return;
      }
      search_query = JSON.stringify(query);
      field.attr("data-search_query", search_query);
      return console.info("----------> Set search query for field " + field.selector + " -> " + search_query);
    };

    AnalysisRequestAdd.prototype.set_reference_field_records = function(field, records) {

      /*
       * Set data-records to display the UID of a reference field
       */
      var $field, existing_records, new_records;
      if (records == null) {
        records = {};
      }
      $field = $(field);
      existing_records = JSON.parse($field.attr("data-records") || '{}');
      new_records = Object.assign(existing_records, records);
      return $field.attr("data-records", JSON.stringify(new_records));
    };

    AnalysisRequestAdd.prototype.set_reference_field = function(field, uid) {

      /*
       * Set the UID of a reference field
       * NOTE: This method overrides any existing value!
       */
      var fieldname, textarea;
      if (!(field.length > 0)) {
        return;
      }
      fieldname = JSON.parse(field.data("name"));
      console.debug("set_reference_field:: field=" + fieldname + " uid=" + uid);
      textarea = field.find("textarea");
      return this.native_set_value(textarea[0], uid);
    };

    AnalysisRequestAdd.prototype.set_multi_reference_field = function(field, uids, append) {
      var existing, fieldname, textarea;
      if (append == null) {
        append = true;
      }

      /*
       * Set multiple UIDs of a reference field
       */
      if (!(field.length > 0)) {
        return;
      }
      if (uids == null) {
        uids = [];
      }
      fieldname = JSON.parse(field.data("name"));
      console.debug("set_multi_reference_field:: field=" + fieldname + " uids=" + uids);
      textarea = field.find("textarea");
      if (!append) {
        return this.native_set_value(textarea[0], uids.join("\n"));
      } else {
        existing = textarea.val().split("\n");
        uids.forEach(function(uid) {
          if (indexOf.call(existing, uid) < 0) {
            return existing = existing.concat(uid);
          }
        });
        return this.native_set_value(textarea[0], existing.join("\n"));
      }
    };

    AnalysisRequestAdd.prototype.get_reference_field_value = function(field) {

      /*
       * Return the value of a single/multi reference field
       */
      var $field, $textarea;
      $field = $(field);
      if ($field.type === "textarea") {
        $textarea = $field;
      } else {
        $textarea = $field.find("textarea");
      }
      return $textarea.val();
    };

    AnalysisRequestAdd.prototype.set_template = function(arnum, template) {

      /*
       * Apply the template data to all fields of arnum
       */
      var field, me, template_field, template_uid, uid, value;
      me = this;
      template_field = $("#Template-" + arnum);
      template_uid = this.get_reference_field_value(template_field);
      if (arnum in this.applied_templates) {
        if (this.applied_templates[arnum] === template_uid) {
          console.debug("Skipping already applied template");
          return;
        }
      }
      this.applied_templates[arnum] = template_uid;
      field = $("#SampleType-" + arnum);
      value = this.get_reference_field_value(field);
      if (!value) {
        uid = template.sample_type_uid;
        this.set_reference_field(field, uid);
      }
      field = $("#SamplePoint-" + arnum);
      value = this.get_reference_field_value(field);
      if (!value) {
        uid = template.sample_point_uid;
        this.set_reference_field(field, uid);
      }
      field = $("#Composite-" + arnum);
      field.prop("checked", template.composite);
      $.each(template.service_uids, function(index, uid) {
        return me.set_service(arnum, uid, true);
      });
      return this.set_reference_field(template_field, template_uid);
    };

    AnalysisRequestAdd.prototype.set_service = function(arnum, uid, checked) {

      /*
       * Select the checkbox of a service by UID
       */
      var el, me, poc;
      console.debug("*** set_service::AR=" + arnum + " UID=" + uid + " checked=" + checked);
      me = this;
      el = $("td[fieldname='Analyses-" + arnum + "'] #cb_" + arnum + "_" + uid);
      if (el.is(":checked") === checked) {
        return;
      }
      el.prop("checked", checked);
      poc = el.closest("tr[poc]").attr("poc");
      if (this.is_poc_expanded(poc)) {
        el.closest("tr").addClass("visible");
      }
      me.set_service_conditions(el);
      return $(this).trigger("services:changed");
    };

    AnalysisRequestAdd.prototype.get_service = function(uid) {

      /*
       * Fetch the service data from server by UID
       */
      var options;
      options = {
        data: {
          uid: uid
        },
        processData: true,
        contentType: 'application/x-www-form-urlencoded; charset=UTF-8'
      };
      return this.ajax_post_form("get_service", options).done(function(data) {
        return console.debug("get_service::data=", data);
      });
    };

    AnalysisRequestAdd.prototype.hide_all_service_info = function() {

      /*
       * hide all open service info boxes
       */
      var info;
      info = $("div.service-info");
      return info.hide();
    };

    AnalysisRequestAdd.prototype.is_poc_expanded = function(poc) {

      /*
       * Checks if the point of captures are visible
       */
      var el;
      el = $("tr.service-listing-header[poc=" + poc + "]");
      return el.hasClass("visible");
    };

    AnalysisRequestAdd.prototype.toggle_poc_categories = function(poc, toggle) {

      /*
       * Toggle all categories within a point of capture (lab/service)
       * :param poc: the point of capture (lab/field)
       * :param toggle: services visible if true
       */
      var categories, el, services, services_checked, toggle_buttons;
      if (toggle == null) {
        toggle = !this.is_poc_expanded(poc);
      }
      el = $("tr[data-poc=" + poc + "]");
      categories = $("tr.category." + poc);
      services = $("tr.service." + poc);
      services_checked = $("input[type=checkbox]:checked", services);
      toggle_buttons = $(".service-category-toggle");
      if (toggle) {
        el.addClass("visible");
        categories.addClass("visible");
        return services_checked.closest("tr").addClass("visible");
      } else {
        el.removeClass("visible");
        categories.removeClass("visible");
        categories.removeClass("expanded");
        services.removeClass("visible");
        services.removeClass("expanded");
        return toggle_buttons.text("+");
      }
    };


    /* EVENT HANDLER */

    AnalysisRequestAdd.prototype.on_referencefield_value_changed = function(event) {

      /*
       * Generic event handler for when a reference field value changed
       */
      var $el, after_change, arnum, el, event_data, field_name, manually_deselected, me, select, value;
      me = this;
      el = event.currentTarget;
      $el = $(el);
      field_name = $el.closest("tr[fieldname]").attr("fieldname");
      arnum = $el.closest("[arnum]").attr("arnum");
      value = event.detail.value;
      if (value) {
        manually_deselected = this.deselected_uids[field_name] || [];
        select = event.type === "select" ? true : false;
        if (select) {
          manually_deselected = manually_deselected.filter(function(item) {
            return item !== value;
          });
          console.debug("Reference with UID " + value + " was manually selected");
        } else {
          manually_deselected = manually_deselected.indexOf(value > -1) ? manually_deselected.concat(value) : void 0;
          console.debug("Reference with UID " + value + " was manually deselected");
        }
        this.deselected_uids[field_name] = manually_deselected;
      }
      if (field_name === "Template" || field_name === "Profiles") {
        return;
      }
      console.debug("°°° on_referencefield_value_changed: field_name=" + field_name + " arnum=" + arnum + " °°°");
      me.flush_fields_for(field_name, arnum);
      event_data = {
        bubbles: true,
        detail: {
          value: el.value
        }
      };
      after_change = new CustomEvent(field_name + ":after_change", event_data);
      el.dispatchEvent(after_change);
      return $(me).trigger("form:changed");
    };

    AnalysisRequestAdd.prototype.on_analysis_details_click = function(event) {

      /*
       * Eventhandler when the user clicked on the info icon of a service.
       */
      var $el, arnum, context, data, el, extra, info, profiles, record, template, templates, uid;
      el = event.currentTarget;
      $el = $(el);
      uid = $el.attr("uid");
      arnum = $el.closest("[arnum]").attr("arnum");
      console.debug("°°° on_analysis_column::UID=" + uid + "°°°");
      info = $("div.service-info", $el.parent());
      info.empty();
      data = info.data("data");
      extra = {
        profiles: [],
        templates: []
      };
      record = this.records_snapshot[arnum];
      if (uid in record.service_to_profiles) {
        profiles = record.service_to_profiles[uid];
        $.each(profiles, function(index, uid) {
          return extra["profiles"].push(record.profiles_metadata[uid]);
        });
      }
      if (uid in record.service_to_templates) {
        templates = record.service_to_templates[uid];
        $.each(templates, function(index, uid) {
          return extra["templates"].push(record.template_metadata[uid]);
        });
      }
      if (!data) {
        return this.get_service(uid).done(function(data) {
          var context, template;
          context = $.extend({}, data, extra);
          template = this.render_template("service-info", context);
          info.append(template);
          info.data("data", context);
          return info.fadeIn();
        });
      } else {
        context = $.extend({}, data, extra);
        template = this.render_template("service-info", context);
        info.append(template);
        return info.fadeToggle();
      }
    };

    AnalysisRequestAdd.prototype.on_analysis_lock_button_click = function(event) {

      /*
       * Eventhandler when an Analysis Profile was removed.
       */
      var $el, arnum, buttons, context, dialog, el, me, profile_uid, record, template_uid, uid;
      console.debug("°°° on_analysis_lock_button_click °°°");
      me = this;
      el = event.currentTarget;
      $el = $(el);
      uid = $el.attr("uid");
      arnum = $el.closest("[arnum]").attr("arnum");
      record = me.records_snapshot[arnum];
      context = {};
      context["service"] = record.service_metadata[uid];
      context["profiles"] = [];
      context["templates"] = [];
      if (uid in record.service_to_profiles) {
        profile_uid = record.service_to_profiles[uid];
        context["profiles"].push(record.profiles_metadata[profile_uid]);
      }
      if (uid in record.service_to_templates) {
        template_uid = record.service_to_templates[uid];
        context["templates"].push(record.template_metadata[template_uid]);
      }
      buttons = {
        OK: function() {
          return $(this).dialog("close");
        }
      };
      return dialog = this.template_dialog("service-dependant-template", context, buttons);
    };

    AnalysisRequestAdd.prototype.on_analysis_template_selected = function(event) {

      /*
       * Eventhandler when an Analysis Template was selected.
       */
      console.debug("°°° on_analysis_template_selected °°°");
      return $(this).trigger("form:changed");
    };

    AnalysisRequestAdd.prototype.on_analysis_template_removed = function(event) {

      /*
       * Eventhandler when an Analysis Template was removed.
       */
      var $el, arnum, el;
      console.debug("°°° on_analysis_template_removed °°°");
      el = event.currentTarget;
      $el = $(el);
      arnum = $el.closest("[arnum]").attr("arnum");
      this.applied_templates[arnum] = null;
      return $(this).trigger("form:changed");
    };

    AnalysisRequestAdd.prototype.on_analysis_profile_selected = function(event) {

      /*
       * Eventhandler when an Analysis Profile was selected.
       */
      console.debug("°°° on_analysis_profile_selected °°°");
      return $(this).trigger("form:changed");
    };

    AnalysisRequestAdd.prototype.on_analysis_profile_removed = function(event) {

      /*
       * Eventhandler when an Analysis Profile was removed.
       */
      var $el, arnum, context, dialog, el, me, profile_metadata, profile_services, profile_uid, record;
      console.debug("°°° on_analysis_profile_removed °°°");
      me = this;
      el = event.currentTarget;
      $el = $(el);
      arnum = $el.closest("[arnum]").attr("arnum");
      profile_uid = event.detail.value;
      record = this.records_snapshot[arnum];
      profile_metadata = record.profiles_metadata[profile_uid];
      profile_services = [];
      $.each(record.profile_to_services[profile_uid], function(index, uid) {
        return profile_services.push(record.service_metadata[uid]);
      });
      context = {};
      context["profile"] = profile_metadata;
      context["services"] = profile_services;
      me = this;
      dialog = this.template_dialog("profile-remove-template", context);
      dialog.on("yes", function() {
        $.each(profile_services, function(index, service) {
          return me.set_service(arnum, service.uid, false);
        });
        return $(me).trigger("form:changed");
      });
      return dialog.on("no", function() {
        return $(me).trigger("form:changed");
      });
    };

    AnalysisRequestAdd.prototype.on_analysis_checkbox_click = function(event) {

      /*
       * Eventhandler for Analysis Service Checkboxes.
       */
      var $el, checked, el, me, uid;
      me = this;
      el = event.currentTarget;
      checked = el.checked;
      $el = $(el);
      uid = $el.val();
      console.debug("°°° on_analysis_click::UID=" + uid + " checked=" + checked + "°°°");
      me.set_service_conditions($el);
      $(me).trigger("form:changed");
      return $(me).trigger("services:changed");
    };

    AnalysisRequestAdd.prototype.on_service_listing_header_click = function(event) {

      /*
       * Eventhandler for analysis service category header rows.
       * Toggles the visibility of all categories within this poc.
       */
      var $el, poc, toggle, visible;
      $el = $(event.currentTarget);
      poc = $el.data("poc");
      visible = $el.hasClass("visible");
      toggle = !visible;
      return this.toggle_poc_categories(poc, toggle);
    };

    AnalysisRequestAdd.prototype.on_service_category_click = function(event) {

      /*
       * Eventhandler for analysis service category rows.
       * Toggles the visibility of all services within this category.
       * Selected services always stay visible.
       */
      var $btn, $el, category, expanded, poc, services, services_checked;
      event.preventDefault();
      $el = $(event.currentTarget);
      poc = $el.attr("poc");
      $btn = $(".service-category-toggle", $el);
      expanded = $el.hasClass("expanded");
      category = $el.data("category");
      services = $("tr." + poc + "." + category);
      services_checked = $("input[type=checkbox]:checked", services);
      console.debug("°°° on_service_category_click: category=" + category + " °°°");
      if (expanded) {
        $btn.text("+");
        $el.removeClass("expanded");
        services.removeClass("visible");
        services.removeClass("expanded");
        return services_checked.closest("tr").addClass("visible");
      } else {
        $btn.text("-");
        $el.addClass("expanded");
        services.addClass("visible");
        return services.addClass("expanded");
      }
    };

    AnalysisRequestAdd.prototype.on_copy_button_click = function(event) {

      /*
       * Eventhandler for the field copy button per row.
       * Copies the value of the first field in this row to the remaining.
       * XXX Refactor
       */
      var $el, $td1, $tr, ar_count, el, i, me, record_one, records, results, td1, tr, value;
      console.debug("°°° on_copy_button_click °°°");
      me = this;
      el = event.target;
      $el = $(el);
      tr = $el.closest('tr')[0];
      $tr = $(tr);
      td1 = $(tr).find('td[arnum="0"]').first();
      $td1 = $(td1);
      ar_count = parseInt($('input[id="ar_count"]').val(), 10);
      if (!(ar_count > 1)) {
        return;
      }
      record_one = this.records_snapshot[0];
      if ($(td1).find('.ArchetypesReferenceWidget').length > 0) {
        console.debug("-> Copy reference field");
        el = $(td1).find(".ArchetypesReferenceWidget");
        records = JSON.parse(el.attr("data-records")) || {};
        value = me.get_reference_field_value(el);
        $.each((function() {
          results = [];
          for (var i = 1; 1 <= ar_count ? i <= ar_count : i >= ar_count; 1 <= ar_count ? i++ : i--){ results.push(i); }
          return results;
        }).apply(this), function(arnum) {
          var _el, _field_name, _td;
          if (!(arnum > 0)) {
            return;
          }
          _td = $tr.find("td[arnum=" + arnum + "]");
          _el = $(_td).find(".ArchetypesReferenceWidget");
          _field_name = _el.closest("tr[fieldname]").attr("fieldname");
          me.flush_fields_for(_field_name, arnum);
          me.set_reference_field_records(_el, records);
          return me.set_reference_field(_el, value);
        });
        $(me).trigger("form:changed");
        return;
      }
      $td1.find("input[type=checkbox]").each(function(index, el) {
        var checked, is_service, j, results1;
        console.debug("-> Copy checkbox field");
        $el = $(el);
        checked = $el.prop("checked");
        is_service = $el.hasClass("analysisservice-cb");
        $.each((function() {
          results1 = [];
          for (var j = 1; 1 <= ar_count ? j <= ar_count : j >= ar_count; 1 <= ar_count ? j++ : j--){ results1.push(j); }
          return results1;
        }).apply(this), function(arnum) {
          var _el, _td, uid;
          if (!(arnum > 0)) {
            return;
          }
          _td = $tr.find("td[arnum=" + arnum + "]");
          _el = $(_td).find("input[type=checkbox]")[index];
          $(_el).prop("checked", checked);
          if (is_service) {
            uid = $el.closest("[uid]").attr("uid");
            me.set_service_conditions($(_el));
            return me.copy_service_conditions(0, arnum, uid);
          }
        });
        if (is_service) {
          return $(me).trigger("services:changed");
        }
      });
      $td1.find("select").each(function(index, el) {
        var j, results1;
        console.debug("-> Copy select field");
        $el = $(el);
        value = $el.val();
        return $.each((function() {
          results1 = [];
          for (var j = 1; 1 <= ar_count ? j <= ar_count : j >= ar_count; 1 <= ar_count ? j++ : j--){ results1.push(j); }
          return results1;
        }).apply(this), function(arnum) {
          var _el, _td;
          if (!(arnum > 0)) {
            return;
          }
          _td = $tr.find("td[arnum=" + arnum + "]");
          _el = $(_td).find("select")[index];
          return $(_el).val(value);
        });
      });
      $td1.find("input[type=text]").each(function(index, el) {
        var j, results1;
        console.debug("-> Copy text field");
        $el = $(el);
        value = $el.val();
        return $.each((function() {
          results1 = [];
          for (var j = 1; 1 <= ar_count ? j <= ar_count : j >= ar_count; 1 <= ar_count ? j++ : j--){ results1.push(j); }
          return results1;
        }).apply(this), function(arnum) {
          var _el, _td;
          if (!(arnum > 0)) {
            return;
          }
          _td = $tr.find("td[arnum=" + arnum + "]");
          _el = $(_td).find("input[type=text]")[index];
          return $(_el).val(value);
        });
      });
      $td1.find("input[type=number]").each(function(index, el) {
        var j, results1;
        console.debug("-> Copy text field");
        $el = $(el);
        value = $el.val();
        return $.each((function() {
          results1 = [];
          for (var j = 1; 1 <= ar_count ? j <= ar_count : j >= ar_count; 1 <= ar_count ? j++ : j--){ results1.push(j); }
          return results1;
        }).apply(this), function(arnum) {
          var _el, _td;
          if (!(arnum > 0)) {
            return;
          }
          _td = $tr.find("td[arnum=" + arnum + "]");
          _el = $(_td).find("input[type=number]")[index];
          return $(_el).val(value);
        });
      });
      $td1.find("textarea").each(function(index, el) {
        var j, results1;
        console.debug("-> Copy textarea field");
        $el = $(el);
        value = $el.val();
        return $.each((function() {
          results1 = [];
          for (var j = 1; 1 <= ar_count ? j <= ar_count : j >= ar_count; 1 <= ar_count ? j++ : j--){ results1.push(j); }
          return results1;
        }).apply(this), function(arnum) {
          var _el, _td;
          if (!(arnum > 0)) {
            return;
          }
          _td = $tr.find("td[arnum=" + arnum + "]");
          _el = $(_td).find("textarea")[index];
          return me.native_set_value(_el, value);
        });
      });
      $td1.find("input[type=radio]").each(function(index, el) {
        var checked, j, results1;
        console.debug("-> Copy radio field");
        $el = $(el);
        checked = $(el).is(":checked");
        return $.each((function() {
          results1 = [];
          for (var j = 1; 1 <= ar_count ? j <= ar_count : j >= ar_count; 1 <= ar_count ? j++ : j--){ results1.push(j); }
          return results1;
        }).apply(this), function(arnum) {
          var _el, _td;
          if (!(arnum > 0)) {
            return;
          }
          _td = $tr.find("td[arnum=" + arnum + "]");
          _el = $(_td).find("input[type=radio]")[index];
          return $(_el).prop("checked", checked);
        });
      });
      $td1.find("input[type='date']").each(function(index, el) {
        var j, results1;
        console.debug("-> Copy date field");
        $el = $(el);
        value = $el.val();
        return $.each((function() {
          results1 = [];
          for (var j = 1; 1 <= ar_count ? j <= ar_count : j >= ar_count; 1 <= ar_count ? j++ : j--){ results1.push(j); }
          return results1;
        }).apply(this), function(arnum) {
          var _el, _td;
          if (!(arnum > 0)) {
            return;
          }
          _td = $tr.find("td[arnum=" + arnum + "]");
          _el = $(_td).find("input[type='date']")[index];
          return $(_el).val(value);
        });
      });
      $td1.find("input[type='time']").each(function(index, el) {
        var j, results1;
        console.debug("-> Copy time field");
        $el = $(el);
        value = $el.val();
        return $.each((function() {
          results1 = [];
          for (var j = 1; 1 <= ar_count ? j <= ar_count : j >= ar_count; 1 <= ar_count ? j++ : j--){ results1.push(j); }
          return results1;
        }).apply(this), function(arnum) {
          var _el, _td;
          if (!(arnum > 0)) {
            return;
          }
          _td = $tr.find("td[arnum=" + arnum + "]");
          _el = $(_td).find("input[type='time']")[index];
          return $(_el).val(value);
        });
      });
      $td1.find("input[type='hidden']").each(function(index, el) {
        var j, results1;
        console.debug("-> Copy hidden field");
        $el = $(el);
        value = $el.val();
        return $.each((function() {
          results1 = [];
          for (var j = 1; 1 <= ar_count ? j <= ar_count : j >= ar_count; 1 <= ar_count ? j++ : j--){ results1.push(j); }
          return results1;
        }).apply(this), function(arnum) {
          var _el, _td;
          if (!(arnum > 0)) {
            return;
          }
          _td = $tr.find("td[arnum=" + arnum + "]");
          _el = $(_td).find("input[type='hidden']")[index];
          return $(_el).val(value);
        });
      });
      return $(me).trigger("form:changed");
    };


    /**
      * Set input value with native setter to support ReactJS components
     */

    AnalysisRequestAdd.prototype.native_set_value = function(input, value) {
      var event, setter;
      setter = null;
      if (input.tagName === "TEXTAREA") {
        setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
      } else if (input.tagName === "SELECT") {
        setter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, "value").set;
      } else if (input.tagName === "INPUT") {
        setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
      } else {
        input.value = value;
      }
      if (setter) {
        setter.call(input, value);
      }
      event = new Event("input", {
        bubbles: true
      });
      return input.dispatchEvent(event);
    };

    AnalysisRequestAdd.prototype.ajax_post_form = function(endpoint, options) {
      var ajax_options, base_url, form, form_data, me, url;
      if (options == null) {
        options = {};
      }

      /*
       * Ajax POST the form data to the given endpoint
       */
      console.debug("°°° ajax_post_form::Endpoint=" + endpoint + " °°°");
      base_url = this.get_base_url();
      url = base_url + "/ajax_ar_add/" + endpoint;
      console.debug("Ajax POST to url " + url);
      form = $("#analysisrequest_add_form");
      form_data = new FormData(form[0]);
      ajax_options = {
        url: url,
        type: 'POST',
        data: form_data,
        context: this,
        cache: false,
        dataType: 'json',
        processData: false,
        contentType: false,
        timeout: 600000
      };
      $.extend(ajax_options, options);

      /* Execute the request */
      me = this;
      $(me).trigger("ajax:start");
      return $.ajax(ajax_options).always(function(data) {
        return $(me).trigger("ajax:end");
      }).fail(function(request, status, error) {
        var msg;
        msg = _t("Sorry, an error occured: " + status);
        window.bika.lims.portalMessage(msg);
        return window.scroll(0, 0);
      });
    };

    AnalysisRequestAdd.prototype.on_ajax_start = function() {

      /*
       * Ajax request started
       */
      var save_and_copy_button, save_button;
      console.debug("°°° on_ajax_start °°°");
      save_button = $("input[name=save_button]");
      save_button.prop({
        "disabled": true
      });
      save_button[0].value = _t("Loading ...");
      save_and_copy_button = $("input[name=save_and_copy_button]");
      return save_and_copy_button.prop({
        "disabled": true
      });
    };

    AnalysisRequestAdd.prototype.on_ajax_end = function() {

      /*
       * Ajax request finished
       */
      var save_and_copy_button, save_button;
      console.debug("°°° on_ajax_end °°°");
      save_button = $("input[name=save_button]");
      save_button.prop({
        "disabled": false
      });
      save_button[0].value = _t("Save");
      save_and_copy_button = $("input[name=save_and_copy_button]");
      return save_and_copy_button.prop({
        "disabled": false
      });
    };

    AnalysisRequestAdd.prototype.on_cancel = function(event, callback) {
      var base_url;
      console.debug("°°° on_cancel °°°");
      event.preventDefault();
      base_url = this.get_base_url();
      return this.ajax_post_form("cancel").done(function(data) {
        if (data["redirect_to"]) {
          return window.location.replace(data["redirect_to"]);
        } else {
          return window.location.replace(base_url);
        }
      });
    };

    AnalysisRequestAdd.prototype.on_form_submit = function(event, callback) {

      /*
       * Eventhandler for the form submit button.
       * Extracts and submits all form data asynchronous.
       */
      var action, action_input, base_url, btn, me, portal_url;
      console.debug("°°° on_form_submit °°°");
      event.preventDefault();
      me = this;
      btn = event.currentTarget;
      action = "save";
      if (btn.name === "save_and_copy_button") {
        action = "save_and_copy";
      }
      action_input = document.querySelector("input[name='submit_action']");
      action_input.value = action;
      base_url = me.get_base_url();
      portal_url = me.get_portal_url();
      $("div.error").removeClass("error");
      $("div.fieldErrorBox").text("");
      return this.ajax_post_form("submit").done(function(data) {

        /*
         * data contains the following useful keys:
         * - errors: any errors which prevented the AR from being created
         *   these are displayed immediately and no further ation is taken
         * - destination: the URL to which we should redirect on success.
         *   This includes GET params for printing labels, so that we do not
         *   have to care about this here.
         */
        var dialog, errorbox, field, fieldname, message, msg, parent;
        if (data['errors']) {
          msg = data.errors.message;
          if (msg !== "") {
            msg = _t("Sorry, an error occured 🙈<p class='code'>" + msg + "</p>");
          }
          for (fieldname in data.errors.fielderrors) {
            field = $("#" + fieldname);
            parent = field.parent("div.field");
            if (field && parent) {
              parent.toggleClass("error");
              errorbox = parent.children("div.fieldErrorBox");
              message = data.errors.fielderrors[fieldname];
              errorbox.text(message);
              msg += message + "<br/>";
            }
          }
          window.bika.lims.portalMessage(msg);
          return window.scroll(0, 0);
        } else if (data['confirmation']) {
          dialog = me.template_dialog("confirm-template", data.confirmation);
          dialog.on("yes", function() {
            $("input[name=confirmed]").val("1");
            return $("input[name=save_button]").trigger("click");
          });
          return dialog.on("no", function() {
            var destination;
            destination = data.confirmation["destination"];
            if (destination) {
              return window.location.replace(portal_url + '/' + destination);
            }
          });
        } else if (data['redirect_to']) {
          return window.location.replace(data['redirect_to']);
        } else {
          return window.location.replace(base_url);
        }
      });
    };

    AnalysisRequestAdd.prototype.init_file_fields = function() {
      var me;
      me = this;
      return $('tr[fieldname] input[type="file"]').each(function(index, element) {
        var add_btn, add_btn_src, file_field, file_field_div;
        file_field = $(element);
        file_field.wrap("<div class='field'/>");
        file_field_div = file_field.parent();
        add_btn_src = window.portal_url + "/senaite_theme/icon/plus";
        add_btn = $("<img class='addbtn' width='16' style='cursor:pointer;' src='" + add_btn_src + "' />");
        add_btn.on("click", element, function(event) {
          return me.file_addbtn_click(event, element);
        });
        return file_field_div.append(add_btn);
      });
    };

    AnalysisRequestAdd.prototype.file_addbtn_click = function(event, element) {
      var arnum, counter, del_btn, del_btn_src, existing_file_field_names, existing_file_fields, file_field, file_field_div, holding_div, name, newfieldname, ref;
      file_field = $(element).clone();
      file_field.val("");
      file_field.wrap("<div class='field'/>");
      file_field_div = file_field.parent();
      ref = $(element).attr("name").split("-"), name = ref[0], arnum = ref[1];
      holding_div = $(element).parent().parent();
      existing_file_fields = holding_div.find("input[type='file']");
      existing_file_field_names = existing_file_fields.map(function(index, element) {
        return $(element).attr("name");
      });
      counter = 0;
      newfieldname = $(element).attr("name");
      while (indexOf.call(existing_file_field_names, newfieldname) >= 0) {
        newfieldname = name + "_" + counter + "-" + arnum;
        counter++;
      }
      file_field.attr("name", newfieldname);
      file_field.attr("id", newfieldname);
      del_btn_src = window.portal_url + "/senaite_theme/icon/delete";
      del_btn = $("<img class='delbtn' width='16' style='cursor:pointer;' src='" + del_btn_src + "' />");
      del_btn.on("click", element, function(event) {
        return $(this).parent().remove();
      });
      file_field_div.append(del_btn);
      return $(element).parent().parent().append(file_field_div);
    };

    AnalysisRequestAdd.prototype.set_service_conditions = function(el) {

      /*
       * Shows or hides the service conditions input elements for the service
       * bound to the checkbox element passed in
       */
      var arnum, base_info, checked, conditions, context, data, parent, template, uid;
      checked = el.prop("checked");
      parent = el.closest("td[uid][arnum]");
      uid = parent.attr("uid");
      arnum = parent.attr("arnum");
      conditions = $("div.service-conditions", parent);
      conditions.empty();
      if (!checked) {
        conditions.hide();
        return;
      }
      data = conditions.data("data");
      base_info = {
        arnum: arnum
      };
      if (!data) {
        return this.get_service(uid).done(function(data) {
          var context, template;
          context = $.extend({}, data, base_info);
          if (context.conditions && context.conditions.length > 0) {
            template = this.render_template("service-conditions", context);
            conditions.append(template);
            conditions.data("data", context);
            return conditions.show();
          }
        });
      } else {
        context = $.extend({}, data, base_info);
        if (context.conditions && context.conditions.length > 0) {
          template = this.render_template("service-conditions", context);
          conditions.append(template);
          return conditions.show();
        }
      }
    };

    AnalysisRequestAdd.prototype.copy_service_conditions = function(from, to, uid) {

      /*
       * Copies the service conditions values from those set for the service with
       * the specified uid and arnum_from column to the same analysis from the
       * arnum_to column
       */
      var me, source;
      console.debug("*** copy_service_conditions::from=" + from + " to=" + to + " UID=" + uid);
      me = this;
      source = "td[fieldname='Analyses-" + from + "'] div[id='" + uid + "-conditions'] input[name='ServiceConditions-" + from + ".value:records']";
      return $(source).each(function(idx, el) {
        var $el, dest, name, subfield;
        $el = $(el);
        name = $el.attr("name");
        subfield = $el.closest("[data-subfield]").attr("data-subfield");
        console.debug("-> Copy service condition: " + subfield);
        dest = $("td[fieldname='Analyses-" + to + "'] tr[data-subfield='" + subfield + "'] input[name='ServiceConditions-" + to + ".value:records']");
        return dest.val($el.val());
      });
    };

    AnalysisRequestAdd.prototype.init_service_conditions = function() {

      /*
       * Updates the visibility of the conditions for the selected services
       */
      var me, services;
      console.debug("init_service_conditions");
      me = this;
      services = $("input[type=checkbox].analysisservice-cb:checked");
      return $(services).each(function(idx, el) {
        var $el;
        $el = $(el);
        return me.set_service_conditions($el);
      });
    };

    return AnalysisRequestAdd;

  })();

}).call(this);
