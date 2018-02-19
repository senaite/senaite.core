
/* Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.bikalisting.coffee
 */

(function() {
  var bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  window.BikaListingTableView = (function() {
    function BikaListingTableView() {
      this.on_show_more_click = bind(this.on_show_more_click, this);
      this.on_column_header_click = bind(this.on_column_header_click, this);
      this.on_ajax_submit_end = bind(this.on_ajax_submit_end, this);
      this.on_ajax_submit_start = bind(this.on_ajax_submit_start, this);
      this.on_checkbox_click = bind(this.on_checkbox_click, this);
      this.on_select_all_click = bind(this.on_select_all_click, this);
      this.on_search_button_click = bind(this.on_search_button_click, this);
      this.on_search_field_keypress = bind(this.on_search_field_keypress, this);
      this.on_contextmenu_item_click = bind(this.on_contextmenu_item_click, this);
      this.on_contextmenu = bind(this.on_contextmenu, this);
      this.on_workflow_button_click = bind(this.on_workflow_button_click, this);
      this.on_autosave_field_change = bind(this.on_autosave_field_change, this);
      this.on_category_header_click = bind(this.on_category_header_click, this);
      this.on_listing_entry_keypress = bind(this.on_listing_entry_keypress, this);
      this.on_listing_entry_change = bind(this.on_listing_entry_change, this);
      this.on_review_state_filter_click = bind(this.on_review_state_filter_click, this);
      this.on_click = bind(this.on_click, this);
      this.parse_int = bind(this.parse_int, this);
      this.show_more = bind(this.show_more, this);
      this.filter_state = bind(this.filter_state, this);
      this.toggle_category = bind(this.toggle_category, this);
      this.sort_column = bind(this.sort_column, this);
      this.toggle_column = bind(this.toggle_column, this);
      this.get_toggle_cols = bind(this.get_toggle_cols, this);
      this.toggle_sort_order = bind(this.toggle_sort_order, this);
      this.get_toggle_cookie_key = bind(this.get_toggle_cookie_key, this);
      this.set_cookie = bind(this.set_cookie, this);
      this.get_cookie = bind(this.get_cookie, this);
      this.get_authenticator = bind(this.get_authenticator, this);
      this.get_base_url = bind(this.get_base_url, this);
      this.get_portal_url = bind(this.get_portal_url, this);
      this.ajax_submit = bind(this.ajax_submit, this);
      this.bind_eventhandler = bind(this.bind_eventhandler, this);
      this.load = bind(this.load, this);
    }


    /*
    * Controller class for Bika Listing Table view
     */

    BikaListingTableView.prototype.load = function() {
      console.debug("ListingTableView::load");
      this.bind_eventhandler();
      this.loading_transitions = false;
      this.toggle_cols_cookie = "toggle_cols";
      this.load_transitions();
      return window.tv = this;
    };


    /* INITIALIZERS */

    BikaListingTableView.prototype.bind_eventhandler = function() {

      /*
       * Binds callbacks on elements
       *
       * N.B. We attach all the events to the form and refine the selector to
       * delegate the event: https://learn.jquery.com/events/event-delegation/
       *
       */
      console.debug("ListingTableView::bind_eventhandler");
      $("form").on("click", "th.sortable", this.on_column_header_click);
      $("form").on("click", "a.bika_listing_show_more", this.on_show_more_click);
      $("form").on("click", "input[type='checkbox'][id*='_cb_']", this.on_checkbox_click);
      $("form").on("click", "input[id*='select_all']", this.on_select_all_click);
      $("form").on("keypress", ".filter-search-input", this.on_search_field_keypress);
      $("form").on("click", ".filter-search-button", this.on_search_button_click);
      $("form").on('contextmenu', "th[id^='foldercontents-']", this.on_contextmenu);
      $("form").on("click", "input.workflow_action_button", this.on_workflow_button_click);
      $("form").on("change", "input.autosave, select.autsave", this.on_autosave_field_change);
      $("form").on("click", "th.collapsed, th.expanded", this.on_category_header_click);
      $("form").on("change", ".listing_string_entry, .listing_select_entry", this.on_listing_entry_change);
      $("form").on("keypress", ".listing_string_entry, .listing_select_entry", this.on_listing_entry_keypress);
      $("form").on("click", "td.review_state_selector a", this.on_review_state_filter_click);
      $(document).on("click", this.on_click);
      $(document).on("click", ".contextmenu tr", this.on_contextmenu_item_click);
      $(this).on("ajax:submit:start", this.on_ajax_submit_start);
      return $(this).on("ajax:submit:end", this.on_ajax_submit_end);
    };


    /* METHODS */

    BikaListingTableView.prototype.ajax_submit = function(options) {
      var done;
      if (options == null) {
        options = {};
      }

      /*
       * Ajax Submit with automatic event triggering and some sane defaults
       */
      console.debug("°°° ajax_submit °°°");
      if (options.type == null) {
        options.type = "POST";
      }
      if (options.url == null) {
        options.url = window.location.href;
      }
      if (options.context == null) {
        options.context = this;
      }
      console.debug(">>> ajax_submit::options=", options);
      $(this).trigger("ajax:submit:start");
      done = (function(_this) {
        return function() {
          return $(_this).trigger("ajax:submit:end");
        };
      })(this);
      return $.ajax(options).done(done);
    };

    BikaListingTableView.prototype.get_portal_url = function() {

      /*
       * Return the portal url (calculated in code)
       */
      var url;
      url = $("input[name=portal_url]").val();
      return url || window.portal_url;
    };

    BikaListingTableView.prototype.get_base_url = function() {

      /*
       * Return the current base url
       */
      var url;
      url = window.location.href;
      return url.split('?')[0];
    };

    BikaListingTableView.prototype.get_authenticator = function() {

      /*
       * Get the authenticator value
       */
      return $("input[name='_authenticator']").val();
    };

    BikaListingTableView.prototype.get_cookie = function(name) {

      /*
       * read the value of the cookie
       */
      var c, cookies, i;
      name = name + "=";
      cookies = document.cookie.split(";");
      i = 0;
      while (i < cookies.length) {
        c = cookies[i];
        while (c.charAt(0) === " ") {
          c = c.substring(1, c.length);
        }
        if (c.indexOf(name) === 0) {
          return unescape(c.substring(name.length, c.length));
        }
        i = i + 1;
      }
      return null;
    };

    BikaListingTableView.prototype.set_cookie = function(name, value, days) {

      /*
       * set the value of the cookie
       */
      var cookie, date, expires;
      if (days) {
        date = new Date;
        date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000);
        expires = date.toGMTString();
      } else {
        expires = "";
      }
      cookie = name + "=" + (escape(value)) + "; expires=" + expires + "; path=/;";
      document.cookie = cookie;
      return true;
    };

    BikaListingTableView.prototype.get_toggle_cookie_key = function(form_id) {

      /*
       * Make a unique toggle cookie key for the current listing site
       */
      var portal_type;
      portal_type = $("#" + form_id + " input[name=portal_type]").val();
      return "" + portal_type + form_id;
    };

    BikaListingTableView.prototype.toggle_sort_order = function(sort_order) {

      /*
       * Toggle the sort_order value
       */
      if (sort_order === "ascending") {
        return "descending";
      }
      return "ascending";
    };

    BikaListingTableView.prototype.get_toggle_cols = function(form_id) {

      /*
       * Get the value of the toggle cols input field
       */
      var toggle_cols;
      toggle_cols = $("#" + form_id + "_toggle_cols");
      if (toggle_cols.length === 0) {
        return {};
      }
      return $.parseJSON(toggle_cols.val());
    };

    BikaListingTableView.prototype.toggle_column = function(form_id, col_id) {

      /*
       * Toggle column by form and column id
       */
      var all_cols, columns, cookie, cookie_key, form, form_data, table, toggle_cols;
      form = $("form#" + form_id);
      table = $("table.bika-listing-table", form);
      toggle_cols = this.get_toggle_cols(form_id);
      cookie = $.parseJSON(this.get_cookie(this.toggle_cols_cookie) || "{}");
      cookie_key = this.get_toggle_cookie_key(form_id);
      columns = cookie[cookie_key];
      if (!columns) {
        columns = [];
        $.each(toggle_cols, function(name, record) {
          if ($("#foldercontents-" + name + "-column").length > 0) {
            return columns.push(name);
          }
        });
      }
      if (col_id === _('Default')) {
        console.debug("*** Set DEFAULT toggle columns ***");
        delete cookie[cookie_key];
      } else if (col_id === _('All')) {
        console.debug("*** Set ALL toggle columns ***");
        all_cols = [];
        $.each(toggle_cols, function(name, record) {
          return all_cols.push(name);
        });
        cookie[cookie_key] = all_cols;
      } else {
        if (!(col_id in toggle_cols)) {
          console.warn("Invalid column name: '" + col_id + "'");
          return;
        }
        if (columns.indexOf(col_id) > -1) {
          console.debug("*** Toggle " + col_id + " OFF ***");
          columns.splice(columns.indexOf(col_id), 1);
        } else {
          console.debug("*** Toggle " + col_id + " ON ***");
          columns.push(col_id);
        }
        cookie[cookie_key] = columns;
      }
      this.set_cookie(this.toggle_cols_cookie, $.toJSON(cookie), 365);
      form_data = new FormData(form[0]);
      form_data.set("table_only", form_id);
      return this.ajax_submit({
        data: form_data,
        processData: false,
        contentType: false
      }).done(function(data) {
        var menu, style, tooltip;
        $(table).replaceWith(data);
        table = $("table.bika-listing-table", form);
        tooltip = $(".tooltip");
        if (tooltip.length > 0) {
          style = tooltip.attr("style");
          menu = this.make_context_menu(table);
          menu = $(menu).appendTo("body");
          return menu.attr("style", style);
        }
      });
    };

    BikaListingTableView.prototype.sort_column = function(form_id, sort_index) {

      /*
       * Sort column by form and sort index
       */
      var form, form_data, sort_on, sort_on_value, sort_order, sort_order_value, table;
      form = $("form#" + form_id);
      table = $("table.bika-listing-table", form);
      sort_on = $("[name=" + form_id + "_sort_on]");
      sort_order = $("[name=" + form_id + "_sort_order]");
      sort_on_value = sort_on.val();
      sort_order_value = sort_order.val();
      sort_on.val(sort_index);
      sort_order.val(this.toggle_sort_order(sort_order_value));
      form_data = new FormData(form[0]);
      form_data.set("table_only", form_id);
      return this.ajax_submit({
        data: form_data,
        processData: false,
        contentType: false
      }).done(function(data) {
        $(table).replaceWith(data);
        return this.load_transitions();
      });
    };

    BikaListingTableView.prototype.toggle_category = function(form_id, cat_id) {

      /*
       * Toggle category by form and category id
       */
      var base_url, cat, cat_items, cat_url, expanded, form, form_data, placeholder, url;
      form = $("form#" + form_id);
      cat = $("th.cat_header[cat=" + cat_id + "]");
      placeholder = $("tr[data-ajax_category=" + cat_id);
      expanded = cat.hasClass("expanded");
      cat_items = $("tr[cat=" + cat_id + "]");
      cat.toggleClass("expanded collapsed");
      if (cat_items.length > 0) {
        console.debug("ListingTableView::toggle_category: Category " + cat_id + " is already expanded -> Toggle only");
        cat_items.toggle();
        return;
      }
      cat_url = $("input[name=ajax_categories_url]").val();
      base_url = this.get_base_url();
      url = cat_url || base_url;
      form_data = new FormData();
      form_data.set("cat", cat_id);
      form_data.set("form_id", form_id);
      form_data.set("ajax_category_expand", 1);
      return this.ajax_submit({
        url: url,
        data: form_data,
        processData: false,
        contentType: false
      }).done(function(data) {
        placeholder.replaceWith(data);
        return this.load_transitions();
      });
    };

    BikaListingTableView.prototype.filter_state = function(form_id, state_id) {

      /*
       * Filter listing by review_state
       */
      var form, form_data, input, input_name, table;
      form = $("form#" + form_id);
      table = $("table.bika-listing-table", form);
      input_name = form_id + "_review_state";
      input = $("input[name=" + input_name + "]", form);
      if (input.length === 0) {
        input = form.append("<input name='" + input_name + "' value='" + state_id + "' type='hidden'/>");
      }
      input.val(state_id);
      form_data = new FormData(form[0]);
      form_data.set("table_only", form_id);
      form_data.set(form_id + "_review_state", state_id);
      return this.ajax_submit({
        data: form_data,
        processData: false,
        contentType: false
      }).done(function(data) {
        $(table).replaceWith(data);
        return this.load_transitions();
      });
    };

    BikaListingTableView.prototype.show_more = function(form_id, pagesize, limit_from) {

      /*
       * Show more
       */
      var filter_options, filters, filters1, filters2, form, form_data, show_more, table, tbody;
      form = $("form#" + form_id);
      table = $("table.bika-listing-table", form);
      tbody = $("tbody.item-listing-tbody", table);
      show_more = $("#" + form_id + " a.bika_listing_show_more");
      if (pagesize == null) {
        pagesize = 30;
      }
      if (limit_from == null) {
        limit_from = 0;
      }
      form_data = new FormData(form[0]);
      form_data.set("rows_only", form_id);
      form_data.set(form_id + "_pagesize", pagesize);
      form_data.set(form_id + "_limit_from", limit_from);
      filter_options = [];
      filters1 = $(".bika_listing_filter_bar input[name][value!='']");
      filters2 = $(".bika_listing_filter_bar select option:selected[value!='']");
      filters = $.merge(filters1, filters2);
      $(filters).each(function(e) {
        return filter_options.push([$(this).attr('name'), $(this).val()]);
      });
      if (filter_options.length > 0) {
        form_data.set("bika_listing_filter_bar", $.toJSON(filter_options));
      }
      show_more.fadeOut();
      return this.ajax_submit({
        data: form_data,
        processData: false,
        contentType: false
      }).done(function(data) {
        var numitems, rows;
        rows = $(data).filter("tr");
        if (rows.length % pagesize === 0) {
          show_more.fadeIn();
        }
        if (limit_from === 0) {
          $(tbody).empty();
        }
        $(tbody).append(rows);
        numitems = $("table.bika-listing-table[form_id=" + form_id + "] tbody.item-listing-tbody tr").length;
        $("#" + form_id + " span.number-items").html(numitems);
        show_more.attr("data-limitfrom", numitems);
        show_more.attr("data-pagesize", pagesize);
        return this.load_transitions();
      });
    };

    BikaListingTableView.prototype.parse_int = function(thing, fallback) {
      var number;
      if (fallback == null) {
        fallback = 0;
      }

      /*
       * Safely parse to an integer
       */
      number = parseInt(thing);
      return number || fallback;
    };

    BikaListingTableView.prototype.load_transitions = function(table) {

      /*
       * Fetch allowed transitions for all the objects listed in bika_listing and
       * sets the value for the attribute 'data-valid_transitions' for each check
       * box next to each row.
       * The process requires an ajax call, so the function keeps checkboxes
       * disabled until the allowed transitions for the associated object are set.
       */
      var $table, checkall, self, uids, wf_buttons, wo_trans;
      self = this;
      if (!table) {
        $("table.bika-listing-table").each(function(index) {
          return self.load_transitions(this);
        });
      }
      $table = $(table);
      wf_buttons = $(table).find("span.workflow_action_buttons");
      if (this.loading_transitions || $(wf_buttons).length === 0) {
        return;
      }
      uids = [];
      checkall = $("input[id*='select_all']", $table);
      $(checkall).hide();
      wo_trans = $("input[id*='_cb_'][data-valid_transitions='{}']");
      $(wo_trans).prop("disabled", true);
      $(wo_trans).each(function(e) {
        return uids.push($(this).val());
      });
      if (uids.length === 0) {
        return;
      }
      this.loading_transitions = true;
      return this.ajax_submit({
        url: (this.get_portal_url()) + "/@@API/allowedTransitionsFor_many",
        data: {
          _authenticator: this.get_authenticator(),
          uid: $.toJSON(uids)
        }
      }).done(function(data) {
        this.loading_transitions = false;
        $("input[id*='select_all']").fadeIn();
        if ("transitions" in data) {
          $.each(data.transitions, function(index, record) {
            var checkbox, trans, uid;
            uid = record.uid;
            trans = record.transitions;
            checkbox = $("input[id*='_cb_'][value='" + uid + "']");
            checkbox.attr("data-valid_transitions", $.toJSON(trans));
            return $(checkbox).prop("disabled", false);
          });
        }
        return this.render_transition_buttons(table);
      });
    };

    BikaListingTableView.prototype.render_transition_buttons = function(table) {

      /* Render workflow transition buttons to the table
       *
       * Re-generates the workflow action buttons from the bottom of the list in
       * accordance with the allowed transitions for the currently selected items.
       * This is, makes the intersection within all allowed transitions and adds
       * the corresponding buttons to the workflow action bar.
       */
      var allowed_transitions, checked, custom_transitions, hidden_transitions, restricted_transitions, self, wf_buttons;
      self = this;
      wf_buttons = $(table).find("span.workflow_action_buttons");
      if ($(wf_buttons).length === 0) {
        return;
      }
      allowed_transitions = [];
      hidden_transitions = $(table).find("input[id='hide_transitions']");
      hidden_transitions = $(hidden_transitions).length === 1 ? $(hidden_transitions).val() : '';
      hidden_transitions = hidden_transitions === '' ? [] : hidden_transitions.split(',');
      restricted_transitions = $(table).find("input[id='restricted_transitions']");
      restricted_transitions = $(restricted_transitions).length === 1 ? $(restricted_transitions).val() : '';
      restricted_transitions = restricted_transitions === '' ? [] : restricted_transitions.split(',');
      checked = $(table).find("input[id*='_cb_']:checked");
      $(checked).each(function(index) {
        var transitions;
        transitions = $.parseJSON($(this).attr("data-valid_transitions"));
        if (!transitions.length) {
          return;
        }
        if (restricted_transitions.length > 0) {
          transitions = transitions.filter(function(el) {
            return restricted_transitions.indexOf(el.id) > -1;
          });
        }
        if (hidden_transitions.length > 0) {
          transitions = transitions.filter(function(el) {
            return hidden_transitions.indexOf(el.id) < 0;
          });
        }
        if (allowed_transitions.length > 0) {
          return transitions = transitions.filter(function(el) {
            return allowed_transitions.indexOf(el) > -1;
          });
        } else {
          allowed_transitions = transitions;
          if (transitions.length > 0) {
            return allowed_transitions = allowed_transitions.filter(function(el) {
              return transitions.indexOf(el) > -1;
            });
          }
        }
      });
      $(wf_buttons).html("");
      $.each(allowed_transitions, function(index, record) {
        var button, transition, url, value;
        transition = record.id;
        url = "";
        value = PMF(record.title);
        button = self.make_wf_button(transition, url, value);
        return $(wf_buttons).append(button);
      });
      if ($(checked).length > 0) {
        custom_transitions = $(table).find("input[type='hidden'].custom_transition");
        return $.each(custom_transitions, function(index, element) {
          var button, transition, url, value;
          transition = $(element).val();
          url = $(element).attr("url");
          value = $(element).attr("title");
          button = self.make_wf_button(transition, url, value);
          return $(wf_buttons).append(button);
        });
      }
    };

    BikaListingTableView.prototype.make_wf_button = function(transition, url, value) {

      /*
       * Make a workflow button
       */
      var button;
      button = "<input id='" + transition + "_transition' class='context workflow_action_button action_button allowMultiSubmit' type='submit' url='" + url + "' value='" + value + "' transition='" + transition + "' name='workflow_action_button'/>&nbsp;";
      return button;
    };

    BikaListingTableView.prototype.search = function(form_id, searchterm) {

      /*
       * Search in table and expand the rows
       */
      var form, form_data, table;
      form = $("form#" + form_id);
      form_id = form.attr("id");
      table = $("table.bika-listing-table", form);
      form_data = new FormData(form[0]);
      form_data.set("table_only", form_id);
      form_data.set(form_id + "_filter", searchterm);
      return this.ajax_submit({
        data: form_data,
        processData: false,
        contentType: false
      }).done(function(data) {
        table = $(table).replaceWith(data);
        $(".filter-search-input", form).select();
        return this.load_transitions();
      });
    };

    BikaListingTableView.prototype.make_context_menu = function(table) {

      /*
       * Build context menu HTML
       */
      var form, form_id, menu, portal_url, sorted_toggle_cols, toggle_cols, toggleable_columns;
      console.debug("°°° ListingTableView::make_context_menu °°°");
      $(".tooltip").remove();
      form = $(table).parents("form");
      form_id = form.attr("id");
      portal_url = this.get_portal_url();
      toggle_cols = $("#" + form_id + "_toggle_cols");
      if (!toggle_cols.val()) {
        console.warn("Could not get toggle column info from input field " + toggle_cols);
        return false;
      }
      sorted_toggle_cols = [];
      $.each($.parseJSON(toggle_cols.val()), function(column, record) {
        record.id = column;
        record.title = _(record.title) || _(record.id);
        sorted_toggle_cols.push(record);
      });
      sorted_toggle_cols.sort(function(a, b) {
        var titleA, titleB;
        titleA = a.title.toLowerCase();
        titleB = b.title.toLowerCase();
        if (titleA < titleB) {
          return -1;
        }
        if (titleA > titleB) {
          return 1;
        }
        return 0;
      });
      toggleable_columns = "";
      $.each(sorted_toggle_cols, function(index, record) {
        var col, column_exists;
        column_exists = $("#foldercontents-" + record.id + "-column");
        if (column_exists.length > 0) {
          col = "<tr class=\"enabled\" col_id=\"" + record.id + "\" form_id=\"" + form_id + "\">\n  <td>&#10003;</td>\n  <td>" + (record.title || record.id) + "</td>\n</tr>";
        } else {
          col = "<tr col_id=" + record.id + " form_id=\"" + form_id + "\">\n  <td>&nbsp;</td>\n  <td>" + (record.title || record.id) + "</td>\n</tr>";
        }
        return toggleable_columns += col;
      });
      menu = "<div class=\"tooltip bottom\">\n  <div class=\"tooltip-inner\">\n    <table class=\"contextmenu\" cellpadding=\"0\" cellspacing=\"0\">\n      <tr>\n        <th colspan=\"2\">" + (_("Display columns")) + "</th>\n      </tr>\n      " + toggleable_columns + "\n      <tr col_id=\"" + (_("All")) + "\" form_id=\"" + form_id + "\">\n        <td style=\"border-top:1px solid #ddd;\">&nbsp;</td>\n        <td style=\"border-top:1px solid #ddd;\">" + (_("All")) + "</td>\n      </tr>\n      <tr col_id=\"" + (_("Default")) + "\" form_id=\"" + form_id + "\">\n        <td>&nbsp;</td>\n        <td>" + (_("Default")) + "</td>\n      </tr>\n    </table>\n  </div>\n  <div class=\"tooltip-arrow\"></div>\n</div>";
      return menu;
    };


    /* EVENT HANDLER */

    BikaListingTableView.prototype.on_click = function(event) {

      /*
       * Eventhandler for all clicks
       */
      var el;
      el = $(event.target);
      if (el.parents(".tooltip").length === 0) {
        return $(".tooltip").remove();
      }
    };

    BikaListingTableView.prototype.on_review_state_filter_click = function(event) {

      /*
       * Eventhandler for review state filter buttons
       */
      var $el, el, form, form_id, state_id;
      console.debug("°°° ListingTableView::on_review_state_filter_click °°°");
      event.preventDefault();
      el = event.currentTarget;
      $el = $(el);
      form = $el.parents("form");
      form_id = form.attr("id");
      state_id = $el.attr("value");
      return this.filter_state(form_id, state_id);
    };

    BikaListingTableView.prototype.on_listing_entry_change = function(event) {

      /*
       * Eventhandler for listing entries (results capturing)
       */
      var $el, checkbox, el, table, tr, uid;
      console.debug("°°° ListingTableView::on_listing_entry_change °°°");
      el = event.currentTarget;
      $el = $(el);
      uid = $el.attr("uid");
      tr = $el.parents("tr#folder-contents-item-" + uid);
      checkbox = tr.find("input[id$=_cb_" + uid + "]");
      if ($(checkbox).length === 1) {
        table = $(checkbox).parents("table.bika-listing-table");
        $(checkbox).prop('checked', true);
        return this.render_transition_buttons(table);
      }
    };

    BikaListingTableView.prototype.on_listing_entry_keypress = function(event) {

      /*
       * Eventhandler for listing entries (results capturing)
       */
      console.debug("°°° ListingTableView::on_listing_entry_keypress °°°");
      if (event.which === 13) {
        console.debug("ListingTableView::on_listing_entry_keypress: capture Enter key");
        return event.preventDefault();
      }
    };

    BikaListingTableView.prototype.on_category_header_click = function(event) {

      /*
       * Eventhandler for collapsed/expanded categories
       */
      var $el, cat_id, el, form, form_id;
      console.debug("°°° ListingTableView::on_category_header_click °°°");
      el = event.currentTarget;
      $el = $(el);
      if ($el.hasClass("ignore_bikalisting_default_handler")) {
        console.debug("Category toggling disabled by CSS class");
        return;
      }
      form = $el.parents("form");
      form_id = form.attr("id");
      cat_id = $el.attr("cat");
      return this.toggle_category(form_id, cat_id);
    };

    BikaListingTableView.prototype.on_autosave_field_change = function(event) {

      /*
       * Eventhandler for input fields with `autosave` css class
       *
       * This function looks for the column defined as 'autosave' and if its value
       * is true, the result of this input will be saved after each change via
       * ajax.
       */
      console.warn("BBB: Autosave is deprecated and not supported anymore");
      return false;
    };

    BikaListingTableView.prototype.on_workflow_button_click = function(event) {

      /*
       * Eventhandler for the workflow buttons
       */
      var $el, e, el, focus, form, form_id, transition;
      console.debug("°°° ListingTableView::on_workflow_button_click °°°");
      el = event.currentTarget;
      $el = $(el);
      form = $el.parents("form");
      form_id = $(form).attr("id");
      transition = $el.attr("transition");
      $(form).append("<input type='hidden' name='workflow_action_id' value='" + transition + "' />");
      if ($el.id === "submit_transition") {
        focus = $(".ajax_calculate_focus");
        if (focus.length > 0) {
          e = $(focus[0]);
          if ($(e).attr("focus_value") === $(e).val()) {
            $(e).removeAttr("focus_value");
            $(e).removeClass("ajax_calculate_focus");
          } else {
            $(e).parents("form").attr("submit_after_calculation", 1);
            event.preventDefault();
          }
        }
      }
      if ($el.attr("url") !== "") {
        form = $el.parents("form");
        $(form).attr("action", $(this).attr("url"));
        return $(form).submit();
      }
    };

    BikaListingTableView.prototype.on_contextmenu = function(event) {

      /*
       * Eventhandler for the table contextmenu
       */
      var $el, el, menu, table;
      console.debug("°°° ListingTableView::on_contextmenu °°°");
      event.preventDefault();
      el = event.currentTarget;
      $el = $(el);
      table = $el.parents("table.bika-listing-table");
      menu = this.make_context_menu(table);
      menu = $(menu).appendTo("body");
      return $(menu).css({
        "border": "1px solid #fff",
        "border-radius": ".25em",
        "background-color": "#fff",
        "position": "absolute",
        "top": event.pageY - 5,
        "left": event.pageX - 5
      });
    };

    BikaListingTableView.prototype.on_contextmenu_item_click = function(event) {

      /*
       * Eventhandler when an item was clicked in the contextmenu
       */
      var $el, col_id, el, form_id;
      console.debug("°°° ListingTableView::on_contextmenu_item_click °°°");
      el = event.currentTarget;
      $el = $(el);
      form_id = $el.attr("form_id");
      col_id = $el.attr("col_id");
      return this.toggle_column(form_id, col_id);
    };

    BikaListingTableView.prototype.on_search_field_keypress = function(event) {

      /*
       * Eventhandler for the search field
       */
      var $el, el, form, form_id, searchfield, searchterm;
      console.debug("°°° ListingTableView::on_search_field_keypress °°°");
      el = event.currentTarget;
      $el = $(el);
      if (event.which === 13) {
        event.preventDefault();
        form = $el.parents("form");
        form_id = form.attr("id");
        searchfield = $(".filter-search-input", form);
        searchterm = searchfield.val();
        return this.search(form_id, searchterm);
      }
    };

    BikaListingTableView.prototype.on_search_button_click = function(event) {

      /*
       * Eventhandler for the search field button
       */
      var $el, el;
      console.debug("°°° ListingTableView::on_search_button_click °°°");
      el = event.currentTarget;
      $el = $(el);
      return this.on_search_field_keypress(event);
    };

    BikaListingTableView.prototype.on_select_all_click = function(event) {

      /*
       * Eventhandler when the select all checkbox was clicked
       *
       * Controls the behavior when the 'select all' checkbox is clicked.
       * Checks/Unchecks all the row selection checkboxes and once done,
       * re-renders the workflow action buttons from the bottom of the list,
       * based on the allowed transitions for the currently selected items
       */
      var $el, checkboxes, el, table;
      console.debug("°°° ListingTableView::on_select_all_click °°°");
      el = event.currentTarget;
      $el = $(el);
      table = $el.parents("table.bika-listing-table");
      checkboxes = $(table).find("[id*='_cb_']");
      $(checkboxes).prop("checked", $el.prop("checked"));
      return this.render_transition_buttons(table);
    };

    BikaListingTableView.prototype.on_checkbox_click = function(event) {

      /*
       * Eventhandler when a Checkbox was clicked
       *
       * Controls the behavior when a checkbox of row selection is clicked.
       * Updates the status of the 'select all' checkbox accordingly and also
       * re-renders the workflow action buttons from the bottom of the list
       * based on the allowed transitions of the currently selected items
       */
      var $el, all, checkall, checked, el, table;
      console.debug("°°° ListingTableView::on_checkbox_click °°°");
      el = event.currentTarget;
      $el = $(el);
      table = $el.parents("table.bika-listing-table");
      checked = $("input[type='checkbox'][id*='_cb_']:checked");
      all = $("input[type='checkbox'][id*='_cb_']");
      checkall = $(table).find("input[id*='select_all']");
      checkall.prop("checked", checked.length === all.length);
      return this.render_transition_buttons(table);
    };

    BikaListingTableView.prototype.on_ajax_submit_start = function(event) {

      /*
       * Eventhandler for Ajax form submit
       */
      return console.debug("°°° ListingTableView::on_ajax_submit_start °°°");
    };

    BikaListingTableView.prototype.on_ajax_submit_end = function(event) {

      /*
       * Eventhandler for Ajax form submit
       */
      return console.debug("°°° ListingTableView::on_ajax_submit_end °°°");
    };

    BikaListingTableView.prototype.on_column_header_click = function(event) {

      /*
       * Eventhandler for Table Column Header
       */
      var $el, el, form, form_id, sort_index;
      console.debug("°°° ListingTableView::on_column_header_click °°°");
      el = event.currentTarget;
      $el = $(el);
      form = $el.parents("form");
      form_id = form.attr("id");
      sort_index = $el.attr("id").split("-")[1];
      return this.sort_column(form_id, sort_index);
    };

    BikaListingTableView.prototype.on_show_more_click = function(event) {

      /*
       * Eventhandler for the Table "Show More" Button
       */
      var $el, el, form_id, limit_from, pagesize;
      console.debug("°°° ListingTableView::on_show_more_click °°°");
      el = event.currentTarget;
      $el = $(el);
      event.preventDefault();
      form_id = $el.attr("data-form-id");
      pagesize = this.parse_int($el.attr("data-pagesize"));
      limit_from = this.parse_int($el.attr("data-limitfrom"));
      return this.show_more(form_id, pagesize, limit_from);
    };

    return BikaListingTableView;

  })();

}).call(this);
