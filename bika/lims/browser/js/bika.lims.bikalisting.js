
/* Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.bikalisting.coffee
 */


/*
 * Controller class for Bika Listing Table view
 */

(function() {
  window.BikaListingTableView = function() {
    var autosave, build_typical_save_request, category_header_clicked, column_header_clicked, column_toggle_context_menu, column_toggle_context_menu_selection, filter_search_button_click, filter_search_keypress, listing_string_input_keypress, listing_string_select_changed, loadNewRemarksEventHandlers, load_transitions, loading_transitions, pagesize_change, positionTooltip, render_transition_buttons, save_elements, select_all_clicked, select_one_clicked, show_more_clicked, that, workflow_action_button_click;
    that = this;
    loading_transitions = false;
    show_more_clicked = function() {
      $('a.bika_listing_show_more').click(function(e) {
        var filter_options, filterbar, filters, filters1, filters2, formid, limit_from, pagesize, tbody, url;
        e.preventDefault();
        formid = $(this).attr('data-form-id');
        pagesize = parseInt($(this).attr('data-pagesize'));
        url = $(this).attr('data-ajax-url');
        limit_from = parseInt($(this).attr('data-limitfrom'));
        url = url.replace('_limit_from=', '_olf=');
        url += '&' + formid + '_limit_from=' + limit_from;
        $('#' + formid + ' a.bika_listing_show_more').fadeOut();
        tbody = $('table.bika-listing-table[form_id="' + formid + '"] tbody.item-listing-tbody');
        filter_options = [];
        filters1 = $('.bika_listing_filter_bar input[name][value!=""]');
        filters2 = $('.bika_listing_filter_bar select option:selected[value!=""]');
        filters = $.merge(filters1, filters2);
        $(filters).each(function(e) {
          var opt;
          opt = [$(this).attr('name'), $(this).val()];
          filter_options.push(opt);
        });
        filterbar = {};
        if (filter_options.length > 0) {
          filterbar.bika_listing_filter_bar = $.toJSON(filter_options);
        }
        $.post(url, filterbar).done(function(data) {
          var rows;
          try {
            rows = $('<html><table>' + data + '</table></html>').find('tr');
            $(tbody).append(rows);
            $('#' + formid + ' a.bika_listing_show_more').attr('data-limitfrom', limit_from + pagesize);
            loadNewRemarksEventHandlers();
          } catch (error) {
            e = error;
            $('#' + formid + ' a.bika_listing_show_more').hide();
            console.log(e);
          }
          load_transitions();
        }).fail(function() {
          $('#' + formid + ' a.bika_listing_show_more').hide();
          console.log('bika_listing_show_more failed');
        }).always(function() {
          var numitems;
          numitems = $('table.bika-listing-table[form_id="' + formid + '"] tbody.item-listing-tbody tr').length;
          $('#' + formid + ' span.number-items').html(numitems);
          if (numitems % pagesize === 0) {
            $('#' + formid + ' a.bika_listing_show_more').fadeIn();
          }
        });
      });
    };
    loadNewRemarksEventHandlers = function() {
      var pointer, txt1;
      $('a.add-remark').remove();
      txt1 = '<a href="#" class="add-remark"><img src="' + window.portal_url + '/++resource++bika.lims.images/comment_ico.png" title="' + _('Add Remark') + '")"></a>';
      pointer = $('.listing_remarks:contains(\'\')').closest('tr').prev().find('td.service_title span.before');
      $(pointer).append(txt1);
      $('a.add-remark').click(function(e) {
        var rmks;
        e.preventDefault();
        rmks = $(this).closest('tr').next('tr').find('td.remarks');
        if (rmks.length > 0) {
          rmks.toggle();
        }
      });
      $('td.remarks').hide();
    };
    column_header_clicked = function() {
      $('th.sortable').live('click', function() {
        var column_id, column_index, form, form_id, options, sort_on, sort_on_selector, sort_order, sort_order_selector, stored_form_action;
        form = $(this).parents('form');
        form_id = $(form).attr('id');
        column_id = this.id.split('-')[1];
        column_index = $(this).parent().children('th').index(this);
        sort_on_selector = '[name=' + form_id + '_sort_on]';
        sort_on = $(sort_on_selector).val();
        sort_order_selector = '[name=' + form_id + '_sort_order]';
        sort_order = $(sort_order_selector).val();
        if (sort_on === column_id) {
          if (sort_order === 'descending') {
            sort_order = 'ascending';
          } else {
            sort_order = 'descending';
          }
        } else {
          sort_on = column_id;
          sort_order = 'ascending';
        }
        $(sort_on_selector).val(sort_on);
        $(sort_order_selector).val(sort_order);
        stored_form_action = $(form).attr('action');
        $(form).attr('action', window.location.href);
        $(form).append('<input type=\'hidden\' name=\'table_only\' value=\'' + form_id + '\'>');
        options = {
          target: $(this).parents('table'),
          replaceTarget: true,
          data: form.formToArray()
        };
        form.ajaxSubmit(options);
        $('[name=\'table_only\']').remove();
        $(form).attr('action', stored_form_action);
      });
    };

    /*
    * Fetch allowed transitions for all the objects listed in bika_listing and
    * sets the value for the attribute 'data-valid_transitions' for each check
    * box next to each row.
    * The process requires an ajax call, so the function keeps checkboxes
    * disabled until the allowed transitions for the associated object are set.
     */
    load_transitions = function(blisting) {
      'use strict';
      var blistings, buttonspane, checkall, request_data, uids, wo_trans;
      if (blisting === '' || typeof blisting === 'undefined') {
        blistings = $('table.bika-listing-table');
        $(blistings).each(function(i) {
          load_transitions($(this));
        });
        return;
      }
      buttonspane = $(blisting).find('span.workflow_action_buttons');
      if (loading_transitions || $(buttonspane).length === 0) {
        return;
      }
      loading_transitions = true;
      uids = [];
      checkall = $("input[id*='select_all']");
      $(checkall).hide();
      wo_trans = $("input[data-valid_transitions='{}']");
      $(wo_trans).prop('disabled', true);
      $(wo_trans).each(function(e) {
        uids.push($(this).val());
      });
      if (uids.length > 0) {
        request_data = {
          _authenticator: $('input[name=\'_authenticator\']').val(),
          uid: $.toJSON(uids)
        };
        window.jsonapi_cache = window.jsonapi_cache || {};
        $.ajax({
          type: 'POST',
          dataType: 'json',
          url: window.portal_url + '/@@API/allowedTransitionsFor_many',
          data: request_data,
          success: function(data) {
            var el, i, trans, uid;
            if ('transitions' in data) {
              i = 0;
              while (i < data.transitions.length) {
                uid = data.transitions[i].uid;
                trans = data.transitions[i].transitions;
                el = $("input[id*='_cb_'][value='" + uid + "']");
                el.attr('data-valid_transitions', $.toJSON(trans));
                $(el).prop('disabled', false);
                i++;
              }
              $("input[id*='select_all']").fadeIn();
            }
          }
        });
      }
      loading_transitions = false;
    };

    /*
    * Controls the behavior when a checkbox of row selection is clicked.
    * Updates the status of the 'select all' checkbox accordingly and also
    * re-renders the workflow action buttons from the bottom of the list
    * based on the allowed transitions of the currently selected items
     */
    select_one_clicked = function() {
      'use strict';
      $('input[type=\'checkbox\'][id*=\'_cb_\']').live('click', function() {
        var all, blst, checkall, checked;
        blst = $(this).parents('table.bika-listing-table');
        render_transition_buttons(blst);
        checked = $('input[type=\'checkbox\'][id*=\'_cb_\']:checked');
        all = $('input[type=\'checkbox\'][id*=\'_cb_\']');
        checkall = $(blst).find('input[id*=\'select_all\']');
        checkall.prop('checked', checked.length === all.length);
      });
    };

    /*
    * Controls the behavior when the 'select all' checkbox is clicked.
    * Checks/Unchecks all the row selection checkboxes and once done,
    * re-renders the workflow action buttons from the bottom of the list,
    * based on the allowed transitions for the currently selected items
     */
    select_all_clicked = function() {
      'use strict';
      $('input[id*=\'select_all\']').live('click', function() {
        var blst, checkboxes;
        blst = $(this).parents('table.bika-listing-table');
        checkboxes = $(blst).find('[id*=\'_cb_\']');
        $(checkboxes).prop('checked', $(this).prop('checked'));
        render_transition_buttons(blst);
      });
    };

    /*
    * Re-generates the workflow action buttons from the bottom of the list in
    * accordance with the allowed transitions for the currently selected items.
    * This is, makes the intersection within all allowed transitions and adds
    * the corresponding buttons to the workflow action bar.
     */
    render_transition_buttons = function(blst) {
      'use strict';
      var _button, allowed_transitions, buttonspane, checked, custom_transitions, hidden_transitions, i, restricted_transitions, trans;
      buttonspane = $(blst).find('span.workflow_action_buttons');
      if ($(buttonspane).length === 0) {
        return;
      }
      allowed_transitions = [];
      hidden_transitions = $(blst).find('input[id="hide_transitions"]');
      hidden_transitions = $(hidden_transitions).length === 1 ? $(hidden_transitions).val() : '';
      hidden_transitions = hidden_transitions === '' ? [] : hidden_transitions.split(',');
      restricted_transitions = $(blst).find('input[id="restricted_transitions"]');
      restricted_transitions = $(restricted_transitions).length === 1 ? $(restricted_transitions).val() : '';
      restricted_transitions = restricted_transitions === '' ? [] : restricted_transitions.split(',');
      checked = $(blst).find("input[id*='_cb_']:checked");
      $(checked).each(function(e) {
        var transitions;
        transitions = $.parseJSON($(this).attr('data-valid_transitions'));
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
          transitions = transitions.filter(function(el) {
            return allowed_transitions.indexOf(el) > -1;
          });
        } else {
          allowed_transitions = transitions;
        }
        if (transitions.length > 0) {
          allowed_transitions = allowed_transitions.filter(function(el) {
            return transitions.indexOf(el) > -1;
          });
        }
      });
      $(buttonspane).html('');
      i = 0;
      while (i < allowed_transitions.length) {
        trans = allowed_transitions[i];
        _button = "<input id='" + trans['id'] + "_transition' class='context workflow_action_button action_button allowMultiSubmit' type='submit' value='" + (PMF(trans['title'])) + "' transition='" + trans['id'] + "' name='workflow_action_button'/>&nbsp;";
        $(buttonspane).append(_button);
        i++;
      }
      if ($(checked).length > 0) {
        custom_transitions = $(blst).find('input[type="hidden"].custom_transition');
        $(custom_transitions).each(function(i, e) {
          var _title, _trans, _url;
          _trans = $(e).val();
          _url = $(e).attr('url');
          _title = $(e).attr('title');
          _button = "<input id='" + _trans + "_transition' class='context workflow_action_button action_button allowMultiSubmit' type='submit' url='" + _url + "' value='" + _title + "' transition='" + _trans + "' name='workflow_action_button'/>&nbsp;";
          $(buttonspane).append(_button);
        });
      }
    };
    listing_string_input_keypress = function() {
      'use strict';
      $('.listing_string_entry,.listing_select_entry').live('keypress', function(event) {
        var blst, checkbox, enter, tr, uid;
        enter = 13;
        if (event.which === enter) {
          event.preventDefault();
        }
        uid = $(this).attr('uid');
        tr = $(this).parents('tr#folder-contents-item-' + uid);
        checkbox = tr.find('input[id$="_cb_' + uid + '"]');
        if ($(checkbox).length === 1) {
          blst = $(checkbox).parents('table.bika-listing-table');
          $(checkbox).prop('checked', true);
          render_transition_buttons(blst);
        }
      });
    };
    listing_string_select_changed = function() {
      $('.listing_select_entry').live('change', function() {
        var blst, checkbox, tr, uid;
        uid = $(this).attr('uid');
        tr = $(this).parents('tr#folder-contents-item-' + uid);
        checkbox = tr.find('input[id$="_cb_' + uid + '"]');
        if ($(checkbox).length === 1) {
          blst = $(checkbox).parents('table.bika-listing-table');
          $(checkbox).prop('checked', true);
          render_transition_buttons(blst);
        }
      });
    };
    pagesize_change = function() {
      $('select.pagesize').live('change', function() {
        var form, form_id, new_query, pagesize;
        form = $(this).parents('form');
        form_id = $(form).attr('id');
        pagesize = $(this).val();
        new_query = $.query.set(form_id + '_pagesize', pagesize).set(form_id + '_pagenumber', 1).toString();
        window.location = window.location.href.split('?')[0] + new_query;
      });
    };
    category_header_clicked = function() {
      $('.bika-listing-table th.collapsed').live('click', function() {
        if (!$(this).hasClass('ignore_bikalisting_default_handler')) {
          that.category_header_expand_handler(this);
        }
      });
      $('.bika-listing-table th.expanded').live('click', function() {
        if (!$(this).hasClass('ignore_bikalisting_default_handler')) {
          $(this).parent().nextAll('tr[cat=\'' + $(this).attr('cat') + '\']').toggle();
          if ($(this).hasClass('expanded')) {
            $(this).removeClass('expanded').addClass('collapsed');
          } else if ($(this).hasClass('collapsed')) {
            $(this).removeClass('collapsed').addClass('expanded');
          }
        }
      });
    };
    filter_search_keypress = function() {
      $('.filter-search-input').live('keypress', function(event) {
        var enter;
        enter = 13;
        if (event.which === enter) {
          $('.filter-search-button').click();
          return false;
        }
      });
    };
    filter_search_button_click = function() {
      $('.filter-search-button').live('click', function(event) {
        var form, form_id, stored_form_action, table, url;
        form = $(this).parents('form');
        form_id = $(form).attr('id');
        stored_form_action = $(form).attr('action');
        $(form).attr('action', window.location.href);
        $(form).append('<input type=\'hidden\' name=\'table_only\' value=\'' + form_id + '\'>');
        table = $(this).parents('table');
        url = window.location.href;
        $.post(url, form.formToArray()).done(function(data) {
          $(table).html(data);
          load_transitions();
          show_more_clicked();
        });
        $('[name="table_only"]').remove();
        $(form).attr('action', stored_form_action);
        return false;
      });
    };
    workflow_action_button_click = function() {
      $('.workflow_action_button').live('click', function(event) {
        var e, focus, form, form_id;
        form = $(this).parents('form');
        form_id = $(form).attr('id');
        $(form).append('<input type=\'hidden\' name=\'workflow_action_id\' value=\'' + $(this).attr('transition') + '\'>');
        if (this.id === 'submit_transition') {
          focus = $('.ajax_calculate_focus');
          if (focus.length > 0) {
            e = $(focus[0]);
            if ($(e).attr('focus_value') === $(e).val()) {
              $(e).removeAttr('focus_value');
              $(e).removeClass('ajax_calculate_focus');
            } else {
              $(e).parents('form').attr('submit_after_calculation', 1);
              event.preventDefault();
            }
          }
        }
        if ($(this).attr('url') !== '') {
          form = $(this).parents('form');
          $(form).attr('action', $(this).attr('url'));
          $(form).submit();
        }
      });
    };
    column_toggle_context_menu = function() {
      $('th[id^="foldercontents-"]').live('contextmenu', function(event) {
        var col, col_id, col_title, enabled, form_id, i, portal_url, sorted_toggle_cols, toggle_cols, txt;
        event.preventDefault();
        form_id = $(this).parents('form').attr('id');
        portal_url = window.portal_url;
        toggle_cols = $('#' + form_id + '_toggle_cols').val();
        if (toggle_cols === '' || toggle_cols === void 0 || toggle_cols === null) {
          return false;
        }
        sorted_toggle_cols = [];
        $.each($.parseJSON(toggle_cols), function(col_id, v) {
          v['id'] = col_id;
          sorted_toggle_cols.push(v);
        });
        sorted_toggle_cols.sort(function(a, b) {
          var titleA, titleB;
          titleA = a['title'].toLowerCase();
          titleB = b['title'].toLowerCase();
          if (titleA < titleB) {
            return -1;
          }
          if (titleA > titleB) {
            return 1;
          }
          return 0;
        });
        txt = '<div class="tooltip"><table class="contextmenu" cellpadding="0" cellspacing="0">';
        txt = txt + '<tr><th colspan=\'2\'>' + _('Display columns') + '</th></tr>';
        i = 0;
        while (i < sorted_toggle_cols.length) {
          col = sorted_toggle_cols[i];
          col_id = col['id'];
          col_title = _(col['title']);
          enabled = $('#foldercontents-' + col_id + '-column');
          if (enabled.length > 0) {
            txt = txt + '<tr class=\'enabled\' col_id=\'' + col_id + '\' form_id=\'' + form_id + '\'>';
            txt = txt + '<td>';
            txt = txt + '<img style=\'height:1em;\' src=\'' + portal_url + '/++resource++bika.lims.images/ok.png\'/>';
            txt = txt + '</td>';
            txt = txt + '<td>' + col_title + '</td></tr>';
          } else {
            txt = txt + '<tr col_id=\'' + col_id + '\' form_id=\'' + form_id + '\'>';
            txt = txt + '<td>&nbsp;</td>';
            txt = txt + '<td>' + col_title + '</td></tr>';
          }
          i++;
        }
        txt = txt + '<tr col_id=\'' + _('All') + '\' form_id=\'' + form_id + '\'>';
        txt = txt + '<td style=\'border-top:1px solid #ddd\'>&nbsp;</td>';
        txt = txt + '<td style=\'border-top:1px solid #ddd\'>' + _('All') + '</td></tr>';
        txt = txt + '<tr col_id=\'' + _('Default') + '\' form_id=\'' + form_id + '\'>';
        txt = txt + '<td>&nbsp;</td>';
        txt = txt + '<td>' + _('Default') + '</td></tr>';
        txt = txt + '</table></div>';
        $(txt).appendTo('body');
        positionTooltip(event);
        return false;
      });
    };
    column_toggle_context_menu_selection = function() {
      $('.contextmenu tr').live('click', function(event) {
        var col_id, col_title, cookie, cookie_key, enabled, form, form_id, toggle_cols;
        form_id = $(this).attr('form_id');
        form = $('form#' + form_id);
        col_id = $(this).attr('col_id');
        col_title = $(this).text();
        enabled = $(this).hasClass('enabled');
        cookie = readCookie('toggle_cols');
        cookie = $.parseJSON(cookie);
        cookie_key = $(form[0].portal_type).val() + form_id;
        if (cookie === null || cookie === void 0) {
          cookie = {};
        }
        if (col_id === _('Default')) {
          delete cookie[cookie_key];
          createCookie('toggle_cols', $.toJSON(cookie), 365);
        } else if (col_id === _('All')) {
          toggle_cols = [];
          $.each($.parseJSON($('#' + form_id + '_toggle_cols').val()), function(i, v) {
            toggle_cols.push(i);
          });
          cookie[cookie_key] = toggle_cols;
          createCookie('toggle_cols', $.toJSON(cookie), 365);
        } else {
          toggle_cols = cookie[cookie_key];
          if (toggle_cols === null || toggle_cols === void 0) {
            toggle_cols = [];
            $.each($.parseJSON($('#' + form_id + '_toggle_cols').val()), function(i, v) {
              if (!(col_id === i && enabled) && v['toggle']) {
                toggle_cols.push(i);
              }
            });
          } else {
            if (enabled) {
              toggle_cols.splice(toggle_cols.indexOf(col_id), 1);
            } else {
              toggle_cols.push(col_id);
            }
          }
          cookie[cookie_key] = toggle_cols;
          createCookie('toggle_cols', $.toJSON(cookie), 365);
        }
        $(form).attr('action', window.location.href);
        $('.tooltip').remove();
        form.submit();
        return false;
      });
    };
    positionTooltip = function(event) {
      var tPosX, tPosY;
      tPosX = event.pageX - 5;
      tPosY = event.pageY - 5;
      $('div.tooltip').css({
        'border': '1px solid #fff',
        'border-radius': '.25em',
        'background-color': '#fff',
        'position': 'absolute',
        'top': tPosY,
        'left': tPosX
      });
    };
    autosave = function() {

      /*
      This function looks for the column defined as 'autosave' and if
      its value is true, the result of this input will be saved after each
      change via ajax.
       */
      $('select.autosave, input.autosave').not('[type="hidden"]').each(function(i) {
        $(this).change(function() {
          var pointer;
          pointer = this;
          build_typical_save_request(pointer);
        });
      });
    };
    build_typical_save_request = function(pointer) {

      /*
       * Build an array with the data to be saved for the typical data fields.
       * @pointer is the object which has been modified and we want to save its new data.
       */
      var fieldname, fieldvalue, requestdata, tr, uid;
      fieldvalue = void 0;
      fieldname = void 0;
      requestdata = {};
      uid = void 0;
      tr = void 0;
      fieldvalue = $(pointer).val();
      if ($(pointer).is(':checkbox')) {
        fieldvalue = $(pointer).is(':checked');
      }
      fieldname = $(pointer).attr('field');
      tr = $(pointer).closest('tr');
      uid = $(pointer).attr('uid');
      requestdata[fieldname] = fieldvalue;
      requestdata['obj_uid'] = uid;
      save_elements(requestdata, tr);
    };
    save_elements = function(requestdata, tr) {

      /*
       * Given a dict with a fieldname and a fieldvalue, save this data via ajax petition.
       * @requestdata should has the format {fieldname=fieldvalue, uid=xxxx} -> { ReportDryMatter=false, uid=xxx}.
       */
      var name, url;
      url = window.location.href.replace('/base_view', '');
      name = $(tr).attr('title');
      $.ajax({
        type: 'POST',
        url: window.portal_url + '/@@API/update',
        data: requestdata
      }).done(function(data) {
        var msg;
        if (data !== null && data['success'] === true) {
          bika.lims.SiteView.notificationPanel(name + ' updated successfully', 'succeed');
        } else {
          bika.lims.SiteView.notificationPanel('Error while updating ' + name, 'error');
          msg = 'Error while updating ' + name;
          console.warn(msg);
          window.bika.lims.error(msg);
        }
      }).fail(function() {
        var msg;
        bika.lims.SiteView.notificationPanel('Error while updating ' + name, 'error');
        msg = 'Error while updating ' + name;
        console.warn(msg);
        window.bika.lims.error(msg);
      });
    };
    that.load = function() {
      column_header_clicked();
      load_transitions();
      select_one_clicked();
      select_all_clicked();
      listing_string_input_keypress();
      listing_string_select_changed();
      pagesize_change();
      category_header_clicked();
      filter_search_keypress();
      filter_search_button_click();
      workflow_action_button_click();
      column_toggle_context_menu();
      column_toggle_context_menu_selection();
      show_more_clicked();
      autosave();
      $('*').click(function() {
        if ($('.tooltip').length > 0) {
          $('.tooltip').remove();
        }
      });
    };
    that.category_header_expand_handler = function(element) {
      var ajax_categories_enabled, cat_title, def, form_id, options, placeholder, url;
      def = $.Deferred();
      form_id = $(element).parents('[form_id]').attr('form_id');
      cat_title = $(element).attr('cat');
      url = $('input[name=\'ajax_categories_url\']').length > 0 ? $('input[name=\'ajax_categories_url\']').val() : window.location.href.split('?')[0];
      placeholder = $('tr[data-ajax_category=\'' + cat_title + '\']');
      if ($(element).hasClass('expanded')) {
        def.resolve();
        return def.promise();
      }
      ajax_categories_enabled = $('input[name=\'ajax_categories\']');
      if (ajax_categories_enabled.length > 0 && placeholder.length > 0) {
        options = {};
        options['ajax_category_expand'] = 1;
        options['cat'] = cat_title;
        options['form_id'] = form_id;
        url = $('input[name=\'ajax_categories_url\']').length > 0 ? $('input[name=\'ajax_categories_url\']').val() : url;
        if ($('.review_state_selector a.selected').length > 0) {
          options['review_state'] = $('.review_state_selector a.selected')[0].id;
        }
        $.ajax({
          url: url,
          data: options
        }).done(function(data) {
          var rows;
          rows = $('<table>' + data + '</table>').find('tr');
          $('[form_id=\'' + form_id + '\'] tr[data-ajax_category=\'' + cat_title + '\']').replaceWith(rows);
          $(element).removeClass('collapsed').addClass('expanded');
          def.resolve();
          load_transitions();
        });
      } else {
        $(element).parent().nextAll('tr[cat=\'' + $(element).attr('cat') + '\']').toggle(true);
        $(element).removeClass('collapsed').addClass('expanded');
        def.resolve();
      }
      return def.promise();
    };
  };

}).call(this);
