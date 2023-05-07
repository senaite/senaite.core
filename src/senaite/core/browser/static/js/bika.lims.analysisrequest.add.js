(function() {
  /* Please use this command to compile this file into the parent `js` directory:
      coffee --no-header -w -o ../ -c bika.lims.analysisrequest.add.coffee
  */
  var hasProp = {}.hasOwnProperty,
    indexOf = [].indexOf;

  window.AnalysisRequestAdd = (function() {
    var typeIsArray;

    class AnalysisRequestAdd {
      constructor() {
        this.load = this.load.bind(this);
        /* METHODS */
        this.bind_eventhandler = this.bind_eventhandler.bind(this);
        this.debounce = this.debounce.bind(this);
        this.template_dialog = this.template_dialog.bind(this);
        this.render_template = this.render_template.bind(this);
        this.get_global_settings = this.get_global_settings.bind(this);
        this.get_flush_settings = this.get_flush_settings.bind(this);
        this.recalculate_records = this.recalculate_records.bind(this);
        this.recalculate_prices = this.recalculate_prices.bind(this);
        this.update_form = this.update_form.bind(this);
        this.get_portal_url = this.get_portal_url.bind(this);
        this.get_base_url = this.get_base_url.bind(this);
        this.reset_reference_field_query = this.reset_reference_field_query.bind(this);
        this.set_reference_field_query = this.set_reference_field_query.bind(this);
        this.set_reference_field_records = this.set_reference_field_records.bind(this);
        this.set_reference_field = this.set_reference_field.bind(this);
        this.get_reference_field_value = this.get_reference_field_value.bind(this);
        this.set_template = this.set_template.bind(this);
        this.set_service = this.set_service.bind(this);
        this.get_service = this.get_service.bind(this);
        this.hide_all_service_info = this.hide_all_service_info.bind(this);
        /* EVENT HANDLER */
        this.on_referencefield_value_changed = this.on_referencefield_value_changed.bind(this);
        this.on_analysis_details_click = this.on_analysis_details_click.bind(this);
        this.on_analysis_lock_button_click = this.on_analysis_lock_button_click.bind(this);
        this.on_analysis_template_selected = this.on_analysis_template_selected.bind(this);
        this.on_analysis_template_removed = this.on_analysis_template_removed.bind(this);
        this.on_analysis_profile_selected = this.on_analysis_profile_selected.bind(this);
        // Note: Context of callback bound to this object
        this.on_analysis_profile_removed = this.on_analysis_profile_removed.bind(this);
        this.on_analysis_checkbox_click = this.on_analysis_checkbox_click.bind(this);
        this.on_service_listing_header_click = this.on_service_listing_header_click.bind(this);
        this.on_service_category_click = this.on_service_category_click.bind(this);
        this.on_copy_button_click = this.on_copy_button_click.bind(this);
        /**
          * Set input value with native setter to support ReactJS components
         */
        this.native_set_value = this.native_set_value.bind(this);
        // Note: Context of callback bound to this object
        this.ajax_post_form = this.ajax_post_form.bind(this);
        this.on_ajax_start = this.on_ajax_start.bind(this);
        this.on_ajax_end = this.on_ajax_end.bind(this);
        this.on_cancel = this.on_cancel.bind(this);
        // Note: Context of callback bound to this object
        this.on_form_submit = this.on_form_submit.bind(this);
        this.init_file_fields = this.init_file_fields.bind(this);
        this.set_service_conditions = this.set_service_conditions.bind(this);
        this.copy_service_conditions = this.copy_service_conditions.bind(this);
        this.init_service_conditions = this.init_service_conditions.bind(this);
      }

      load() {
        console.debug("AnalysisRequestAdd::load");
        // disable browser autocomplete
        $('input[type=text]').prop('autocomplete', 'off');
        // storage for global Bika settings
        this.global_settings = {};
        // storage for mapping of fields to flush on_change
        this.flush_settings = {};
        // services data snapshot from recalculate_records
        // returns a mapping of arnum -> services data
        this.records_snapshot = {};
        // brain for already applied templates
        this.applied_templates = {};
        // manually deselected references
        // => keep track to avoid setting these fields with the default values
        this.deselected_uids = {};
        // Remove the '.blurrable' class to avoid inline field validation
        $(".blurrable").removeClass("blurrable");
        // bind the event handler to the elements
        this.bind_eventhandler();
        // N.B.: The new AR Add form handles File fields like this:
        // - File fields can carry more than one field (see init_file_fields)
        // - All uploaded files are extracted and added as attachments to the new created AR
        // - The file field itself (Plone) will stay empty therefore
        this.init_file_fields();
        // get the global settings on load
        this.get_global_settings();
        // get the flush settings
        this.get_flush_settings();
        // recalculate records on load (needed for AR copies)
        this.recalculate_records();
        // initialize service conditions (needed for AR copies)
        this.init_service_conditions();
        // always recalculate prices in the first run
        this.recalculate_prices();
        // return a reference to the instance
        return this;
      }

      bind_eventhandler() {
        /*
         * Binds callbacks on elements
         *
         * N.B. We attach all the events to the body and refine the selector to
         * delegate the event: https://learn.jquery.com/events/event-delegation/
         *
         */
        console.debug("AnalysisRequestAdd::bind_eventhandler");
        // Categories header clicked
        $("body").on("click", ".service-listing-header", this.on_service_listing_header_click);
        // Category toggle button clicked
        $("body").on("click", "tr.category", this.on_service_category_click);
        // Composite Checkbox clicked
        $("body").on("click", "tr[fieldname=Composite] input[type='checkbox']", this.recalculate_records);
        // InvoiceExclude Checkbox clicked
        $("body").on("click", "tr[fieldname=InvoiceExclude] input[type='checkbox']", this.recalculate_records);
        // Analysis Checkbox clicked
        $("body").on("click", "tr[fieldname=Analyses] input[type='checkbox'].analysisservice-cb", this.on_analysis_checkbox_click);
        // Analysis lock button clicked
        $("body").on("click", ".service-lockbtn", this.on_analysis_lock_button_click);
        // Analysis info button clicked
        $("body").on("click", ".service-infobtn", this.on_analysis_details_click);
        // Copy button clicked
        $("body").on("click", "img.copybutton", this.on_copy_button_click);
        // Generic select/deselect event handler for reference fields
        $("body").on("select deselect", "div.uidreferencefield textarea", this.on_referencefield_value_changed);
        // Analysis Template selected
        $("body").on("select", "tr[fieldname=Template] textarea", this.on_analysis_template_selected);
        // Analysis Template removed
        $("body").on("deselect", "tr[fieldname=Template] textarea", this.on_analysis_template_removed);
        // Analysis Profile selected
        $("body").on("select", "tr[fieldname=Profiles] textarea", this.on_analysis_profile_selected);
        // Analysis Profile deselected
        $("body").on("deselect", "tr[fieldname=Profiles] textarea", this.on_analysis_profile_removed);
        // Save button clicked
        $("body").on("click", "[name='save_button']", this.on_form_submit);
        // Save and copy button clicked
        $("body").on("click", "[name='save_and_copy_button']", this.on_form_submit);
        // Cancel button clicked
        $("body").on("click", "[name='cancel_button']", this.on_cancel);
        /* internal events */
        // handle value changes in the form
        $(this).on("form:changed", this.debounce(this.recalculate_records, 1000));
        // recalculate prices after services changed
        $(this).on("services:changed", this.debounce(this.recalculate_prices, 2000));
        // update form from records after the data changed
        $(this).on("data:updated", this.debounce(this.update_form));
        // hide open service info after data changed
        $(this).on("data:updated", this.debounce(this.hide_all_service_info));
        // handle Ajax events
        $(this).on("ajax:start", this.on_ajax_start);
        return $(this).on("ajax:end", this.on_ajax_end);
      }

      debounce(func, threshold, execAsap) {
        /*
         * Debounce a function call
         * See: https://coffeescript-cookbook.github.io/chapters/functions/debounce
         */
        var timeout;
        timeout = null;
        return function(...args) {
          var delayed, obj;
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
      }

      template_dialog(template_id, context, buttons) {
        var content;
        /*
         * Render the content of a Handlebars template in a jQuery UID dialog
           [1] http://handlebarsjs.com/
           [2] https://jqueryui.com/dialog/
         */
        // prepare the buttons
        if (buttons == null) {
          buttons = {};
          buttons[_t("Yes")] = function() {
            // trigger 'yes' event
            $(this).trigger("yes");
            return $(this).dialog("close");
          };
          buttons[_t("No")] = function() {
            // trigger 'no' event
            $(this).trigger("no");
            return $(this).dialog("close");
          };
        }
        // render the Handlebars template
        content = this.render_template(template_id, context);
        // render the dialog box
        return $(content).dialog({
          width: 450,
          resizable: false,
          closeOnEscape: false,
          buttons: buttons,
          open: function(event, ui) {
            // Hide the X button on the top right border
            return $(".ui-dialog-titlebar-close").hide();
          }
        });
      }

      render_template(template_id, context) {
        var content, source, template;
        /*
         * Render Handlebars JS template
         */
        // get the template by ID
        source = $(`#${template_id}`).html();
        if (!source) {
          return;
        }
        // Compile the handlebars template
        template = Handlebars.compile(source);
        // Render the template with the given context
        content = template(context);
        return content;
      }

      get_global_settings() {
        /*
         * Fetch global settings from the setup, e.g. show_prices
         */
        return this.ajax_post_form("get_global_settings").done(function(settings) {
          console.debug("Global Settings:", settings);
          // remember the global settings
          this.global_settings = settings;
          // trigger event for whom it might concern
          return $(this).trigger("settings:updated", settings);
        });
      }

      get_flush_settings() {
        /*
         * Retrieve the flush settings mapping (field name -> list of other fields to flush)
         */
        return this.ajax_post_form("get_flush_settings").done(function(settings) {
          console.debug("Flush settings:", settings);
          this.flush_settings = settings;
          return $(this).trigger("flush_settings:updated", settings);
        });
      }

      recalculate_records() {
        /*
         * Submit all form values to the server to recalculate the records
         */
        return this.ajax_post_form("recalculate_records").done(function(records) {
          console.debug("Recalculate Analyses: Records=", records);
          // remember a services snapshot
          this.records_snapshot = records;
          // trigger event for whom it might concern
          return $(this).trigger("data:updated", records);
        });
      }

      recalculate_prices() {
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
            $(`#discount-${arnum}`).text(prices.discount);
            $(`#subtotal-${arnum}`).text(prices.subtotal);
            $(`#vat-${arnum}`).text(prices.vat);
            $(`#total-${arnum}`).text(prices.total);
          }
          // trigger event for whom it might concern
          return $(this).trigger("prices:updated", data);
        });
      }

      update_form(event, records) {
        var me;
        /*
         * Update form according to the server data
         *
         * Records provided from the server (see ajax_recalculate_records)
         */
        console.debug("*** update_form ***");
        me = this;
        // initially hide all lock icons
        $(".service-lockbtn").hide();
        // set all values for one record (a single column in the AR Add form)
        return $.each(records, function(arnum, record) {
          var discard;
          // Apply the values generically, but those to be handled differently
          discard = ["service_metadata", "template_metadata"];
          $.each(record, function(name, metadata) {
            // Discard those fields that will be handled differently and those that
            // do not contain explicit object metadata
            if (indexOf.call(discard, name) >= 0 || !name.endsWith("_metadata")) {
              return;
            }
            return $.each(metadata, function(uid, obj_info) {
              return me.apply_field_value(arnum, obj_info);
            });
          });
          // set services
          $.each(record.service_metadata, function(uid, metadata) {
            var lock;
            // lock icon (to be displayed when the service cannot be deselected)
            lock = $(`#${uid}-${arnum}-lockbtn`);
            // service is included in a profile
            if (uid in record.service_to_profiles) {
              lock.show();
            }
            // select the service
            return me.set_service(arnum, uid, true);
          });
          // set template
          $.each(record.template_metadata, function(uid, template) {
            return me.set_template(arnum, template);
          });
          // handle unmet dependencies, one at a time
          return $.each(record.unmet_dependencies, function(uid, dependencies) {
            var context, dialog, service;
            service = record.service_metadata[uid];
            context = {
              "service": service,
              "dependencies": dependencies
            };
            dialog = me.template_dialog("dependency-add-template", context);
            dialog.on("yes", function() {
              // select the services
              $.each(dependencies, function(index, service) {
                return me.set_service(arnum, service.uid, true);
              });
              // trigger form:changed event
              return $(me).trigger("form:changed");
            });
            dialog.on("no", function() {
              // deselect the dependant service
              me.set_service(arnum, uid, false);
              // trigger form:changed event
              return $(me).trigger("form:changed");
            });
            // break the iteration after the first loop to avoid multiple dialogs.
            return false;
          });
        });
      }

      get_portal_url() {
        /*
         * Return the portal url (calculated in code)
         */
        var url;
        url = $("input[name=portal_url]").val();
        return url;
      }

      get_base_url() {
        /*
         * Return the current (relative) base url
         */
        var base_url;
        base_url = window.location.href;
        if (base_url.search("/portal_factory") >= 0) {
          return base_url.split("/portal_factory")[0];
        }
        return base_url.split("/ar_add")[0];
      }

      apply_field_value(arnum, record) {
        /*
         * Applies the value for the given record, by setting values and applying
         * search filters to dependents
         */
        var me, title;
        me = this;
        title = record.title;
        console.debug(`apply_field_value: arnum=${arnum} record=${title}`);
        // Set default values to dependents
        me.apply_dependent_values(arnum, record);
        // Apply search filters to other fields
        return me.apply_dependent_filter_queries(record, arnum);
      }

      apply_dependent_values(arnum, record) {
        /*
         * Set default field values to dependents
         */
        var me;
        me = this;
        return $.each(record.field_values, function(field_name, values) {
          return me.apply_dependent_value(arnum, field_name, values);
        });
      }

      apply_dependent_value(arnum, field_name, values) {
        /*
         * Set default field value
         */
        var field, manually_deselected, me, ref, values_json;
        me = this;
        values_json = JSON.stringify(values);
        field = $("#" + field_name + `-${arnum}`);
        if ((values.if_empty != null) && values.if_empty === true) {
          // Set the value if the field is empty only
          if (field.val()) {
            return;
          // handle reference fields
          } else if (this.is_reference_field(field) && this.get_reference_field_value(field)) {
            return;
          }
        }
        // reference field has a value
        console.debug(`apply_dependent_value: field_name=${field_name} field_values=${values_json}`);
        if ((values.uid != null) && (values.title != null)) {
          manually_deselected = this.deselected_uids[field_name] || [];
          // don't set if value was manually deslected
          if (ref = values.uid, indexOf.call(manually_deselected, ref) >= 0) {
            return;
          }
          // reference field value
          return me.set_reference_field(field, values.uid);
        } else if (values.value != null) {
          // default value
          if (typeof values.value === "boolean") {
            return field.prop("checked", values.value);
          } else {
            return field.val(values.value);
          }
        }
      }

      apply_dependent_filter_queries(record, arnum) {
        /*
         * Apply search filters to dependents
         */
        var me;
        me = this;
        return $.each(record.filter_queries, function(field_name, query) {
          var field;
          field = $("#" + field_name + `-${arnum}`);
          return me.set_reference_field_query(field, query);
        });
      }

      flush_fields_for(field_name, arnum) {
        /*
         * Flush dependant fields
         */
        var field_ids, me;
        me = this;
        field_ids = this.flush_settings[field_name];
        return $.each(this.flush_settings[field_name], function(index, id) {
          var field;
          console.debug(`flushing: id=${id}`);
          field = $(`#${id}-${arnum}`);
          return me.flush_reference_field(field);
        });
      }

      is_reference_field(field) {
        field = $(field);
        if (field.hasClass("senaite-uidreference-widget-input")) {
          return true;
        }
        if (field.hasClass("ArchetypesReferenceWidget")) {
          return true;
        }
        return false;
      }

      flush_reference_field(field) {
        /*
         * Empty the reference field and restore the search query
         */
        if (!(field.length > 0)) {
          return;
        }
        // restore the original search query
        this.reset_reference_field_query(field);
        // set emtpy value
        return this.set_reference_field(field, "");
      }

      reset_reference_field_query(field) {
        /*
         * Restores the catalog search query for the given reference field
         */
        if (!(field.length > 0)) {
          return;
        }
        return this.set_reference_field_query(field, {});
      }

      set_reference_field_query(field, query) {
        var search_query;
        /*
         * Set the catalog search query for the given reference field
         */
        if (!(field.length > 0)) {
          return;
        }
        // set the new query
        search_query = JSON.stringify(query);
        field.attr("data-search_query", search_query);
        return console.info(`----------> Set search query for field ${field.selector} -> ${search_query}`);
      }

      set_reference_field_records(field, records) {
        var $field, existing_records, new_records;
        /*
         * Set data-records to display the UID of a reference field
         */
        if (records == null) {
          records = {};
        }
        $field = $(field);
        existing_records = JSON.parse($field.attr("data-records") || '{}');
        new_records = Object.assign(existing_records, records);
        return $field.attr("data-records", JSON.stringify(new_records));
      }

      set_reference_field(field, uid) {
        var fieldname, textarea;
        /*
         * Set the UID of a reference field
         */
        if (!(field.length > 0)) {
          return;
        }
        fieldname = JSON.parse(field.data("name"));
        console.debug(`set_reference_field:: field=${fieldname} uid=${uid}`);
        textarea = field.find("textarea");
        return this.native_set_value(textarea[0], uid);
      }

      get_reference_field_value(field) {
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
      }

      set_template(arnum, template) {
        /*
         * Apply the template data to all fields of arnum
         */
        var field, me, template_field, template_uid, uid, value;
        me = this;
        // apply template only once
        template_field = $(`#Template-${arnum}`);
        template_uid = this.get_reference_field_value(template_field);
        if (arnum in this.applied_templates) {
          // Allow to remove fields set by the template
          if (this.applied_templates[arnum] === template_uid) {
            console.debug("Skipping already applied template");
            return;
          }
        }
        // remember the template for this ar
        this.applied_templates[arnum] = template_uid;
        // set the sample type
        field = $(`#SampleType-${arnum}`);
        value = this.get_reference_field_value(value);
        if (!value) {
          uid = template.sample_type_uid;
          this.set_reference_field(field, uid);
        }
        // set the sample point
        field = $(`#SamplePoint-${arnum}`);
        value = this.get_reference_field_value(value);
        if (!value) {
          uid = template.sample_point_uid;
          this.set_reference_field(field, uid);
        }
        // set the analysis profile
        field = $(`#Profiles-${arnum}`);
        value = this.get_reference_field_value(value);
        if (!value) {
          uid = template.analysis_profile_uid;
          this.set_reference_field(field, uid);
        }
        // set the remarks
        field = $(`#Remarks-${arnum}`);
        if (!field.val()) {
          field.text(template.remarks);
        }
        // set the composite checkbox
        field = $(`#Composite-${arnum}`);
        field.prop("checked", template.composite);
        // set the services
        $.each(template.service_uids, function(index, uid) {
          // select the service
          return me.set_service(arnum, uid, true);
        });
        // set the template field again
        // XXX how to avoid that setting the sample types flushes the template field?
        return this.set_reference_field(template_field, template_uid);
      }

      set_service(arnum, uid, checked) {
        var el, me, poc;
        /*
         * Select the checkbox of a service by UID
         */
        console.debug(`*** set_service::AR=${arnum} UID=${uid} checked=${checked}`);
        me = this;
        // get the service checkbox element
        el = $(`td[fieldname='Analyses-${arnum}'] #cb_${arnum}_${uid}`);
        // avoid unneccessary event triggers if the checkbox status is unchanged
        if (el.is(":checked") === checked) {
          return;
        }
        // select the checkbox
        el.prop("checked", checked);
        // get the point of capture of this element
        poc = el.closest("tr[poc]").attr("poc");
        // make the element visible if the categories are visible
        if (this.is_poc_expanded(poc)) {
          el.closest("tr").addClass("visible");
        }
        // show/hide the service conditions for this analysis
        me.set_service_conditions(el);
        // trigger event for price recalculation
        return $(this).trigger("services:changed");
      }

      get_service(uid) {
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
      }

      hide_all_service_info() {
        /*
         * hide all open service info boxes
         */
        var info;
        info = $("div.service-info");
        return info.hide();
      }

      is_poc_expanded(poc) {
        /*
         * Checks if the point of captures are visible
         */
        var el;
        el = $(`tr.service-listing-header[poc=${poc}]`);
        return el.hasClass("visible");
      }

      toggle_poc_categories(poc, toggle) {
        var categories, el, services, services_checked, toggle_buttons;
        /*
         * Toggle all categories within a point of capture (lab/service)
         * :param poc: the point of capture (lab/field)
         * :param toggle: services visible if true
         */
        if (toggle == null) {
          toggle = !this.is_poc_expanded(poc);
        }
        // get the element
        el = $(`tr[data-poc=${poc}]`);
        // all categories of this poc
        categories = $(`tr.category.${poc}`);
        // all services of this poc
        services = $(`tr.service.${poc}`);
        // all checked services
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
      }

      on_referencefield_value_changed(event) {
        /*
         * Generic event handler for when a reference field value changed
         */
        var $el, after_change, arnum, deselected, el, event_data, field_name, me, value;
        me = this;
        el = event.currentTarget;
        $el = $(el);
        field_name = $el.closest("tr[fieldname]").attr("fieldname");
        arnum = $el.closest("[arnum]").attr("arnum");
        // remember deselected UIDs
        if (event.type === "deselect") {
          value = event.detail.value;
          deselected = this.deselected_uids[field_name] || [];
          if (value && indexOf.call(deselected, value) < 0) {
            this.deselected_uids[field_name] = deselected.concat(value);
          }
        }
        if (field_name === "Template" || field_name === "Profiles") {
          return;
        }
        // These fields have it's own event handler
        console.debug(`°°° on_referencefield_value_changed: field_name=${field_name} arnum=${arnum} °°°`);
        // Flush depending fields
        me.flush_fields_for(field_name, arnum);
        // trigger custom event <field_name>:after_change
        event_data = {
          bubbles: true,
          detail: {
            value: el.value
          }
        };
        after_change = new CustomEvent(`${field_name}:after_change`, event_data);
        el.dispatchEvent(after_change);
        // trigger form:changed event
        return $(me).trigger("form:changed");
      }

      on_analysis_details_click(event) {
        /*
         * Eventhandler when the user clicked on the info icon of a service.
         */
        var $el, arnum, context, data, el, extra, info, profiles, record, template, templates, uid;
        el = event.currentTarget;
        $el = $(el);
        uid = $el.attr("uid");
        arnum = $el.closest("[arnum]").attr("arnum");
        console.debug(`°°° on_analysis_column::UID=${uid}°°°`);
        info = $("div.service-info", $el.parent());
        info.empty();
        data = info.data("data");
        // extra data to extend to the template context
        extra = {
          profiles: [],
          templates: []
        };
        // get the current snapshot record for this column
        record = this.records_snapshot[arnum];
        // inject profile info
        if (uid in record.service_to_profiles) {
          profiles = record.service_to_profiles[uid];
          $.each(profiles, function(index, uid) {
            return extra["profiles"].push(record.profiles_metadata[uid]);
          });
        }
        // inject template info
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
      }

      on_analysis_lock_button_click(event) {
        var $el, arnum, buttons, context, dialog, el, me, profile_uid, record, template_uid, uid;
        /*
         * Eventhandler when an Analysis Profile was removed.
         */
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
        // collect profiles
        if (uid in record.service_to_profiles) {
          profile_uid = record.service_to_profiles[uid];
          context["profiles"].push(record.profiles_metadata[profile_uid]);
        }
        // collect templates
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
      }

      on_analysis_template_selected(event) {
        /*
         * Eventhandler when an Analysis Template was selected.
         */
        console.debug("°°° on_analysis_template_selected °°°");
        // trigger form:changed event
        return $(this).trigger("form:changed");
      }

      on_analysis_template_removed(event) {
        var $el, arnum, el;
        /*
         * Eventhandler when an Analysis Template was removed.
         */
        console.debug("°°° on_analysis_template_removed °°°");
        el = event.currentTarget;
        $el = $(el);
        arnum = $el.closest("[arnum]").attr("arnum");
        this.applied_templates[arnum] = null;
        // trigger form:changed event
        return $(this).trigger("form:changed");
      }

      on_analysis_profile_selected(event) {
        /*
         * Eventhandler when an Analysis Profile was selected.
         */
        console.debug("°°° on_analysis_profile_selected °°°");
        // trigger form:changed event
        return $(this).trigger("form:changed");
      }

      on_analysis_profile_removed(event) {
        var $el, arnum, context, dialog, el, me, profile_metadata, profile_services, profile_uid, record;
        /*
         * Eventhandler when an Analysis Profile was removed.
         */
        console.debug("°°° on_analysis_profile_removed °°°");
        me = this;
        el = event.currentTarget;
        $el = $(el);
        arnum = $el.closest("[arnum]").attr("arnum");
        // The event detail tells us which profile UID has been deselected
        profile_uid = event.detail.value;
        record = this.records_snapshot[arnum];
        profile_metadata = record.profiles_metadata[profile_uid];
        profile_services = [];
        // prepare a list of services used by the profile with the given UID
        $.each(record.profile_to_services[profile_uid], function(index, uid) {
          return profile_services.push(record.service_metadata[uid]);
        });
        context = {};
        context["profile"] = profile_metadata;
        context["services"] = profile_services;
        me = this;
        dialog = this.template_dialog("profile-remove-template", context);
        dialog.on("yes", function() {
          // deselect the services
          $.each(profile_services, function(index, service) {
            return me.set_service(arnum, service.uid, false);
          });
          // trigger form:changed event
          return $(me).trigger("form:changed");
        });
        return dialog.on("no", function() {
          // trigger form:changed event
          return $(me).trigger("form:changed");
        });
      }

      on_analysis_checkbox_click(event) {
        /*
         * Eventhandler for Analysis Service Checkboxes.
         */
        var $el, checked, el, me, uid;
        me = this;
        el = event.currentTarget;
        checked = el.checked;
        $el = $(el);
        uid = $el.val();
        console.debug(`°°° on_analysis_click::UID=${uid} checked=${checked}°°°`);
        // show/hide the service conditions for this analysis
        me.set_service_conditions($el);
        // trigger form:changed event
        $(me).trigger("form:changed");
        // trigger event for price recalculation
        return $(me).trigger("services:changed");
      }

      on_service_listing_header_click(event) {
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
      }

      on_service_category_click(event) {
        var $btn, $el, category, expanded, poc, services, services_checked;
        /*
         * Eventhandler for analysis service category rows.
         * Toggles the visibility of all services within this category.
         * Selected services always stay visible.
         */
        event.preventDefault();
        $el = $(event.currentTarget);
        poc = $el.attr("poc");
        $btn = $(".service-category-toggle", $el);
        expanded = $el.hasClass("expanded");
        category = $el.data("category");
        services = $(`tr.${poc}.${category}`);
        services_checked = $("input[type=checkbox]:checked", services);
        console.debug(`°°° on_service_category_click: category=${category} °°°`);
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
      }

      on_copy_button_click(event) {
        var $el, $td1, $tr, ar_count, el, me, record_one, records, td1, tr, value;
        /*
         * Eventhandler for the field copy button per row.
         * Copies the value of the first field in this row to the remaining.
         * XXX Refactor
         */
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
        // the record data of the first AR
        record_one = this.records_snapshot[0];
        // reference widget
        if ($(td1).find('.ArchetypesReferenceWidget').length > 0) {
          console.debug("-> Copy reference field");
          el = $(td1).find(".ArchetypesReferenceWidget");
          records = JSON.parse(el.attr("data-records")) || {};
          value = me.get_reference_field_value(el);
          $.each((function() {
            var results = [];
            for (var i = 1; 1 <= ar_count ? i <= ar_count : i >= ar_count; 1 <= ar_count ? i++ : i--){ results.push(i); }
            return results;
          }).apply(this), function(arnum) {
            var _el, _field_name, _td;
            // skip the first (source) column
            if (!(arnum > 0)) {
              return;
            }
            // find the reference widget of the next column
            _td = $tr.find(`td[arnum=${arnum}]`);
            _el = $(_td).find(".ArchetypesReferenceWidget");
            // XXX: Needed?
            _field_name = _el.closest("tr[fieldname]").attr("fieldname");
            me.flush_fields_for(_field_name, arnum);
            // RectJS queryselect widget provides the JSON data of the selected
            // records in the `data-records` attribute.
            // This is needed because otherwise we would only see the raw UID value
            // (or another Ajax call would be needed.)
            me.set_reference_field_records(_el, records);
            // set the textarea (this triggers a select event on the field)
            return me.set_reference_field(_el, value);
          });
          // trigger form:changed event
          $(me).trigger("form:changed");
          return;
        }
        // Copy <input type="checkbox"> fields
        $td1.find("input[type=checkbox]").each(function(index, el) {
          var checked, is_service;
          console.debug("-> Copy checkbox field");
          $el = $(el);
          checked = $el.prop("checked");
          is_service = $el.hasClass("analysisservice-cb");
          // iterate over columns, starting from column 2
          $.each((function() {
            var results = [];
            for (var i = 1; 1 <= ar_count ? i <= ar_count : i >= ar_count; 1 <= ar_count ? i++ : i--){ results.push(i); }
            return results;
          }).apply(this), function(arnum) {
            var _el, _td, uid;
            // skip the first column
            if (!(arnum > 0)) {
              return;
            }
            _td = $tr.find(`td[arnum=${arnum}]`);
            _el = $(_td).find("input[type=checkbox]")[index];
            $(_el).prop("checked", checked);
            if (is_service) {
              // show/hide the service conditions for this analysis
              uid = $el.closest("[uid]").attr("uid");
              me.set_service_conditions($(_el));
              // copy the conditions for this analysis
              return me.copy_service_conditions(0, arnum, uid);
            }
          });
          // trigger event for price recalculation
          if (is_service) {
            return $(me).trigger("services:changed");
          }
        });
        // Copy <select> fields
        $td1.find("select").each(function(index, el) {
          console.debug("-> Copy select field");
          $el = $(el);
          value = $el.val();
          return $.each((function() {
            var results = [];
            for (var i = 1; 1 <= ar_count ? i <= ar_count : i >= ar_count; 1 <= ar_count ? i++ : i--){ results.push(i); }
            return results;
          }).apply(this), function(arnum) {
            var _el, _td;
            // skip the first column
            if (!(arnum > 0)) {
              return;
            }
            _td = $tr.find(`td[arnum=${arnum}]`);
            _el = $(_td).find("select")[index];
            return $(_el).val(value);
          });
        });
        // Copy <input type="text"> fields
        $td1.find("input[type=text]").each(function(index, el) {
          console.debug("-> Copy text field");
          $el = $(el);
          value = $el.val();
          return $.each((function() {
            var results = [];
            for (var i = 1; 1 <= ar_count ? i <= ar_count : i >= ar_count; 1 <= ar_count ? i++ : i--){ results.push(i); }
            return results;
          }).apply(this), function(arnum) {
            var _el, _td;
            // skip the first column
            if (!(arnum > 0)) {
              return;
            }
            _td = $tr.find(`td[arnum=${arnum}]`);
            _el = $(_td).find("input[type=text]")[index];
            return $(_el).val(value);
          });
        });
        // Copy <input type="number"> fields
        $td1.find("input[type=number]").each(function(index, el) {
          console.debug("-> Copy text field");
          $el = $(el);
          value = $el.val();
          return $.each((function() {
            var results = [];
            for (var i = 1; 1 <= ar_count ? i <= ar_count : i >= ar_count; 1 <= ar_count ? i++ : i--){ results.push(i); }
            return results;
          }).apply(this), function(arnum) {
            var _el, _td;
            // skip the first column
            if (!(arnum > 0)) {
              return;
            }
            _td = $tr.find(`td[arnum=${arnum}]`);
            _el = $(_td).find("input[type=number]")[index];
            return $(_el).val(value);
          });
        });
        // Copy <textarea> fields
        $td1.find("textarea").each(function(index, el) {
          console.debug("-> Copy textarea field");
          $el = $(el);
          value = $el.val();
          return $.each((function() {
            var results = [];
            for (var i = 1; 1 <= ar_count ? i <= ar_count : i >= ar_count; 1 <= ar_count ? i++ : i--){ results.push(i); }
            return results;
          }).apply(this), function(arnum) {
            var _el, _td;
            // skip the first column
            if (!(arnum > 0)) {
              return;
            }
            _td = $tr.find(`td[arnum=${arnum}]`);
            _el = $(_td).find("textarea")[index];
            return me.native_set_value(_el, value);
          });
        });
        // Copy <input type="radio"> fields
        $td1.find("input[type=radio]").each(function(index, el) {
          var checked;
          console.debug("-> Copy radio field");
          $el = $(el);
          checked = $(el).is(":checked");
          return $.each((function() {
            var results = [];
            for (var i = 1; 1 <= ar_count ? i <= ar_count : i >= ar_count; 1 <= ar_count ? i++ : i--){ results.push(i); }
            return results;
          }).apply(this), function(arnum) {
            var _el, _td;
            // skip the first column
            if (!(arnum > 0)) {
              return;
            }
            _td = $tr.find(`td[arnum=${arnum}]`);
            _el = $(_td).find("input[type=radio]")[index];
            return $(_el).prop("checked", checked);
          });
        });
        // Copy <input type="date"> fields
        $td1.find("input[type='date']").each(function(index, el) {
          console.debug("-> Copy date field");
          $el = $(el);
          value = $el.val();
          return $.each((function() {
            var results = [];
            for (var i = 1; 1 <= ar_count ? i <= ar_count : i >= ar_count; 1 <= ar_count ? i++ : i--){ results.push(i); }
            return results;
          }).apply(this), function(arnum) {
            var _el, _td;
            // skip the first column
            if (!(arnum > 0)) {
              return;
            }
            _td = $tr.find(`td[arnum=${arnum}]`);
            _el = $(_td).find("input[type='date']")[index];
            return $(_el).val(value);
          });
        });
        // Copy <input type="time"> fields
        $td1.find("input[type='time']").each(function(index, el) {
          console.debug("-> Copy time field");
          $el = $(el);
          value = $el.val();
          return $.each((function() {
            var results = [];
            for (var i = 1; 1 <= ar_count ? i <= ar_count : i >= ar_count; 1 <= ar_count ? i++ : i--){ results.push(i); }
            return results;
          }).apply(this), function(arnum) {
            var _el, _td;
            // skip the first column
            if (!(arnum > 0)) {
              return;
            }
            _td = $tr.find(`td[arnum=${arnum}]`);
            _el = $(_td).find("input[type='time']")[index];
            return $(_el).val(value);
          });
        });
        // Copy <input type="hidden"> fields
        $td1.find("input[type='hidden']").each(function(index, el) {
          console.debug("-> Copy hidden field");
          $el = $(el);
          value = $el.val();
          return $.each((function() {
            var results = [];
            for (var i = 1; 1 <= ar_count ? i <= ar_count : i >= ar_count; 1 <= ar_count ? i++ : i--){ results.push(i); }
            return results;
          }).apply(this), function(arnum) {
            var _el, _td;
            // skip the first column
            if (!(arnum > 0)) {
              return;
            }
            _td = $tr.find(`td[arnum=${arnum}]`);
            _el = $(_td).find("input[type='hidden']")[index];
            return $(_el).val(value);
          });
        });
        // trigger form:changed event
        return $(me).trigger("form:changed");
      }

      native_set_value(input, value) {
        var event, setter;
        // https://stackoverflow.com/questions/23892547/what-is-the-best-way-to-trigger-onchange-event-in-react-js
        // TL;DR: React library overrides input value setter
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
      }

      ajax_post_form(endpoint, options = {}) {
        var ajax_options, base_url, form, form_data, me, url;
        /*
         * Ajax POST the form data to the given endpoint
         */
        console.debug(`°°° ajax_post_form::Endpoint=${endpoint} °°°`);
        // calculate the right form URL
        base_url = this.get_base_url();
        url = `${base_url}/ajax_ar_add/${endpoint}`;
        console.debug(`Ajax POST to url ${url}`);
        // extract the form data
        form = $("#analysisrequest_add_form");
        // form.serialize does not include file attachments
        // form_data = form.serialize()
        form_data = new FormData(form[0]);
        // jQuery Ajax options
        ajax_options = {
          url: url,
          type: 'POST',
          data: form_data,
          context: this,
          cache: false,
          dataType: 'json', // data type we expect from the server
          processData: false,
          contentType: false,
          // contentType: 'application/x-www-form-urlencoded; charset=UTF-8'
          timeout: 600000 // 10 minutes timeout
        };
        
        // Update Options
        $.extend(ajax_options, options);
        /* Execute the request */
        // Notify Ajax start
        me = this;
        $(me).trigger("ajax:start");
        return $.ajax(ajax_options).always(function(data) {
          // Always notify Ajax end
          return $(me).trigger("ajax:end");
        }).fail(function(request, status, error) {
          var msg;
          msg = _t(`Sorry, an error occured: ${status}`);
          window.bika.lims.portalMessage(msg);
          return window.scroll(0, 0);
        });
      }

      on_ajax_start() {
        var save_and_copy_button, save_button;
        /*
         * Ajax request started
         */
        console.debug("°°° on_ajax_start °°°");
        // deactivate the save button
        save_button = $("input[name=save_button]");
        save_button.prop({
          "disabled": true
        });
        save_button[0].value = _t("Loading ...");
        // deactivate the save and copy button
        save_and_copy_button = $("input[name=save_and_copy_button]");
        return save_and_copy_button.prop({
          "disabled": true
        });
      }

      on_ajax_end() {
        var save_and_copy_button, save_button;
        /*
         * Ajax request finished
         */
        console.debug("°°° on_ajax_end °°°");
        // reactivate the save button
        save_button = $("input[name=save_button]");
        save_button.prop({
          "disabled": false
        });
        save_button[0].value = _t("Save");
        // reactivate the save and copy button
        save_and_copy_button = $("input[name=save_and_copy_button]");
        return save_and_copy_button.prop({
          "disabled": false
        });
      }

      on_cancel(event, callback) {
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
      }

      on_form_submit(event, callback) {
        var action, action_input, base_url, btn, me, portal_url;
        /*
         * Eventhandler for the form submit button.
         * Extracts and submits all form data asynchronous.
         */
        console.debug("°°° on_form_submit °°°");
        event.preventDefault();
        me = this;
        // The clicked submit button is not part of the form data, therefore,
        // we pass the name of the button through a hidden field
        btn = event.currentTarget;
        action = "save";
        if (btn.name === "save_and_copy_button") {
          action = "save_and_copy";
        }
        action_input = document.querySelector("input[name='submit_action']");
        action_input.value = action;
        // get the right base url
        base_url = me.get_base_url();
        // the poral url
        portal_url = me.get_portal_url();
        // remove all errors
        $("div.error").removeClass("error");
        $("div.fieldErrorBox").text("");
        // Ajax POST to the submit endpoint
        return this.ajax_post_form("submit").done(function(data) {
          var dialog, errorbox, field, fieldname, message, msg, parent;
          /*
           * data contains the following useful keys:
           * - errors: any errors which prevented the AR from being created
           *   these are displayed immediately and no further ation is taken
           * - destination: the URL to which we should redirect on success.
           *   This includes GET params for printing labels, so that we do not
           *   have to care about this here.
           */
          if (data['errors']) {
            msg = data.errors.message;
            if (msg !== "") {
              msg = _t(`Sorry, an error occured 🙈<p class='code'>${msg}</p>`);
            }
            for (fieldname in data.errors.fielderrors) {
              field = $(`#${fieldname}`);
              parent = field.parent("div.field");
              if (field && parent) {
                parent.toggleClass("error");
                errorbox = parent.children("div.fieldErrorBox");
                message = data.errors.fielderrors[fieldname];
                errorbox.text(message);
                msg += `${message}<br/>`;
              }
            }
            window.bika.lims.portalMessage(msg);
            return window.scroll(0, 0);
          } else if (data['confirmation']) {
            dialog = me.template_dialog("confirm-template", data.confirmation);
            dialog.on("yes", function() {
              // Re-submit
              $("input[name=confirmed]").val("1");
              return $("input[name=save_button]").trigger("click");
            });
            return dialog.on("no", function() {
              var destination;
              // Don't submit and redirect user if required
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
      }

      init_file_fields() {
        var me;
        me = this;
        return $('tr[fieldname] input[type="file"]').each(function(index, element) {
          var add_btn, add_btn_src, file_field, file_field_div;
          // Wrap the initial field into a div
          file_field = $(element);
          file_field.wrap("<div class='field'/>");
          file_field_div = file_field.parent();
          // Create and add an ADD Button on the fly
          add_btn_src = `${window.portal_url}/senaite_theme/icon/plus`;
          add_btn = $(`<img class='addbtn' width='16' style='cursor:pointer;' src='${add_btn_src}' />`);
          // bind ADD event handler
          add_btn.on("click", element, function(event) {
            return me.file_addbtn_click(event, element);
          });
          // Attach the Button into the same div container
          return file_field_div.append(add_btn);
        });
      }

      file_addbtn_click(event, element) {
        var arnum, counter, del_btn, del_btn_src, existing_file_field_names, existing_file_fields, file_field, file_field_div, holding_div, name, newfieldname;
        // Clone the file field and wrap it into a div
        file_field = $(element).clone();
        file_field.val("");
        file_field.wrap("<div class='field'/>");
        file_field_div = file_field.parent();
        [name, arnum] = $(element).attr("name").split("-");
        // Get all existing input fields and their names
        holding_div = $(element).parent().parent();
        existing_file_fields = holding_div.find("input[type='file']");
        existing_file_field_names = existing_file_fields.map(function(index, element) {
          return $(element).attr("name");
        });
        // Generate a new name for the field and ensure it is not taken by another field already
        counter = 0;
        newfieldname = $(element).attr("name");
        while (indexOf.call(existing_file_field_names, newfieldname) >= 0) {
          newfieldname = `${name}_${counter}-${arnum}`;
          counter++;
        }
        // set the new id, name
        file_field.attr("name", newfieldname);
        file_field.attr("id", newfieldname);
        // Create and add an DELETE Button on the fly
        del_btn_src = `${window.portal_url}/senaite_theme/icon/delete`;
        del_btn = $(`<img class='delbtn' width='16' style='cursor:pointer;' src='${del_btn_src}' />`);
        // Bind an DELETE event handler
        del_btn.on("click", element, function(event) {
          return $(this).parent().remove();
        });
        // Attach the Button into the same div container
        file_field_div.append(del_btn);
        // Attach the new field to the outer div of the passed file field
        return $(element).parent().parent().append(file_field_div);
      }

      set_service_conditions(el) {
        var arnum, base_info, checked, conditions, context, data, parent, template, uid;
        /*
         * Shows or hides the service conditions input elements for the service
         * bound to the checkbox element passed in
         */
        // Check whether the checkbox is selected or not
        checked = el.prop("checked");
        // Get the uid of the analysis and the column number
        parent = el.closest("td[uid][arnum]");
        uid = parent.attr("uid");
        arnum = parent.attr("arnum");
        // Get the div where service conditions are rendered
        conditions = $("div.service-conditions", parent);
        conditions.empty();
        // If the service is unchecked, remove the conditions form
        if (!checked) {
          conditions.hide();
          return;
        }
        // Check if this service requires conditions
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
      }

      copy_service_conditions(from, to, uid) {
        var me, source;
        /*
         * Copies the service conditions values from those set for the service with
         * the specified uid and arnum_from column to the same analysis from the
         * arnum_to column
         */
        console.debug(`*** copy_service_conditions::from=${from} to=${to} UID=${uid}`);
        me = this;
        // Copy the values from all input fields to destination by name
        source = `td[fieldname='Analyses-${from}'] div[id='${uid}-conditions'] input[name='ServiceConditions-${from}.value:records']`;
        return $(source).each(function(idx, el) {
          var $el, dest, name, subfield;
          // Extract the information from the field to look for
          $el = $(el);
          name = $el.attr("name");
          subfield = $el.closest("[data-subfield]").attr("data-subfield");
          console.debug(`-> Copy service condition: ${subfield}`);
          // Set the value
          dest = $(`td[fieldname='Analyses-${to}'] tr[data-subfield='${subfield}'] input[name='ServiceConditions-${to}.value:records']`);
          return dest.val($el.val());
        });
      }

      init_service_conditions() {
        var me, services;
        /*
         * Updates the visibility of the conditions for the selected services
         */
        console.debug("init_service_conditions");
        me = this;
        // Find out all selected services checkboxes
        services = $("input[type=checkbox].analysisservice-cb:checked");
        return $(services).each(function(idx, el) {
          var $el;
          $el = $(el);
          return me.set_service_conditions($el);
        });
      }

    };

    typeIsArray = Array.isArray || function(value) {
      /*
       * Returns if the given value is an array
       * Taken from: https://coffeescript-cookbook.github.io/chapters/arrays/check-type-is-array
       */
      return {}.toString.call(value) === '[object Array]';
    };

    return AnalysisRequestAdd;

  }).call(this);

}).call(this);
