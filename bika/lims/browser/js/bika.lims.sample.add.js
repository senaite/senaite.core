
/* Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.sample.add.coffee
 */

(function() {
  var bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
    indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  window.SampleAdd = (function() {
    function SampleAdd() {
      this.init_file_fields = bind(this.init_file_fields, this);
      this.on_form_submit = bind(this.on_form_submit, this);
      this.on_ajax_end = bind(this.on_ajax_end, this);
      this.on_ajax_start = bind(this.on_ajax_start, this);
      this.ajax_post_form = bind(this.ajax_post_form, this);
      this.on_copy_button_click = bind(this.on_copy_button_click, this);
      this.on_sampletype_changed = bind(this.on_sampletype_changed, this);
      this.on_client_changed = bind(this.on_client_changed, this);
      this.set_sampletype = bind(this.set_sampletype, this);
      this.set_client = bind(this.set_client, this);
      this.set_reference_field = bind(this.set_reference_field, this);
      this.set_reference_field_query = bind(this.set_reference_field_query, this);
      this.get_field_by_id = bind(this.get_field_by_id, this);
      this.get_fields = bind(this.get_fields, this);
      this.get_form = bind(this.get_form, this);
      this.get_authenticator = bind(this.get_authenticator, this);
      this.get_base_url = bind(this.get_base_url, this);
      this.get_portal_url = bind(this.get_portal_url, this);
      this.update_form = bind(this.update_form, this);
      this.recalculate_records = bind(this.recalculate_records, this);
      this.get_global_settings = bind(this.get_global_settings, this);
      this.render_template = bind(this.render_template, this);
      this.template_dialog = bind(this.template_dialog, this);
      this.bind_eventhandler = bind(this.bind_eventhandler, this);
      this.load = bind(this.load, this);
    }

    SampleAdd.prototype.load = function() {
      console.debug("SampleAdd::load");
      jarn.i18n.loadCatalog('bika');
      this._ = window.jarn.i18n.MessageFactory('bika');
      $('input[type=text]').prop('autocomplete', 'off');
      this.global_settings = {};
      this.records_snapshot = {};
      $(".blurrable").removeClass("blurrable");
      this.bind_eventhandler();
      this.init_file_fields();
      this.get_global_settings();
      return this.recalculate_records();
    };


    /* METHODS */

    SampleAdd.prototype.bind_eventhandler = function() {

      /*
       * Binds callbacks on elements
       */
      console.debug("SampleAdd::bind_eventhandler");
      $("[name='save_button']").on("click", this.on_form_submit);
      $("tr[fieldname=Client] input[type='text']").on("selected change", this.on_client_changed);
      $("tr[fieldname=SampleType] input[type='text']").on("selected change", this.on_sampletype_changed);
      $("img.copybutton").on("click", this.on_copy_button_click);

      /* internal events */
      $(this).on("form:changed", this.recalculate_records);
      $(this).on("data:updated", this.update_form);
      $(this).on("ajax:start", this.on_ajax_start);
      return $(this).on("ajax:end", this.on_ajax_end);
    };

    SampleAdd.prototype.template_dialog = function(template_id, context, buttons) {

      /*
       * Render the content of a Handlebars template in a jQuery UID dialog
         [1] http://handlebarsjs.com/
         [2] https://jqueryui.com/dialog/
       */
      var content;
      if (buttons == null) {
        buttons = {};
        buttons[this._("Yes")] = function() {
          $(this).trigger("yes");
          return $(this).dialog("close");
        };
        buttons[this._("No")] = function() {
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

    SampleAdd.prototype.render_template = function(template_id, context) {

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

    SampleAdd.prototype.get_global_settings = function() {

      /*
       * Submit all form values to the server to recalculate the records
       */
      return this.ajax_post_form("get_global_settings").done(function(settings) {
        console.debug("Global Settings:", settings);
        this.global_settings = settings;
        return $(this).trigger("settings:updated", settings);
      });
    };

    SampleAdd.prototype.recalculate_records = function() {

      /*
       * Submit all form values to the server to recalculate the records
       */
      return this.ajax_post_form("recalculate_records").done(function(records) {
        console.debug("Recalculate Sample: Records=", records);
        this.records_snapshot = records;
        return $(this).trigger("data:updated", records);
      });
    };

    SampleAdd.prototype.update_form = function(event, records) {

      /*
       * Update form according to the server data
       */
      var me;
      console.debug("*** update_form ***");
      me = this;
      $(".service-lockbtn").hide();
      return $.each(records, function(arnum, record) {
        $.each(record.client_metadata, function(uid, client) {
          return me.set_client(arnum, client);
        });
        $.each(record.contact_metadata, function(uid, contact) {
          return me.set_contact(arnum, contact);
        });
        $.each(record.service_metadata, function(uid, metadata) {
          var lock;
          lock = $("#" + uid + "-" + arnum + "-lockbtn");
          if (uid in record.service_to_profiles) {
            lock.show();
          }
          if (uid in record.service_to_dms) {
            lock.show();
          }
          return me.set_service(arnum, uid, true);
        });
        $.each(record.template_metadata, function(uid, template) {
          return me.set_template(arnum, template);
        });
        $.each(record.specification_metadata, function(uid, spec) {
          return $.each(spec.specifications, function(uid, service_spec) {
            return me.set_service_spec(arnum, uid, service_spec);
          });
        });
        $.each(record.sample_metadata, function(uid, sample) {
          return me.set_sample(arnum, sample);
        });
        $.each(record.sampletype_metadata, function(uid, sampletype) {
          return me.set_sampletype(arnum, sampletype);
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

    SampleAdd.prototype.get_portal_url = function() {

      /*
       * Return the portal url (calculated in code)
       */
      var url;
      url = $("input[name=portal_url]").val();
      return url;
    };

    SampleAdd.prototype.get_base_url = function() {

      /*
       * Return the current (relative) base url
       */
      var base_url;
      base_url = window.location.href;
      if (base_url.search("/portal_factory") >= 0) {
        return base_url.split("/portal_factory")[0];
      }
      return base_url.split("/sample_add")[0];
    };

    SampleAdd.prototype.get_authenticator = function() {

      /*
       * Get the authenticator value
       */
      return $("input[name='_authenticator']").val();
    };

    SampleAdd.prototype.get_form = function() {

      /*
       * Return the form element
       */
      return $("#sample_add_form");
    };

    SampleAdd.prototype.get_fields = function(arnum) {

      /*
       * Get all fields of the form
       */
      var fields, fields_selector, form;
      form = this.get_form();
      fields_selector = "tr[fieldname] td[arnum] input";
      if (arnum != null) {
        fields_selector = "tr[fieldname] td[arnum=" + arnum + "] input";
      }
      fields = $(fields_selector, form);
      return fields;
    };

    SampleAdd.prototype.get_field_by_id = function(id, arnum) {

      /*
       * Query the field by id
       */
      var field_id, name, ref, suffix;
      ref = id.split("_"), name = ref[0], suffix = ref[1];
      field_id = name + "-" + arnum;
      if (suffix != null) {
        field_id = field_id + "_" + suffix;
      }
      if (!id.startsWith("#")) {
        field_id = "#" + field_id;
      }
      console.debug("get_field_by_id: $(" + field_id + ")");
      return $(field_id);
    };

    SampleAdd.prototype.flush_reference_field = function(field) {

      /*
       * Empty the reference field
       */
      var catalog_name;
      catalog_name = field.attr("catalog_name");
      if (!catalog_name) {
        return;
      }
      field.val("");
      $("input[type=hidden]", field.parent()).val("");
      return $(".multiValued-listing", field.parent()).empty();
    };

    SampleAdd.prototype.set_reference_field_query = function(field, query, type) {
      var catalog_name, catalog_query, new_query, options, url;
      if (type == null) {
        type = "base_query";
      }

      /*
       * Set the catalog search query for the given reference field
       * XXX This is lame! The field should provide a proper API.
       */
      catalog_name = field.attr("catalog_name");
      if (!catalog_name) {
        return;
      }
      options = $.parseJSON(field.attr("combogrid_options"));
      url = this.get_base_url();
      url += "/" + options.url;
      url += "?_authenticator=" + (this.get_authenticator());
      url += "&catalog_name=" + catalog_name;
      url += "&colModel=" + ($.toJSON(options.colModel));
      url += "&search_fields=" + ($.toJSON(options.search_fields));
      url += "&discard_empty=" + ($.toJSON(options.discard_empty));
      catalog_query = $.parseJSON(field.attr(type));
      $.extend(catalog_query, query);
      new_query = $.toJSON(catalog_query);
      console.debug("set_reference_field_query: query=" + new_query);
      if (type === 'base_query') {
        url += "&base_query=" + new_query;
        url += "&search_query=" + (field.attr('search_query'));
      } else {
        url += "&base_query=" + (field.attr('base_query'));
        url += "&search_query=" + new_query;
      }
      options.url = url;
      options.force_all = "false";
      field.combogrid(options);
      return field.attr("search_query", "{}");
    };

    SampleAdd.prototype.set_reference_field = function(field, uid, title) {

      /*
       * Set the value and the uid of a reference field
       * XXX This is lame! The field should handle this on data change.
       */
      var $field, $parent, div, existing_uids, fieldname, img, me, mvl, portal_url, src, uids, uids_field;
      me = this;
      $field = $(field);
      if (!$field.length) {
        console.debug("field " + field + " does not exist, skip set_reference_field");
        return;
      }
      $parent = field.closest("div.field");
      fieldname = field.attr("name");
      console.debug("set_reference_field:: field=" + fieldname + " uid=" + uid + " title=" + title);
      uids_field = $("input[type=hidden]", $parent);
      existing_uids = uids_field.val();
      if (existing_uids.indexOf(uid) >= 0) {
        return;
      }
      if (existing_uids.length === 0) {
        uids_field.val(uid);
      } else {
        uids = uids_field.val().split(",");
        uids.push(uid);
        uids_field.val(uids.join(","));
      }
      $field.val(title);
      mvl = $(".multiValued-listing", $parent);
      if (mvl.length > 0) {
        portal_url = this.get_portal_url();
        src = portal_url + "/++resource++bika.lims.images/delete.png";
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
    };

    SampleAdd.prototype.set_client = function(arnum, client) {

      /*
       * Filter Contacts
       * Filter CCContacts
       * Filter InvoiceContacts
       * Filter SamplePoints
       * Filter ARTemplates
       * Filter Specification
       * Filter SamplingRound
       */
      var field, query;
      field = $("#Contact-" + arnum);
      query = client.filter_queries.contact;
      this.set_reference_field_query(field, query);
      field = $("#CCContact-" + arnum);
      query = client.filter_queries.cc_contact;
      this.set_reference_field_query(field, query);
      field = $("#InvoiceContact-" + arnum);
      query = client.filter_queries.invoice_contact;
      this.set_reference_field_query(field, query);
      field = $("#SamplePoint-" + arnum);
      query = client.filter_queries.samplepoint;
      this.set_reference_field_query(field, query);
      field = $("#Template-" + arnum);
      query = client.filter_queries.artemplates;
      this.set_reference_field_query(field, query);
      field = $("#Profiles-" + arnum);
      query = client.filter_queries.analysisprofiles;
      this.set_reference_field_query(field, query);
      field = $("#Specification-" + arnum);
      query = client.filter_queries.analysisspecs;
      this.set_reference_field_query(field, query);
      field = $("#SamplingRound-" + arnum);
      query = client.filter_queries.samplinground;
      this.set_reference_field_query(field, query);
      field = $("#Sample-" + arnum);
      query = client.filter_queries.sample;
      return this.set_reference_field_query(field, query);
    };

    SampleAdd.prototype.set_sampletype = function(arnum, sampletype) {

      /*
       * Recalculate partitions
       * Filter Sample Points
       */
      var field, query, title, uid;
      field = $("#SamplePoint-" + arnum);
      query = sampletype.filter_queries.samplepoint;
      this.set_reference_field_query(field, query);
      field = $("#DefaultContainerType-" + arnum);
      if (!field.val()) {
        uid = sampletype.container_type_uid;
        title = sampletype.container_type_title;
        this.flush_reference_field(field);
        this.set_reference_field(field, uid, title);
      }
      field = $("#Specification-" + arnum);
      query = sampletype.filter_queries.specification;
      return this.set_reference_field_query(field, query);
    };


    /* EVENT HANDLER */

    SampleAdd.prototype.on_client_changed = function(event) {

      /*
       * Eventhandler when the client changed (happens on Batches)
       */
      var $el, arnum, el, field_ids, me, uid;
      me = this;
      el = event.currentTarget;
      $el = $(el);
      uid = $el.attr("uid");
      arnum = $el.closest("[arnum]").attr("arnum");
      console.debug("°°° on_client_changed: arnum=" + arnum + " °°°");
      field_ids = ["Contact", "CCContact", "InvoiceContact", "SamplePoint", "Template", "Profiles", "Specification"];
      $.each(field_ids, function(index, id) {
        var field;
        field = me.get_field_by_id(id, arnum);
        return me.flush_reference_field(field);
      });
      return $(me).trigger("form:changed");
    };

    SampleAdd.prototype.on_sampletype_changed = function(event) {

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
      console.debug("°°° on_sampletype_change::UID=" + uid + " SampleType=" + val + "°°°");
      if (!has_sampletype_selected) {
        $("input[type=hidden]", $el.parent()).val("");
      }
      field_ids = ["SamplePoint", "Specification"];
      $.each(field_ids, function(index, id) {
        var field;
        field = me.get_field_by_id(id, arnum);
        return me.flush_reference_field(field);
      });
      return $(me).trigger("form:changed");
    };

    SampleAdd.prototype.on_copy_button_click = function(event) {

      /*
       * Eventhandler for the field copy button per row.
       * Copies the value of the first field in this row to the remaining.
       * XXX Refactor
       */
      var $el, $td1, $tr, ar_count, el, field, i, me, mvl, record_one, results, td1, tr, uid, value;
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
        field = el.find("input[type=text]");
        uid = field.attr("uid");
        value = field.val();
        mvl = el.find(".multiValued-listing");
        $.each((function() {
          results = [];
          for (var i = 1; 1 <= ar_count ? i <= ar_count : i >= ar_count; 1 <= ar_count ? i++ : i--){ results.push(i); }
          return results;
        }).apply(this), function(arnum) {
          var _el, _field, _td;
          if (!(arnum > 0)) {
            return;
          }
          _td = $tr.find("td[arnum=" + arnum + "]");
          _el = $(_td).find(".ArchetypesReferenceWidget");
          _field = _el.find("input[type=text]");
          me.flush_reference_field(_field);
          if (mvl.length > 0) {
            $.each(mvl.children(), function(idx, item) {
              uid = $(item).attr("uid");
              value = $(item).text();
              return me.set_reference_field(_field, uid, value);
            });
          } else {
            me.set_reference_field(_field, uid, value);
          }
          return $(_field).trigger("change");
        });
        $(me).trigger("form:changed");
        return;
      }
      $td1.find("input[type=checkbox]").each(function(index, el) {
        var checked, j, results1;
        console.debug("-> Copy checkbox field");
        $el = $(el);
        checked = $el.prop("checked");
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
          _el = $(_td).find("input[type=checkbox]")[index];
          return $(_el).prop("checked", checked);
        });
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
          return $(_el).val(value);
        });
      });
      return $(me).trigger("form:changed");
    };

    SampleAdd.prototype.ajax_post_form = function(endpoint, options) {
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
        contentType: false
      };
      $.extend(ajax_options, options);

      /* Execute the request */
      me = this;
      $(me).trigger("ajax:start");
      return $.ajax(ajax_options).always(function(data) {
        return $(me).trigger("ajax:end");
      });
    };

    SampleAdd.prototype.on_ajax_start = function() {

      /*
       * Ajax request started
       */
      var button;
      console.debug("°°° on_ajax_start °°°");
      button = $("input[name=save_button]");
      return button.prop({
        "disabled": true
      });
    };

    SampleAdd.prototype.on_ajax_end = function() {

      /*
       * Ajax request finished
       */
      var button;
      console.debug("°°° on_ajax_end °°°");
      button = $("input[name=save_button]");
      return button.prop({
        "disabled": false
      });
    };

    SampleAdd.prototype.on_form_submit = function(event, callback) {

      /*
       * Eventhandler for the form submit button.
       * Extracts and submits all form data asynchronous.
       */
      var base_url, me;
      console.debug("°°° on_form_submit °°°");
      event.preventDefault();
      me = this;
      base_url = me.get_base_url();
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
        var ars, destination, errorbox, field, fieldname, message, msg, parent, q, stickertemplate;
        if (data['errors']) {
          msg = data.errors.message;
          if (msg !== "") {
            msg = msg + "<br/>";
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
    };

    SampleAdd.prototype.init_file_fields = function() {
      var me;
      me = this;
      return $('tr[fieldname] input[type="file"]').each(function(index, element) {
        var add_btn, add_btn_src, file_field, file_field_div;
        file_field = $(element);
        file_field.wrap("<div class='field'/>");
        file_field_div = file_field.parent();
        add_btn_src = window.portal_url + "/++resource++bika.lims.images/add.png";
        add_btn = $("<img class='addbtn' style='cursor:pointer;' src='" + add_btn_src + "' />");
        add_btn.on("click", element, function(event) {
          return me.file_addbtn_click(event, element);
        });
        return file_field_div.append(add_btn);
      });
    };

    SampleAdd.prototype.file_addbtn_click = function(event, element) {
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
      del_btn_src = window.portal_url + "/++resource++bika.lims.images/delete.png";
      del_btn = $("<img class='delbtn' style='cursor:pointer;' src='" + del_btn_src + "' />");
      del_btn.on("click", element, function(event) {
        return $(this).parent().remove();
      });
      file_field_div.append(del_btn);
      return $(element).parent().parent().append(file_field_div);
    };

    return SampleAdd;

  })();

}).call(this);
