(function() {
  /* Please use this command to compile this file into the parent `js` directory:
      coffee --no-header -w -o ../ -c bika.lims.analysisrequest.add.coffee
  */
  var hasProp = {}.hasOwnProperty,
    indexOf = [].indexOf;

  window.AnalysisRequestAdd = class AnalysisRequestAdd {
    constructor() {
      this.load = this.load.bind(this);
      /* METHODS */
      this.bind_eventhandler = this.bind_eventhandler.bind(this);
      this.debounce = this.debounce.bind(this);
      this.template_dialog = this.template_dialog.bind(this);
      this.render_template = this.render_template.bind(this);
      this.get_global_settings = this.get_global_settings.bind(this);
      this.recalculate_records = this.recalculate_records.bind(this);
      this.recalculate_prices = this.recalculate_prices.bind(this);
      this.update_form = this.update_form.bind(this);
      this.get_portal_url = this.get_portal_url.bind(this);
      this.get_base_url = this.get_base_url.bind(this);
      this.get_authenticator = this.get_authenticator.bind(this);
      this.get_form = this.get_form.bind(this);
      this.get_fields = this.get_fields.bind(this);
      this.get_field_by_id = this.get_field_by_id.bind(this);
      this.set_reference_field_query = this.set_reference_field_query.bind(this);
      this.set_reference_field = this.set_reference_field.bind(this);
      this.set_client = this.set_client.bind(this);
      this.set_contact = this.set_contact.bind(this);
      this.set_sample = this.set_sample.bind(this);
      this.set_sampletype = this.set_sampletype.bind(this);
      this.set_template = this.set_template.bind(this);
      this.set_service = this.set_service.bind(this);
      this.set_service_spec = this.set_service_spec.bind(this);
      this.get_service = this.get_service.bind(this);
      this.hide_all_service_info = this.hide_all_service_info.bind(this);
      /* EVENT HANDLER */
      this.on_client_changed = this.on_client_changed.bind(this);
      this.on_contact_changed = this.on_contact_changed.bind(this);
      this.on_analysis_specification_changed = this.on_analysis_specification_changed.bind(this);
      this.on_analysis_details_click = this.on_analysis_details_click.bind(this);
      this.on_analysis_lock_button_click = this.on_analysis_lock_button_click.bind(this);
      this.on_sample_changed = this.on_sample_changed.bind(this);
      this.on_sampletype_changed = this.on_sampletype_changed.bind(this);
      this.on_specification_changed = this.on_specification_changed.bind(this);
      this.on_analysis_template_changed = this.on_analysis_template_changed.bind(this);
      this.on_analysis_profile_selected = this.on_analysis_profile_selected.bind(this);
      // Note: Context of callback bound to this object
      this.on_analysis_profile_removed = this.on_analysis_profile_removed.bind(this);
      this.on_analysis_checkbox_click = this.on_analysis_checkbox_click.bind(this);
      this.on_service_listing_header_click = this.on_service_listing_header_click.bind(this);
      this.on_service_category_click = this.on_service_category_click.bind(this);
      this.on_copy_button_click = this.on_copy_button_click.bind(this);
      // Note: Context of callback bound to this object
      this.ajax_post_form = this.ajax_post_form.bind(this);
      this.on_ajax_start = this.on_ajax_start.bind(this);
      this.on_ajax_end = this.on_ajax_end.bind(this);
      // Note: Context of callback bound to this object
      this.on_form_submit = this.on_form_submit.bind(this);
      this.init_file_fields = this.init_file_fields.bind(this);
    }

    load() {
      console.debug("AnalysisRequestAdd::load");
      // load translations
      jarn.i18n.loadCatalog('senaite.core');
      this._ = window.jarn.i18n.MessageFactory("senaite.core");
      // disable browser autocomplete
      $('input[type=text]').prop('autocomplete', 'off');
      // storage for global Bika settings
      this.global_settings = {};
      // services data snapshot from recalculate_records
      // returns a mapping of arnum -> services data
      this.records_snapshot = {};
      // brain for already applied templates
      this.applied_templates = {};
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
      // recalculate records on load (needed for AR copies)
      return this.recalculate_records();
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
      // Save button clicked
      $("body").on("click", "[name='save_button']", this.on_form_submit);
      // Composite Checkbox clicked
      $("body").on("click", "tr[fieldname=Composite] input[type='checkbox']", this.recalculate_records);
      // InvoiceExclude Checkbox clicked
      $("body").on("click", "tr[fieldname=InvoiceExclude] input[type='checkbox']", this.recalculate_records);
      // Analysis Checkbox clicked
      $("body").on("click", "tr[fieldname=Analyses] input[type='checkbox']", this.on_analysis_checkbox_click);
      // Client changed
      $("body").on("selected change", "tr[fieldname=Client] input[type='text']", this.on_client_changed);
      // Contact changed
      $("body").on("selected change", "tr[fieldname=Contact] input[type='text']", this.on_contact_changed);
      // Analysis Specification changed
      $("body").on("change", "input.min", this.on_analysis_specification_changed);
      $("body").on("change", "input.max", this.on_analysis_specification_changed);
      $("body").on("change", "input.warn_min", this.on_analysis_specification_changed);
      $("body").on("change", "input.warn_max", this.on_analysis_specification_changed);
      // Analysis lock button clicked
      $("body").on("click", ".service-lockbtn", this.on_analysis_lock_button_click);
      // Analysis info button clicked
      $("body").on("click", ".service-infobtn", this.on_analysis_details_click);
      // Sample changed
      $("body").on("selected change", "tr[fieldname=PrimaryAnalysisRequest] input[type='text']", this.on_sample_changed);
      // SampleType changed
      $("body").on("selected change", "tr[fieldname=SampleType] input[type='text']", this.on_sampletype_changed);
      // Specification changed
      $("body").on("selected change", "tr[fieldname=Specification] input[type='text']", this.on_specification_changed);
      // Analysis Template changed
      $("body").on("selected change", "tr[fieldname=Template] input[type='text']", this.on_analysis_template_changed);
      // Analysis Profile selected
      $("body").on("selected", "tr[fieldname=Profiles] input[type='text']", this.on_analysis_profile_selected);
      // Analysis Profile deselected
      $("body").on("click", "tr[fieldname=Profiles] img.deletebtn", this.on_analysis_profile_removed);
      // Copy button clicked
      $("body").on("click", "img.copybutton", this.on_copy_button_click);
      /* internal events */
      // handle value changes in the form
      $(this).on("form:changed", this.debounce(this.recalculate_records, 500));
      // recalculate prices after data changed
      $(this).on("data:updated", this.debounce(this.recalculate_prices, 3000));
      // update form from records after the data changed
      $(this).on("data:updated", this.debounce(this.update_form, 300));
      // hide open service info after data changed
      $(this).on("data:updated", this.debounce(this.hide_all_service_info, 300));
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
        return timeout = setTimeout(delayed, threshold || 100);
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
        buttons[this._("Yes")] = function() {
          // trigger 'yes' event
          $(this).trigger("yes");
          return $(this).dialog("close");
        };
        buttons[this._("No")] = function() {
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
       * Submit all form values to the server to recalculate the records
       */
      return this.ajax_post_form("get_global_settings").done(function(settings) {
        console.debug("Global Settings:", settings);
        // remember the global settings
        this.global_settings = settings;
        // trigger event for whom it might concern
        return $(this).trigger("settings:updated", settings);
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
       */
      console.debug("*** update_form ***");
      me = this;
      // initially hide all lock icons
      $(".service-lockbtn").hide();
      // set all values for one record (a single column in the AR Add form)
      return $.each(records, function(arnum, record) {
        // set client
        $.each(record.client_metadata, function(uid, client) {
          return me.set_client(arnum, client);
        });
        // set contact
        $.each(record.contact_metadata, function(uid, contact) {
          return me.set_contact(arnum, contact);
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
          // service is part of the template
          // if uid of record.service_to_templates
          //   lock.show()

          // select the service
          return me.set_service(arnum, uid, true);
        });
        // set template
        $.each(record.template_metadata, function(uid, template) {
          return me.set_template(arnum, template);
        });
        // set specification
        $.each(record.specification_metadata, function(uid, spec) {
          return $.each(spec.specifications, function(uid, service_spec) {
            return me.set_service_spec(arnum, uid, service_spec);
          });
        });
        // set sample
        $.each(record.sample_metadata, function(uid, sample) {
          return me.set_sample(arnum, sample);
        });
        // set sampletype
        $.each(record.sampletype_metadata, function(uid, sampletype) {
          return me.set_sampletype(arnum, sampletype);
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

    get_authenticator() {
      /*
       * Get the authenticator value
       */
      return $("input[name='_authenticator']").val();
    }

    get_form() {
      /*
       * Return the form element
       */
      return $("#analysisrequest_add_form");
    }

    get_fields(arnum) {
      /*
       * Get all fields of the form
       */
      var fields, fields_selector, form;
      form = this.get_form();
      fields_selector = "tr[fieldname] td[arnum] input";
      if (arnum != null) {
        fields_selector = `tr[fieldname] td[arnum=${arnum}] input`;
      }
      fields = $(fields_selector, form);
      return fields;
    }

    get_field_by_id(id, arnum) {
      var field_id, name, suffix;
      /*
       * Query the field by id
       */
      // split the fieldname from the suffix
      [name, suffix] = id.split("_");
      // append the arnum
      field_id = `${name}-${arnum}`;
      // append the suffix if it is there
      if (suffix != null) {
        field_id = `${field_id}_${suffix}`;
      }
      // prepend a hash if it is not there
      if (!id.startsWith("#")) {
        field_id = `#${field_id}`;
      }
      console.debug(`get_field_by_id: $(${field_id})`);
      // query the field
      return $(field_id);
    }

    flush_reference_field(field) {
      /*
       * Empty the reference field
       */
      var catalog_name;
      catalog_name = field.attr("catalog_name");
      if (!catalog_name) {
        return;
      }
      // flush values
      field.val("");
      $("input[type=hidden]", field.parent()).val("");
      return $(".multiValued-listing", field.parent()).empty();
    }

    set_reference_field_query(field, query, type = "base_query") {
      /*
       * Set the catalog search query for the given reference field
       * XXX This is lame! The field should provide a proper API.
       */
      var catalog_name, catalog_query, new_query, options, url;
      catalog_name = field.attr("catalog_name");
      if (!catalog_name) {
        return;
      }
      // get the combogrid options
      options = $.parseJSON(field.attr("combogrid_options"));
      // prepare the new query url
      url = this.get_base_url();
      url += `/${options.url}`;
      url += `?_authenticator=${this.get_authenticator()}`;
      url += `&catalog_name=${catalog_name}`;
      url += `&colModel=${$.toJSON(options.colModel)}`;
      url += `&search_fields=${$.toJSON(options.search_fields)}`;
      url += `&discard_empty=${$.toJSON(options.discard_empty)}`;
      url += `&minLength=${$.toJSON(options.minLength)}`;
      // get the current query (either "base_query" or "search_query" attribute)
      catalog_query = $.parseJSON(field.attr(type));
      // update this query with the passed in query
      $.extend(catalog_query, query);
      new_query = $.toJSON(catalog_query);
      console.debug(`set_reference_field_query: query=${new_query}`);
      if (type === 'base_query') {
        url += `&base_query=${new_query}`;
        url += `&search_query=${field.attr('search_query')}`;
      } else {
        url += `&base_query=${field.attr('base_query')}`;
        url += `&search_query=${new_query}`;
      }
      options.url = url;
      options.force_all = "false";
      field.combogrid(options);
      return field.attr("search_query", "{}");
    }

    set_reference_field(field, uid, title) {
      /*
       * Set the value and the uid of a reference field
       * XXX This is lame! The field should handle this on data change.
       */
      var $field, $parent, div, existing_uids, fieldname, img, me, mvl, portal_url, src, uids, uids_field;
      me = this;
      $field = $(field);
      if (!$field.length) {
        console.debug(`field ${field} does not exist, skip set_reference_field`);
        return;
      }
      $parent = field.closest("div.field");
      fieldname = field.attr("name");
      console.debug(`set_reference_field:: field=${fieldname} uid=${uid} title=${title}`);
      uids_field = $("input[type=hidden]", $parent);
      existing_uids = uids_field.val();
      // uid is already selected
      if (existing_uids.indexOf(uid) >= 0) {
        return;
      }
      // nothing in the field -> uid is the first entry
      if (existing_uids.length === 0) {
        uids_field.val(uid);
      } else {
        // append to the list
        uids = uids_field.val().split(",");
        uids.push(uid);
        uids_field.val(uids.join(","));
      }
      // set the title as the value
      $field.val(title);
      // handle multivalued reference fields
      mvl = $(".multiValued-listing", $parent);
      if (mvl.length > 0) {
        portal_url = this.get_portal_url();
        src = `${portal_url}/++resource++bika.lims.images/delete.png`;
        img = $("<img class='deletebtn'/>");
        img.attr("src", src);
        img.attr("data-contact-title", title);
        img.attr("fieldname", fieldname);
        img.attr("uid", uid);
        div = $("<div class='reference_multi_item'/>");
        div.attr("uid", uid);
        div.append(img);
        div.append(title);
        mvl.append(div);
        return $field.val("");
      }
    }

    set_client(arnum, client) {
      var contact_title, contact_uid, field, query;
      /*
       * Filter Contacts
       * Filter CCContacts
       * Filter InvoiceContacts
       * Filter SamplePoints
       * Filter ARTemplates
       * Filter Specification
       * Filter SamplingRound
       */
      // filter Contacts
      field = $(`#Contact-${arnum}`);
      query = client.filter_queries.contact;
      this.set_reference_field_query(field, query);
      // handle default contact for /analysisrequests listing
      // https://github.com/senaite/senaite.core/issues/705
      if (document.URL.indexOf("analysisrequests") > -1) {
        contact_title = client.default_contact.title;
        contact_uid = client.default_contact.uid;
        if (contact_title && contact_uid) {
          this.set_reference_field(field, contact_uid, contact_title);
        }
      }
      // filter CCContacts
      field = $(`#CCContact-${arnum}`);
      query = client.filter_queries.cc_contact;
      this.set_reference_field_query(field, query);
      // filter InvoiceContact
      // XXX Where is this field?
      field = $(`#InvoiceContact-${arnum}`);
      query = client.filter_queries.invoice_contact;
      this.set_reference_field_query(field, query);
      // filter Sample Points
      field = $(`#SamplePoint-${arnum}`);
      query = client.filter_queries.samplepoint;
      this.set_reference_field_query(field, query);
      // filter AR Templates
      field = $(`#Template-${arnum}`);
      query = client.filter_queries.artemplates;
      this.set_reference_field_query(field, query);
      // filter Analysis Profiles
      field = $(`#Profiles-${arnum}`);
      query = client.filter_queries.analysisprofiles;
      this.set_reference_field_query(field, query);
      // filter Analysis Specs
      field = $(`#Specification-${arnum}`);
      query = client.filter_queries.analysisspecs;
      this.set_reference_field_query(field, query);
      // filter Samplinground
      field = $(`#SamplingRound-${arnum}`);
      query = client.filter_queries.samplinground;
      this.set_reference_field_query(field, query);
      // filter Sample
      field = $(`#PrimaryAnalysisRequest-${arnum}`);
      query = client.filter_queries.sample;
      return this.set_reference_field_query(field, query);
    }

    set_contact(arnum, contact) {
      /*
       * Set CC Contacts
       */
      var field, me;
      me = this;
      field = $(`#CCContact-${arnum}`);
      return $.each(contact.cccontacts, function(uid, cccontact) {
        var fullname;
        fullname = cccontact.fullname;
        return me.set_reference_field(field, uid, fullname);
      });
    }

    set_sample(arnum, sample) {
      var contact, field, fullname, title, uid, value;
      /*
       * Apply the sample data to all fields of arnum
       */
      // set the client
      field = $(`#Client-${arnum}`);
      uid = sample.client_uid;
      title = sample.client_title;
      this.set_reference_field(field, uid, title);
      // set the client contact
      field = $(`#Contact-${arnum}`);
      contact = sample.contact;
      uid = contact.uid;
      fullname = contact.fullname;
      this.set_reference_field(field, uid, fullname);
      this.set_contact(arnum, contact);
      // set the sampling date
      field = $(`#SamplingDate-${arnum}`);
      value = sample.sampling_date;
      field.val(value);
      // set the date sampled
      field = $(`#DateSampled-${arnum}`);
      value = sample.date_sampled;
      field.val(value);
      // set the sample type (required)
      field = $(`#SampleType-${arnum}`);
      uid = sample.sample_type_uid;
      title = sample.sample_type_title;
      this.set_reference_field(field, uid, title);
      // set environmental conditions
      field = $(`#EnvironmentalConditions-${arnum}`);
      value = sample.environmental_conditions;
      field.val(value);
      // set client sample ID
      field = $(`#ClientSampleID-${arnum}`);
      value = sample.client_sample_id;
      field.val(value);
      // set client reference
      field = $(`#ClientReference-${arnum}`);
      value = sample.client_reference;
      field.val(value);
      // set the client order number
      field = $(`#ClientOrderNumber-${arnum}`);
      value = sample.client_order_number;
      field.val(value);
      // set composite
      field = $(`#Composite-${arnum}`);
      field.prop("checked", sample.composite);
      // set the sample condition
      field = $(`#SampleCondition-${arnum}`);
      uid = sample.sample_condition_uid;
      title = sample.sample_condition_title;
      this.set_reference_field(field, uid, title);
      // set the sample point
      field = $(`#SamplePoint-${arnum}`);
      uid = sample.sample_point_uid;
      title = sample.sample_point_title;
      this.set_reference_field(field, uid, title);
      // set the storage location
      field = $(`#StorageLocation-${arnum}`);
      uid = sample.storage_location_uid;
      title = sample.storage_location_title;
      this.set_reference_field(field, uid, title);
      // set the default container type
      field = $(`#DefaultContainerType-${arnum}`);
      uid = sample.container_type_uid;
      title = sample.container_type_title;
      this.set_reference_field(field, uid, title);
      // set the sampling deviation
      field = $(`#SamplingDeviation-${arnum}`);
      uid = sample.sampling_deviation_uid;
      title = sample.sampling_deviation_title;
      return this.set_reference_field(field, uid, title);
    }

    set_sampletype(arnum, sampletype) {
      var field, query, title, uid;
      /*
       * Recalculate partitions
       * Filter Sample Points
       */
      // restrict the sample points
      field = $(`#SamplePoint-${arnum}`);
      query = sampletype.filter_queries.samplepoint;
      this.set_reference_field_query(field, query);
      // set the default container
      field = $(`#DefaultContainerType-${arnum}`);
      // apply default container if the field is empty
      if (!field.val()) {
        uid = sampletype.container_type_uid;
        title = sampletype.container_type_title;
        this.flush_reference_field(field);
        this.set_reference_field(field, uid, title);
      }
      // restrict the specifications
      field = $(`#Specification-${arnum}`);
      query = sampletype.filter_queries.specification;
      return this.set_reference_field_query(field, query);
    }

    set_template(arnum, template) {
      /*
       * Apply the template data to all fields of arnum
       */
      var field, me, template_uid, title, uid;
      me = this;
      // apply template only once
      field = $(`#Template-${arnum}`);
      uid = field.attr("uid");
      template_uid = template.uid;
      if (arnum in this.applied_templates) {
        if (this.applied_templates[arnum] === template_uid) {
          console.debug("Skipping already applied template");
          return;
        }
      }
      // remember the template for this ar
      this.applied_templates[arnum] = template_uid;
      // set the sample type
      field = $(`#SampleType-${arnum}`);
      uid = template.sample_type_uid;
      title = template.sample_type_title;
      this.flush_reference_field(field);
      this.set_reference_field(field, uid, title);
      // set the sample point
      field = $(`#SamplePoint-${arnum}`);
      uid = template.sample_point_uid;
      title = template.sample_point_title;
      this.flush_reference_field(field);
      this.set_reference_field(field, uid, title);
      // set the analysis profile
      field = $(`#Profiles-${arnum}`);
      uid = template.analysis_profile_uid;
      title = template.analysis_profile_title;
      this.flush_reference_field(field);
      this.set_reference_field(field, uid, title);
      // set the remarks
      field = $(`#Remarks-${arnum}`);
      field.text(template.remarks);
      // set the composite checkbox
      field = $(`#Composite-${arnum}`);
      field.prop("checked", template.composite);
      // set the services
      return $.each(template.service_uids, function(index, uid) {
        // select the service
        return me.set_service(arnum, uid, true);
      });
    }

    set_service(arnum, uid, checked) {
      var el, poc;
      /*
       * Select the checkbox of a service by UID
       */
      console.debug(`*** set_service::AR=${arnum} UID=${uid} checked=${checked}`);
      // get the service checkbox element
      el = $(`td[fieldname='Analyses-${arnum}'] #cb_${uid}`);
      // select the checkbox
      el.prop("checked", checked);
      // get the point of capture of this element
      poc = el.closest("tr[poc]").attr("poc");
      // make the element visible if the categories are visible
      if (this.is_poc_expanded(poc)) {
        return el.closest("tr").addClass("visible");
      }
    }

    set_service_spec(arnum, uid, spec) {
      var el, max, min, warn_max, warn_min;
      /*
       * Set the specification of the service
       */
      console.debug(`*** set_service_spec::AR=${arnum} UID=${uid} spec=`, spec);
      // get the service specifications
      el = $(`div#${uid}-${arnum}-specifications`);
      min = $(".min", el);
      max = $(".max", el);
      warn_min = $(".warn_min", el);
      warn_max = $(".warn_max", el);
      min.val(spec.min);
      max.val(spec.max);
      warn_min.val(spec.warn_min);
      return warn_max.val(spec.warn_max);
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

    on_client_changed(event) {
      /*
       * Eventhandler when the client changed (happens on Batches)
       */
      var $el, arnum, el, field_ids, me, uid;
      me = this;
      el = event.currentTarget;
      $el = $(el);
      uid = $el.attr("uid");
      arnum = $el.closest("[arnum]").attr("arnum");
      console.debug(`°°° on_client_changed: arnum=${arnum} °°°`);
      // Flush client depending fields
      field_ids = ["Contact", "CCContact", "InvoiceContact", "SamplePoint", "Template", "Profiles", "PrimaryAnalysisRequest", "Specification"];
      $.each(field_ids, function(index, id) {
        var field;
        field = me.get_field_by_id(id, arnum);
        return me.flush_reference_field(field);
      });
      // trigger form:changed event
      return $(me).trigger("form:changed");
    }

    on_contact_changed(event) {
      /*
       * Eventhandler when the contact changed
       */
      var $el, arnum, el, field_ids, me, uid;
      me = this;
      el = event.currentTarget;
      $el = $(el);
      uid = $el.attr("uid");
      arnum = $el.closest("[arnum]").attr("arnum");
      console.debug(`°°° on_contact_changed: arnum=${arnum} °°°`);
      // Flush client depending fields
      field_ids = ["CCContact"];
      $.each(field_ids, function(index, id) {
        var field;
        field = me.get_field_by_id(id, arnum);
        return me.flush_reference_field(field);
      });
      // trigger form:changed event
      return $(me).trigger("form:changed");
    }

    on_analysis_specification_changed(event) {
      var me;
      /*
       * Eventhandler when the specification of an analysis service changed
       */
      console.debug("°°° on_analysis_specification_changed °°°");
      me = this;
      // trigger form:changed event
      return $(me).trigger("form:changed");
    }

    on_analysis_details_click(event) {
      /*
       * Eventhandler when the user clicked on the info icon of a service.
       */
      var $el, arnum, context, data, el, extra, info, profiles, record, specifications, template, templates, uid;
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
        templates: [],
        specifications: []
      };
      // get the current snapshot record for this column
      record = this.records_snapshot[arnum];
      // inject profile info
      if (uid in record.service_to_profiles) {
        profiles = record.service_to_profiles[uid];
        $.each(profiles, function(index, uid) {
          return extra["profiles"].push(record.profile_metadata[uid]);
        });
      }
      // inject template info
      if (uid in record.service_to_templates) {
        templates = record.service_to_templates[uid];
        $.each(templates, function(index, uid) {
          return extra["templates"].push(record.template_metadata[uid]);
        });
      }
      // inject specification info
      if (uid in record.service_to_specifications) {
        specifications = record.service_to_specifications[uid];
        $.each(specifications, function(index, uid) {
          return extra["specifications"].push(record.specification_metadata[uid]);
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
        context["profiles"].push(record.profile_metadata[profile_uid]);
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

    on_sample_changed(event) {
      /*
       * Eventhandler when the Sample was changed.
       */
      var $el, arnum, el, has_sample_selected, me, uid, val;
      me = this;
      el = event.currentTarget;
      $el = $(el);
      uid = $(el).attr("uid");
      val = $el.val();
      arnum = $el.closest("[arnum]").attr("arnum");
      has_sample_selected = $el.val();
      console.debug(`°°° on_sample_change::UID=${uid} PrimaryAnalysisRequest=${val}°°°`);
      // deselect the sample if the field is empty
      if (!has_sample_selected) {
        // XXX manually flush UID field
        $("input[type=hidden]", $el.parent()).val("");
      }
      // trigger form:changed event
      return $(me).trigger("form:changed");
    }

    on_sampletype_changed(event) {
      /*
       * Eventhandler when the SampleType was changed.
       * Fires form:changed event
       */
      var $el, arnum, el, field_ids, has_sampletype_selected, me, uid, val;
      me = this;
      el = event.currentTarget;
      $el = $(el);
      uid = $(el).attr("uid");
      val = $el.val();
      arnum = $el.closest("[arnum]").attr("arnum");
      has_sampletype_selected = $el.val();
      console.debug(`°°° on_sampletype_change::UID=${uid} SampleType=${val}°°°`);
      // deselect the sampletype if the field is empty
      if (!has_sampletype_selected) {
        // XXX manually flush UID field
        $("input[type=hidden]", $el.parent()).val("");
      }
      // Flush sampletype depending fields
      field_ids = ["SamplePoint", "Specification"];
      $.each(field_ids, function(index, id) {
        var field;
        field = me.get_field_by_id(id, arnum);
        return me.flush_reference_field(field);
      });
      // trigger form:changed event
      return $(me).trigger("form:changed");
    }

    on_specification_changed(event) {
      /*
       * Eventhandler when the Specification was changed.
       */
      var $el, arnum, el, has_specification_selected, me, uid, val;
      me = this;
      el = event.currentTarget;
      $el = $(el);
      uid = $(el).attr("uid");
      val = $el.val();
      arnum = $el.closest("[arnum]").attr("arnum");
      has_specification_selected = $el.val();
      console.debug(`°°° on_specification_change::UID=${uid} Specification=${val}°°°`);
      // deselect the specification if the field is empty
      if (!has_specification_selected) {
        // XXX manually flush UID field
        $("input[type=hidden]", $el.parent()).val("");
      }
      // trigger form:changed event
      return $(me).trigger("form:changed");
    }

    on_analysis_template_changed(event) {
      /*
       * Eventhandler when an Analysis Template was changed.
       */
      var $el, $parent, arnum, context, dialog, el, existing_uids, field, has_template_selected, item, me, record, remove_index, template_metadata, template_services, title, uid, uids_field, val;
      me = this;
      el = event.currentTarget;
      $el = $(el);
      uid = $(el).attr("uid");
      val = $el.val();
      arnum = $el.closest("[arnum]").attr("arnum");
      has_template_selected = $el.val();
      console.debug(`°°° on_analysis_template_change::UID=${uid} Template=${val}°°°`);
      // remember the set uid to handle later removal
      if (uid) {
        $el.attr("previous_uid", uid);
      } else {
        uid = $el.attr("previous_uid");
      }
      // deselect the template if the field is empty
      if (!has_template_selected && uid) {
        // forget the applied template
        this.applied_templates[arnum] = null;
        // XXX manually flush UID field
        $("input[type=hidden]", $el.parent()).val("");
        record = this.records_snapshot[arnum];
        template_metadata = record.template_metadata[uid];
        template_services = [];
        // prepare a list of services used by the template with the given UID
        $.each(record.template_to_services[uid], function(index, uid) {
          // service might be deselected before and thus, absent
          if (uid in record.service_metadata) {
            return template_services.push(record.service_metadata[uid]);
          }
        });
        if (template_services.length) {
          context = {};
          context["template"] = template_metadata;
          context["services"] = template_services;
          dialog = this.template_dialog("template-remove-template", context);
          dialog.on("yes", function() {
            // deselect the services
            $.each(template_services, function(index, service) {
              return me.set_service(arnum, service.uid, false);
            });
            // trigger form:changed event
            return $(me).trigger("form:changed");
          });
          dialog.on("no", function() {
            // trigger form:changed event
            return $(me).trigger("form:changed");
          });
        }
        // deselect the profile coming from the template
        // XXX: This is crazy and need to get refactored!
        if (template_metadata.analysis_profile_uid) {
          field = $(`#Profiles-${arnum}`);
          // uid and title of the selected profile
          uid = template_metadata.analysis_profile_uid;
          title = template_metadata.analysis_profile_title;
          // get the parent field wrapper (field is only the input)
          $parent = field.closest("div.field");
          // search for the multi item and remove it
          item = $(`.reference_multi_item[uid=${uid}]`, $parent);
          if (item.length) {
            item.remove();
            // remove the uid from the hidden field
            uids_field = $("input[type=hidden]", $parent);
            existing_uids = uids_field.val().split(",");
            remove_index = existing_uids.indexOf(uid);
            if (remove_index > -1) {
              existing_uids.splice(remove_index, 1);
            }
            uids_field.val(existing_uids.join(","));
          }
        }
        // deselect the samplepoint
        if (template_metadata.sample_point_uid) {
          field = $(`#SamplePoint-${arnum}`);
          this.flush_reference_field(field);
        }
        // deselect the sampletype
        if (template_metadata.sample_type_uid) {
          field = $(`#SampleType-${arnum}`);
          this.flush_reference_field(field);
        }
        // flush the remarks field
        if (template_metadata.remarks) {
          field = $(`#Remarks-${arnum}`);
          field.text("");
        }
        // reset the composite checkbox
        if (template_metadata.composite) {
          field = $(`#Composite-${arnum}`);
          field.prop("checked", false);
        }
      }
      // trigger form:changed event
      return $(me).trigger("form:changed");
    }

    on_analysis_profile_selected(event) {
      var $el, el, me, uid;
      /*
       * Eventhandler when an Analysis Profile was selected.
       */
      console.debug("°°° on_analysis_profile_selected °°°");
      me = this;
      el = event.currentTarget;
      $el = $(el);
      uid = $(el).attr("uid");
      // trigger form:changed event
      return $(me).trigger("form:changed");
    }

    on_analysis_profile_removed(event) {
      var $el, arnum, context, dialog, el, me, profile_metadata, profile_services, record, uid;
      /*
       * Eventhandler when an Analysis Profile was removed.
       */
      console.debug("°°° on_analysis_profile_removed °°°");
      me = this;
      el = event.currentTarget;
      $el = $(el);
      uid = $el.attr("uid");
      arnum = $el.closest("[arnum]").attr("arnum");
      record = this.records_snapshot[arnum];
      profile_metadata = record.profile_metadata[uid];
      profile_services = [];
      // prepare a list of services used by the profile with the given UID
      $.each(record.profile_to_services[uid], function(index, uid) {
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
      // trigger form:changed event
      return $(me).trigger("form:changed");
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
      var $el, $td1, $tr, ar_count, el, field, me, mvl, record_one, td1, tr, uid, value;
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
      // ReferenceWidget cannot be simply copied, the combogrid dropdown widgets
      // don't cooperate and the multiValued div must be copied.
      if ($(td1).find('.ArchetypesReferenceWidget').length > 0) {
        console.debug("-> Copy reference field");
        el = $(td1).find(".ArchetypesReferenceWidget");
        field = el.find("input[type=text]");
        uid = field.attr("uid");
        value = field.val();
        mvl = el.find(".multiValued-listing");
        $.each((function() {
          var results = [];
          for (var i = 1; 1 <= ar_count ? i <= ar_count : i >= ar_count; 1 <= ar_count ? i++ : i--){ results.push(i); }
          return results;
        }).apply(this), function(arnum) {
          var _el, _field, _td;
          // skip the first column
          if (!(arnum > 0)) {
            return;
          }
          _td = $tr.find(`td[arnum=${arnum}]`);
          _el = $(_td).find(".ArchetypesReferenceWidget");
          _field = _el.find("input[type=text]");
          // flush the field completely
          me.flush_reference_field(_field);
          if (mvl.length > 0) {
            // multi valued reference field
            $.each(mvl.children(), function(idx, item) {
              uid = $(item).attr("uid");
              value = $(item).text();
              return me.set_reference_field(_field, uid, value);
            });
          } else {
            // single reference field
            me.set_reference_field(_field, uid, value);
          }
          // notify that the field changed
          return $(_field).trigger("change");
        });
        // trigger form:changed event
        $(me).trigger("form:changed");
        return;
      }
      // Copy <input type="checkbox"> fields
      $td1.find("input[type=checkbox]").each(function(index, el) {
        var checked;
        console.debug("-> Copy checkbox field");
        $el = $(el);
        checked = $el.prop("checked");
        // iterate over columns, starting from column 2
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
          _el = $(_td).find("input[type=checkbox]")[index];
          return $(_el).prop("checked", checked);
        });
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
          return $(_el).val(value);
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
      // trigger form:changed event
      return $(me).trigger("form:changed");
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
        contentType: false
      };
      // contentType: 'application/x-www-form-urlencoded; charset=UTF-8'

      // Update Options
      $.extend(ajax_options, options);
      /* Execute the request */
      // Notify Ajax start
      me = this;
      $(me).trigger("ajax:start");
      return $.ajax(ajax_options).always(function(data) {
        // Always notify Ajax end
        return $(me).trigger("ajax:end");
      });
    }

    on_ajax_start() {
      var button;
      /*
       * Ajax request started
       */
      console.debug("°°° on_ajax_start °°°");
      // deactivate the button
      button = $("input[name=save_button]");
      return button.prop({
        "disabled": true
      });
    }

    on_ajax_end() {
      var button;
      /*
       * Ajax request finished
       */
      console.debug("°°° on_ajax_end °°°");
      // reactivate the button
      button = $("input[name=save_button]");
      return button.prop({
        "disabled": false
      });
    }

    on_form_submit(event, callback) {
      var base_url, me;
      /*
       * Eventhandler for the form submit button.
       * Extracts and submits all form data asynchronous.
       */
      console.debug("°°° on_form_submit °°°");
      event.preventDefault();
      me = this;
      // get the right base url
      base_url = me.get_base_url();
      // remove all errors
      $("div.error").removeClass("error");
      $("div.fieldErrorBox").text("");
      // Ajax POST to the submit endpoint
      return this.ajax_post_form("submit").done(function(data) {
        var ars, destination, errorbox, field, fieldname, message, msg, parent, q, stickertemplate;
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
            msg = `${msg}<br/>`;
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
        } else if (data['stickers']) {
          destination = base_url;
          ars = data['stickers'];
          stickertemplate = data['stickertemplate'];
          q = '/sticker?autoprint=1&template=' + stickertemplate + '&items=' + ars.join(',');
          return window.location.replace(destination + q);
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
        add_btn_src = `${window.portal_url}/++resource++bika.lims.images/add.png`;
        add_btn = $(`<img class='addbtn' style='cursor:pointer;' src='${add_btn_src}' />`);
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
      del_btn_src = `${window.portal_url}/++resource++bika.lims.images/delete.png`;
      del_btn = $(`<img class='delbtn' style='cursor:pointer;' src='${del_btn_src}' />`);
      // Bind an DELETE event handler
      del_btn.on("click", element, function(event) {
        return $(this).parent().remove();
      });
      // Attach the Button into the same div container
      file_field_div.append(del_btn);
      // Attach the new field to the outer div of the passed file field
      return $(element).parent().parent().append(file_field_div);
    }

  };

}).call(this);
