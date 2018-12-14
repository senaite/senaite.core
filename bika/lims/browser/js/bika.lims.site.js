(function() {
  /* Please use this command to compile this file into the parent `js` directory:
      coffee --no-header -w -o ../ -c bika.lims.site.coffee
  */
  window.SiteView = class SiteView {
    constructor() {
      this.load = this.load.bind(this);
      /* INITIALIZERS */
      this.bind_eventhandler = this.bind_eventhandler.bind(this);
      this.init_client_add_overlay = this.init_client_add_overlay.bind(this);
      // here is where we'd populate the form controls, if we cared to.
      this.init_spinner = this.init_spinner.bind(this);
      this.init_client_combogrid = this.init_client_combogrid.bind(this);
      this.init_datepickers = this.init_datepickers.bind(this);
      this.init_referencedefinition = this.init_referencedefinition.bind(this);
      /* METHODS */
      this.get_portal_url = this.get_portal_url.bind(this);
      this.get_authenticator = this.get_authenticator.bind(this);
      this.portalAlert = this.portalAlert.bind(this);
      this.portal_alert = this.portal_alert.bind(this);
      this.log = this.log.bind(this);
      this.readCookie = this.readCookie.bind(this);
      this.read_cookie = this.read_cookie.bind(this);
      this.setCookie = this.setCookie.bind(this);
      this.set_cookie = this.set_cookie.bind(this);
      this.notificationPanel = this.notificationPanel.bind(this);
      this.notify_in_panel = this.notify_in_panel.bind(this);
      this.start_spinner = this.start_spinner.bind(this);
      this.stop_spinner = this.stop_spinner.bind(this);
      /* EVENT HANDLER */
      this.on_date_range_start_change = this.on_date_range_start_change.bind(this);
      this.on_date_range_end_change = this.on_date_range_end_change.bind(this);
      this.on_autocomplete_keydown = this.on_autocomplete_keydown.bind(this);
      this.on_at_integer_field_keyup = this.on_at_integer_field_keyup.bind(this);
      this.on_at_float_field_keyup = this.on_at_float_field_keyup.bind(this);
      this.on_numeric_field_paste = this.on_numeric_field_paste.bind(this);
      this.on_numeric_field_keypress = this.on_numeric_field_keypress.bind(this);
      this.on_reference_definition_list_change = this.on_reference_definition_list_change.bind(this);
      this.on_service_info_click = this.on_service_info_click.bind(this);
      this.on_ajax_start = this.on_ajax_start.bind(this);
      this.on_ajax_end = this.on_ajax_end.bind(this);
      this.on_ajax_error = this.on_ajax_error.bind(this);
    }

    load() {
      console.debug("SiteView::load");
      // load translations
      jarn.i18n.loadCatalog('senaite.core');
      this._ = window.jarn.i18n.MessageFactory("senaite.core");
      // initialze the loading spinner
      this.init_spinner();
      // initialze the client add overlay
      this.init_client_add_overlay();
      // initialze the client combogrid
      this.init_client_combogrid();
      // initialze datepickers
      this.init_datepickers();
      // initialze reference definition selection
      this.init_referencedefinition();
      // bind the event handler to the elements
      this.bind_eventhandler();
      // allowed keys for numeric fields
      return this.allowed_keys = [
        8, // backspace
        9, // tab
        13, // enter
        35, // end
        36, // home
        37, // left arrow
        39, // right arrow
        46, // delete - We don't support the del key in Opera because del == . == 46.
        44, // ,
        60, // <
        62, // >
        45, // -
        69, // E
        101, // e,
        61 // =
      ];
    }

    bind_eventhandler() {
      /*
       * Binds callbacks on elements
       *
       * N.B. We attach all the events to the form and refine the selector to
       * delegate the event: https://learn.jquery.com/events/event-delegation/
       */
      console.debug("SiteView::bind_eventhandler");
      // ReferenceSample selection changed
      $("body").on("change", "#ReferenceDefinition\\:list", this.on_reference_definition_list_change);
      // Numeric field events
      $("body").on("keypress", ".numeric", this.on_numeric_field_keypress);
      $("body").on("paste", ".numeric", this.on_numeric_field_paste);
      // AT field events
      $("body").on("keyup", "input[name*='\\:int\'], .ArchetypesIntegerWidget input", this.on_at_integer_field_keyup);
      $("body").on("keyup", "input[name*='\\:float\'], .ArchetypesDecimalWidget input", this.on_at_float_field_keyup);
      // Autocomplete events
      // XXX Where is this used?
      $("body").on("keydown", "input.autocomplete", this.on_autocomplete_keydown);
      // Date Range Filtering
      $("body").on("change", ".date_range_start", this.on_date_range_start_change);
      $("body").on("change", ".date_range_end", this.on_date_range_end_change);
      $("body").on("click", "a.service_info", this.on_service_info_click);
      // handle Ajax events
      $(document).on("ajaxStart", this.on_ajax_start);
      $(document).on("ajaxStop", this.on_ajax_end);
      return $(document).on("ajaxError", this.on_ajax_error);
    }

    init_client_add_overlay() {
      /*
       * Initialize Client Overlay
       */
      console.debug("SiteView::init_client_add_overlay");
      return $('a.add_client').prepOverlay({
        subtype: 'ajax',
        filter: 'head>*,#content>*:not(div.configlet),dl.portalMessage.error,dl.portalMessage.info',
        formselector: '#client-base-edit',
        closeselector: '[name="form.button.cancel"]',
        width: '70%',
        noform: 'close',
        config: {
          closeOnEsc: false,
          onLoad: function() {
            // manually remove remarks
            this.getOverlay().find('.ArchetypesRemarksWidget').remove();
          },
          onClose: function() {}
        }
      });
    }

    init_spinner() {
      /*
       * Initialize Spinner Overlay
       */
      console.debug("SiteView::init_spinner");
      // unbind default Plone loader
      $(document).unbind('ajaxStart');
      $(document).unbind('ajaxStop');
      $('#ajax-spinner').remove();
      // counter of active spinners
      this.counter = 0;
      // crate a spinner and append it to the body
      this.spinner = $(`<div id='bika-spinner'><img src='${this.get_portal_url()}/spinner.gif' alt=''/></div>`);
      return this.spinner.appendTo('body').hide();
    }

    init_client_combogrid() {
      /*
       * Initialize client combogrid, e.g. on the Client Add View
       */
      console.debug("SiteView::init_client_combogrid");
      return $("input[id*='ClientID']").combogrid({
        colModel: [
          {
            'columnName': 'ClientUID',
            'hidden': true
          },
          {
            'columnName': 'ClientID',
            'width': '20',
            'label': _('Client ID')
          },
          {
            'columnName': 'Title',
            'width': '80',
            'label': _('Title')
          }
        ],
        showOn: true,
        width: '450px',
        url: `${this.get_portal_url()}/getClients?_authenticator=${this.get_authenticator()}`,
        select: function(event, ui) {
          $(this).val(ui.item.ClientID);
          $(this).change();
          return false;
        }
      });
    }

    init_datepickers() {
      var curDate, dateFormat, limitString, y;
      /*
       * Initialize date pickers
       *
       * XXX Where are these event handlers used?
       */
      console.debug("SiteView::init_datepickers");
      curDate = new Date;
      y = curDate.getFullYear();
      limitString = '1900:' + y;
      dateFormat = this._('date_format_short_datepicker');
      if (dateFormat === 'date_format_short_datepicker') {
        dateFormat = 'yy-mm-dd';
      }
      $('input.datepicker_range').datepicker({
        /**
        This function defines a datepicker for a date range. Both input
        elements should be siblings and have the class 'date_range_start' and
        'date_range_end'.
        */
        showOn: 'focus',
        showAnim: '',
        changeMonth: true,
        changeYear: true,
        dateFormat: dateFormat,
        yearRange: limitString
      });
      $('input.datepicker').on('click', function() {
        console.warn("SiteView::datepicker.click: Refactor this event handler!");
        $(this).datepicker({
          showOn: 'focus',
          showAnim: '',
          changeMonth: true,
          changeYear: true,
          dateFormat: dateFormat,
          yearRange: limitString
        }).click(function() {
          $(this).attr('value', '');
        }).focus();
      });
      $('input.datepicker_nofuture').on('click', function() {
        console.warn("SiteView::datetimepicker_nofuture.click: Refactor this event handler!");
        $(this).datepicker({
          showOn: 'focus',
          showAnim: '',
          changeMonth: true,
          changeYear: true,
          maxDate: curDate,
          dateFormat: dateFormat,
          yearRange: limitString
        }).click(function() {
          $(this).attr('value', '');
        }).focus();
      });
      $('input.datepicker_2months').on('click', function() {
        console.warn("SiteView::datetimepicker_2months.click: Refactor this event handler!");
        $(this).datepicker({
          showOn: 'focus',
          showAnim: '',
          changeMonth: true,
          changeYear: true,
          maxDate: '+0d',
          numberOfMonths: 2,
          dateFormat: dateFormat,
          yearRange: limitString
        }).click(function() {
          $(this).attr('value', '');
        }).focus();
      });
      return $('input.datetimepicker_nofuture').on('click', function() {
        console.warn("SiteView::datetimepicker_nofuture.click: Refactor this event handler!");
        $(this).datetimepicker({
          showOn: 'focus',
          showAnim: '',
          changeMonth: true,
          changeYear: true,
          maxDate: curDate,
          dateFormat: dateFormat,
          yearRange: limitString,
          timeFormat: 'HH:mm',
          beforeShow: function() {
            setTimeout((function() {
              $('.ui-datepicker').css('z-index', 99999999999999);
            }), 0);
          }
        }).click(function() {
          $(this).attr('value', '');
        }).focus();
      });
    }

    init_referencedefinition() {
      /*
       * Initialize reference definition selection
       * XXX: When is this used?
       */
      console.debug("SiteView::init_referencedefinition");
      if ($('#ReferenceDefinition:list').val() !== '') {
        console.warn("SiteView::init_referencedefinition: Refactor this method!");
        return $('#ReferenceDefinition:list').change();
      }
    }

    get_portal_url() {
      /*
       * Return the portal url
       */
      return window.portal_url;
    }

    get_authenticator() {
      /*
       * Get the authenticator value
       */
      return $("input[name='_authenticator']").val();
    }

    portalAlert(html) {
      /*
       * BBB: Use portal_alert
       */
      console.warn("SiteView::portalAlert: Please use portal_alert method instead.");
      return this.portal_alert(html);
    }

    portal_alert(html) {
      var alerts;
      /*
       * Display a portal alert box
       */
      console.debug("SiteView::portal_alert");
      alerts = $('#portal-alert');
      if (alerts.length === 0) {
        $('#portal-header').append(`<div id='portal-alert' style='display:none'><div class='portal-alert-item'>${html}</div></div>`);
      } else {
        alerts.append(`<div class='portal-alert-item'>${html}</div>`);
      }
      alerts.fadeIn();
    }

    log(message) {
      /*
       * Log message via bika.lims.log
       */
      console.debug(`SiteView::log: message=${message}`);
      // XXX: This should actually log via XHR to the server, but seem to not work.
      return window.bika.lims.log(message);
    }

    readCookie(cname) {
      /*
       * BBB: Use read_cookie
       */
      console.warn("SiteView::readCookie: Please use read_cookie method instead.");
      return this.read_cookie(cname);
    }

    read_cookie(cname) {
      var c, ca, i, name;
      /*
       * Read cookie value
       */
      console.debug(`SiteView::read_cookie:${cname}`);
      name = cname + '=';
      ca = document.cookie.split(';');
      i = 0;
      while (i < ca.length) {
        c = ca[i];
        while (c.charAt(0) === ' ') {
          c = c.substring(1);
        }
        if (c.indexOf(name) === 0) {
          return c.substring(name.length, c.length);
        }
        i++;
      }
      return null;
    }

    setCookie(cname, cvalue) {
      /*
       * BBB: Use set_cookie
       */
      console.warn("SiteView::setCookie: Please use set_cookie method instead.");
      return this.set_cookie(cname, cvalue);
    }

    set_cookie(cname, cvalue) {
      var d, expires;
      /*
       * Read cookie value
       */
      console.debug(`SiteView::set_cookie:cname=${cname}, cvalue=${cvalue}`);
      d = new Date;
      d.setTime(d.getTime() + 1 * 24 * 60 * 60 * 1000);
      expires = 'expires=' + d.toUTCString();
      document.cookie = cname + '=' + cvalue + ';' + expires + ';path=/';
    }

    notificationPanel(data, mode) {
      /*
       * BBB: Use notify_in_panel
       */
      console.warn("SiteView::notificationPanel: Please use notfiy_in_panel method instead.");
      return this.notify_in_panel(data, mode);
    }

    notify_in_panel(data, mode) {
      var html;
      /*
       * Render an alert inside the content panel, e.g.in autosave of ARView
       */
      console.debug(`SiteView::notify_in_panel:data=${data}, mode=${mode}`);
      $('#panel-notification').remove();
      html = `<div id='panel-notification' style='display:none'><div class='${mode}-notification-item'>${data}</div></div>`;
      $('div#viewlet-above-content-title').append(html);
      $('#panel-notification').fadeIn('slow', 'linear', function() {
        setTimeout((function() {
          $('#panel-notification').fadeOut('slow', 'linear');
        }), 3000);
      });
    }

    start_spinner() {
      /*
       * Start Spinner Overlay
       */
      console.debug("SiteView::start_spinner");
      // increase the counter
      this.counter++;
      this.timer = setTimeout((() => {
        if (this.counter > 0) {
          this.spinner.show('fast');
        }
      }), 500);
    }

    stop_spinner() {
      /*
       * Stop Spinner Overlay
       */
      console.debug("SiteView::stop_spinner");
      // decrease the counter
      this.counter--;
      if (this.counter < 0) {
        this.counter = 0;
      }
      if (this.counter === 0) {
        clearTimeout(this.timer);
        this.spinner.stop();
        this.spinner.hide();
      }
    }

    on_date_range_start_change(event) {
      var $el, brother, date_element, el;
      /*
       * Eventhandler for Date Range Filtering
       *
       * 1. Go to Setup and enable advanced filter bar
       * 2. Set the start date of adv. filter bar, e.g. in AR listing
       */
      console.debug("°°° SiteView::on_date_range_start_change °°°");
      el = event.currentTarget;
      $el = $(el);
      // Set the min selectable end date to the start date
      date_element = $el.datepicker('getDate');
      brother = $el.siblings('.date_range_end');
      return $(brother).datepicker('option', 'minDate', date_element);
    }

    on_date_range_end_change(event) {
      var $el, brother, date_element, el;
      /*
       * Eventhandler for Date Range Filtering
       *
       * 1. Go to Setup and enable advanced filter bar
       * 2. Set the start date of adv. filter bar, e.g. in AR listing
       */
      console.debug("°°° SiteView::on_date_range_end_change °°°");
      el = event.currentTarget;
      $el = $(el);
      // Set the max selectable start date to the end date
      date_element = $el.datepicker('getDate');
      brother = $el.siblings('.date_range_start');
      return $(brother).datepicker('option', 'maxDate', date_element);
    }

    on_autocomplete_keydown(event) {
      var $el, availableTags, el, extractLast, split;
      /*
       * Eventhandler for Autocomplete fields
       *
       * XXX: Refactor if it is clear where this code is used!
       */
      console.debug("°°° SiteView::on_autocomplete_keydown °°°");
      el = event.currentTarget;
      $el = $(el);
      availableTags = $.parseJSON($('input.autocomplete').attr('voc'));
      split = function(val) {
        return val.split(/,\s*/);
      };
      extractLast = function(term) {
        return split(term).pop();
      };
      if (event.keyCode === $.ui.keyCode.TAB && $el.autocomplete('instance').menu.active) {
        event.preventDefault();
      }
      return;
      return $el.autocomplete({
        minLength: 0,
        source: function(request, response) {
          // delegate back to autocomplete, but extract the last term
          response($.ui.autocomplete.filter(availableTags, extractLast(request.term)));
        },
        focus: function() {
          // prevent value inserted on focus
          return false;
        },
        select: function(event, ui) {
          var terms;
          terms = split($el.val());
          // remove the current input
          terms.pop();
          // add the selected item
          terms.push(ui.item.value);
          // add placeholder to get the comma-and-space at the end
          terms.push('');
          this.el.val(terms.join(', '));
          return false;
        }
      });
    }

    on_at_integer_field_keyup(event) {
      var $el, el;
      /*
       * Eventhandler for AT integer fields
       */
      console.debug("°°° SiteView::on_at_integer_field_keyup °°°");
      el = event.currentTarget;
      $el = $(el);
      if (/\D/g.test($el.val())) {
        $el.val($el.val().replace(/\D/g, ''));
      }
    }

    on_at_float_field_keyup(event) {
      var $el, el;
      /*
       * Eventhandler for AT float fields
       */
      console.debug("°°° SiteView::on_at_float_field_keyup °°°");
      el = event.currentTarget;
      $el = $(el);
      if (/[^-.\d]/g.test($el.val())) {
        $el.val($el.val().replace(/[^.\d]/g, ''));
      }
    }

    on_numeric_field_paste(event) {
      var $el, el;
      /*
       * Eventhandler when the user pasted a value inside a numeric field.
       */
      console.debug("°°° SiteView::on_numeric_field_paste °°°");
      el = event.currentTarget;
      $el = $(el);
      // Wait (next cycle) for value popluation and replace commas.
      window.setTimeout((function() {
        $el.val($el.val().replace(',', '.'));
      }), 0);
    }

    on_numeric_field_keypress(event) {
      var $el, el, isAllowedKey, key;
      /*
       * Eventhandler when the user pressed a key inside a numeric field.
       */
      console.debug("°°° SiteView::on_numeric_field_keypress °°°");
      el = event.currentTarget;
      $el = $(el);
      key = event.which;
      isAllowedKey = this.allowed_keys.join(',').match(new RegExp(key));
      if (!key || 48 <= key && key <= 57 || isAllowedKey) {
        // Opera assigns values for control keys.
        // Wait (next cycle) for value popluation and replace commas.
        window.setTimeout((function() {
          $el.val($el.val().replace(',', '.'));
        }), 0);
        return;
      } else {
        event.preventDefault();
      }
    }

    on_reference_definition_list_change(event) {
      var $el, authenticator, el, option, uid;
      /*
       * Eventhandler when the user clicked on the reference defintion dropdown.
       *
       * 1. Add a ReferenceDefintion at /bika_setup/bika_referencedefinitions
       * 2. Add a Supplier in /bika_setup/bika_suppliers
       * 3. Add a ReferenceSample in /bika_setup/bika_suppliers/supplier-1/portal_factory/ReferenceSample
       *
       * The dropdown with the id="ReferenceDefinition:list" is rendered there.
       */
      console.debug("°°° SiteView::on_reference_definition_list_change °°°");
      el = event.currentTarget;
      $el = $(el);
      authenticator = this.get_authenticator();
      uid = $el.val();
      option = $el.children(':selected').html();
      if (uid === '') {
        // No reference definition selected;
        // render empty widget.
        $('#Blank').prop('checked', false);
        $('#Hazardous').prop('checked', false);
        $('.bika-listing-table').load('referenceresults', {
          '_authenticator': authenticator
        });
        return;
      }
      if (option.search(this._('(Blank)')) > -1 || option.search("(Blank)") > -1) {
        $('#Blank').prop('checked', true);
      } else {
        $('#Blank').prop('checked', false);
      }
      if (option.search(this._('(Hazardous)')) > -1 || option.search("(Hazardous)") > -1) {
        $('#Hazardous').prop('checked', true);
      } else {
        $('#Hazardous').prop('checked', false);
      }
      $('.bika-listing-table').load('referenceresults', {
        '_authenticator': authenticator,
        'uid': uid
      });
    }

    on_service_info_click(event) {
      var el;
      /*
       * Eventhandler when the service info icon was clicked
       */
      console.debug("°°° SiteView::on_service_info_click °°°");
      event.preventDefault();
      el = event.currentTarget;
      // https://jquerytools.github.io/documentation/overlay
      // https://github.com/plone/plone.app.jquerytools/blob/master/plone/app/jquerytools/browser/overlayhelpers.js
      $(el).prepOverlay({
        subtype: "ajax",
        width: '70%',
        filter: '#content>*:not(div#portal-column-content)',
        config: {
          closeOnClick: true,
          closeOnEsc: true,
          onBeforeLoad: function(event) {
            var overlay;
            overlay = this.getOverlay();
            return overlay.draggable();
          },
          onLoad: function(event) {
            // manually dispatch the DOMContentLoaded event, so that the ReactJS
            // component loads
            event = new Event("DOMContentLoaded", {});
            return window.document.dispatchEvent(event);
          }
        }
      });
      // workaround un-understandable overlay api
      return $(el).click();
    }

    on_ajax_start(event) {
      /*
       * Eventhandler if an global Ajax Request started
       */
      console.debug("°°° SiteView::on_ajax_start °°°");
      // start the loading spinner
      return this.start_spinner();
    }

    on_ajax_end(event) {
      /*
       * Eventhandler if an global Ajax Request ended
       */
      console.debug("°°° SiteView::on_ajax_end °°°");
      // stop the loading spinner
      return this.stop_spinner();
    }

    on_ajax_error(event, jqxhr, settings, thrownError) {
      /*
       * Eventhandler if an global Ajax Request error
       */
      console.debug("°°° SiteView::on_ajax_error °°°");
      // stop the loading spinner
      this.stop_spinner();
      return this.log(`Error at ${settings.url}: ${thrownError}`);
    }

  };

}).call(this);
