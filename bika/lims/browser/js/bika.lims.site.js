
/* Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.site.coffee
 */

(function() {
  var bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  window.SiteView = (function() {
    function SiteView() {
      this.on_service_info_click = bind(this.on_service_info_click, this);
      this.on_reference_definition_list_change = bind(this.on_reference_definition_list_change, this);
      this.on_numeric_field_keypress = bind(this.on_numeric_field_keypress, this);
      this.on_numeric_field_paste = bind(this.on_numeric_field_paste, this);
      this.on_at_float_field_keyup = bind(this.on_at_float_field_keyup, this);
      this.on_at_integer_field_keyup = bind(this.on_at_integer_field_keyup, this);
      this.on_autocomplete_keydown = bind(this.on_autocomplete_keydown, this);
      this.notify_in_panel = bind(this.notify_in_panel, this);
      this.notificationPanel = bind(this.notificationPanel, this);
      this.set_cookie = bind(this.set_cookie, this);
      this.setCookie = bind(this.setCookie, this);
      this.read_cookie = bind(this.read_cookie, this);
      this.readCookie = bind(this.readCookie, this);
      this.log = bind(this.log, this);
      this.portal_alert = bind(this.portal_alert, this);
      this.portalAlert = bind(this.portalAlert, this);
      this.get_authenticator = bind(this.get_authenticator, this);
      this.get_portal_url = bind(this.get_portal_url, this);
      this.init_referencedefinition = bind(this.init_referencedefinition, this);
      this.init_datepickers = bind(this.init_datepickers, this);
      this.bind_eventhandler = bind(this.bind_eventhandler, this);
      this.load = bind(this.load, this);
    }

    SiteView.prototype.load = function() {
      console.debug("SiteView::load");
      jarn.i18n.loadCatalog('senaite.core');
      this._ = window.jarn.i18n.MessageFactory("senaite.core");
      this.init_datepickers();
      this.init_referencedefinition();
      this.bind_eventhandler();
      return this.allowed_keys = [8, 9, 13, 35, 36, 37, 39, 46, 44, 60, 62, 45, 69, 101, 61];
    };


    /* INITIALIZERS */

    SiteView.prototype.bind_eventhandler = function() {

      /*
       * Binds callbacks on elements
       *
       * N.B. We attach all the events to the form and refine the selector to
       * delegate the event: https://learn.jquery.com/events/event-delegation/
       */
      console.debug("SiteView::bind_eventhandler");
      $("body").on("change", "#ReferenceDefinition\\:list", this.on_reference_definition_list_change);
      $("body").on("keypress", ".numeric", this.on_numeric_field_keypress);
      $("body").on("paste", ".numeric", this.on_numeric_field_paste);
      $("body").on("keyup", "input[name*='\\:int\'], .ArchetypesIntegerWidget input", this.on_at_integer_field_keyup);
      $("body").on("keyup", "input[name*='\\:float\'], .ArchetypesDecimalWidget input", this.on_at_float_field_keyup);
      $("body").on("keydown", "input.autocomplete", this.on_autocomplete_keydown);
      $("body").on("click", "a.service_info", this.on_service_info_click);
      return $(document).on({
        ajaxStart: function() {
          $("body").addClass("loading");
        },
        ajaxStop: function() {
          $("body").removeClass("loading");
        },
        ajaxError: function() {
          $("body").removeClass("loading");
        }
      });
    };

    SiteView.prototype.init_datepickers = function() {

      /*
       * Initialize date pickers
       *
       * This is used for date pickers not bound to a DateTime widget
       */
      var config, curDate, dateFormat, lang, limitString, y;
      console.debug("SiteView::init_datepickers");
      curDate = new Date;
      y = curDate.getFullYear();
      limitString = '1900:' + y;
      dateFormat = this._('date_format_short_datepicker');
      if (dateFormat === 'date_format_short_datepicker') {
        dateFormat = 'yy-mm-dd';
      }
      lang = jarn.i18n.currentLanguage;
      config = $.datepicker.regional[lang] || $.datepicker.regional[''];
      $("input[class*='datepicker']").datepicker(Object.assign(config, {
        showOn: 'focus',
        showAnim: '',
        changeMonth: true,
        changeYear: true,
        dateFormat: dateFormat,
        numberOfMonths: 1,
        yearRange: limitString
      }));
      $('input.datepicker_2months').datepicker("option", "numberOfMonths", 2);
      $('input.datepicker_2months').datepicker("option", "maxDate", "+0d");
      $('input.datepicker_nofuture').datepicker("option", "maxDate", curDate);
      $('input.datetimepicker_nofuture').datepicker("option", "maxDate", curDate);
      return $('input.datetimepicker_nofuture').datepicker("option", "timeFormat", "HH:mm");
    };

    SiteView.prototype.init_referencedefinition = function() {

      /*
       * Initialize reference definition selection
       * XXX: When is this used?
       */
      console.debug("SiteView::init_referencedefinition");
      if ($('#ReferenceDefinition:list').val() !== '') {
        console.warn("SiteView::init_referencedefinition: Refactor this method!");
        return $('#ReferenceDefinition:list').change();
      }
    };


    /* METHODS */

    SiteView.prototype.get_portal_url = function() {

      /*
       * Return the portal url
       */
      return window.portal_url;
    };

    SiteView.prototype.get_authenticator = function() {

      /*
       * Get the authenticator value
       */
      return $("input[name='_authenticator']").val();
    };

    SiteView.prototype.portalAlert = function(html) {

      /*
       * BBB: Use portal_alert
       */
      console.warn("SiteView::portalAlert: Please use portal_alert method instead.");
      return this.portal_alert(html);
    };

    SiteView.prototype.portal_alert = function(html) {

      /*
       * Display a portal alert box
       */
      var alerts;
      console.debug("SiteView::portal_alert");
      alerts = $('#portal-alert');
      if (alerts.length === 0) {
        $('#portal-header').append("<div id='portal-alert' style='display:none'><div class='portal-alert-item'>" + html + "</div></div>");
      } else {
        alerts.append("<div class='portal-alert-item'>" + html + "</div>");
      }
      alerts.fadeIn();
    };

    SiteView.prototype.log = function(message) {

      /*
       * Log message via bika.lims.log
       */
      console.debug("SiteView::log: message=" + message);
      return window.bika.lims.log(message);
    };

    SiteView.prototype.readCookie = function(cname) {

      /*
       * BBB: Use read_cookie
       */
      console.warn("SiteView::readCookie: Please use read_cookie method instead.");
      return this.read_cookie(cname);
    };

    SiteView.prototype.read_cookie = function(cname) {

      /*
       * Read cookie value
       */
      var c, ca, i, name;
      console.debug("SiteView::read_cookie:" + cname);
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
    };

    SiteView.prototype.setCookie = function(cname, cvalue) {

      /*
       * BBB: Use set_cookie
       */
      console.warn("SiteView::setCookie: Please use set_cookie method instead.");
      return this.set_cookie(cname, cvalue);
    };

    SiteView.prototype.set_cookie = function(cname, cvalue) {

      /*
       * Read cookie value
       */
      var d, expires;
      console.debug("SiteView::set_cookie:cname=" + cname + ", cvalue=" + cvalue);
      d = new Date;
      d.setTime(d.getTime() + 1 * 24 * 60 * 60 * 1000);
      expires = 'expires=' + d.toUTCString();
      document.cookie = cname + '=' + cvalue + ';' + expires + ';path=/';
    };

    SiteView.prototype.notificationPanel = function(data, mode) {

      /*
       * BBB: Use notify_in_panel
       */
      console.warn("SiteView::notificationPanel: Please use notfiy_in_panel method instead.");
      return this.notify_in_panel(data, mode);
    };

    SiteView.prototype.notify_in_panel = function(data, mode) {

      /*
       * Render an alert inside the content panel, e.g.in autosave of ARView
       */
      var html;
      console.debug("SiteView::notify_in_panel:data=" + data + ", mode=" + mode);
      $('#panel-notification').remove();
      html = "<div id='panel-notification' style='display:none'><div class='" + mode + "-notification-item'>" + data + "</div></div>";
      $('div#viewlet-above-content-title').append(html);
      $('#panel-notification').fadeIn('slow', 'linear', function() {
        setTimeout((function() {
          $('#panel-notification').fadeOut('slow', 'linear');
        }), 3000);
      });
    };


    /* EVENT HANDLER */

    SiteView.prototype.on_autocomplete_keydown = function(event) {

      /*
       * Eventhandler for Autocomplete fields
       *
       * XXX: Refactor if it is clear where this code is used!
       */
      var $el, availableTags, el, extractLast, split;
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
          response($.ui.autocomplete.filter(availableTags, extractLast(request.term)));
        },
        focus: function() {
          return false;
        },
        select: function(event, ui) {
          var terms;
          terms = split($el.val());
          terms.pop();
          terms.push(ui.item.value);
          terms.push('');
          this.el.val(terms.join(', '));
          return false;
        }
      });
    };

    SiteView.prototype.on_at_integer_field_keyup = function(event) {

      /*
       * Eventhandler for AT integer fields
       */
      var $el, el;
      console.debug("°°° SiteView::on_at_integer_field_keyup °°°");
      el = event.currentTarget;
      $el = $(el);
      if (/\D/g.test($el.val())) {
        $el.val($el.val().replace(/\D/g, ''));
      }
    };

    SiteView.prototype.on_at_float_field_keyup = function(event) {

      /*
       * Eventhandler for AT float fields
       */
      var $el, el;
      console.debug("°°° SiteView::on_at_float_field_keyup °°°");
      el = event.currentTarget;
      $el = $(el);
      if (/[^-.\d]/g.test($el.val())) {
        $el.val($el.val().replace(/[^.\d]/g, ''));
      }
    };

    SiteView.prototype.on_numeric_field_paste = function(event) {

      /*
       * Eventhandler when the user pasted a value inside a numeric field.
       */
      var $el, el;
      console.debug("°°° SiteView::on_numeric_field_paste °°°");
      el = event.currentTarget;
      $el = $(el);
      window.setTimeout((function() {
        $el.val($el.val().replace(',', '.'));
      }), 0);
    };

    SiteView.prototype.on_numeric_field_keypress = function(event) {

      /*
       * Eventhandler when the user pressed a key inside a numeric field.
       */
      var $el, el, isAllowedKey, key;
      console.debug("°°° SiteView::on_numeric_field_keypress °°°");
      el = event.currentTarget;
      $el = $(el);
      key = event.which;
      isAllowedKey = this.allowed_keys.join(',').match(new RegExp(key));
      if (!key || 48 <= key && key <= 57 || isAllowedKey) {
        window.setTimeout((function() {
          $el.val($el.val().replace(',', '.'));
        }), 0);
        return;
      } else {
        event.preventDefault();
      }
    };

    SiteView.prototype.on_reference_definition_list_change = function(event) {

      /*
       * Eventhandler when the user clicked on the reference defintion dropdown.
       *
       * 1. Add a ReferenceDefintion at /bika_setup/bika_referencedefinitions
       * 2. Add a Supplier in /bika_setup/bika_suppliers
       * 3. Add a ReferenceSample in /bika_setup/bika_suppliers/supplier-1/portal_factory/ReferenceSample
       *
       * The dropdown with the id="ReferenceDefinition:list" is rendered there.
       */
      var $el, authenticator, el, option, uid;
      console.debug("°°° SiteView::on_reference_definition_list_change °°°");
      el = event.currentTarget;
      $el = $(el);
      authenticator = this.get_authenticator();
      uid = $el.val();
      option = $el.children(':selected').html();
      if (uid === '') {
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
    };

    SiteView.prototype.on_service_info_click = function(event) {

      /*
       * Eventhandler when the service info icon was clicked
       */
      var el;
      console.debug("°°° SiteView::on_service_info_click °°°");
      event.preventDefault();
      el = event.currentTarget;
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
            event = new Event("DOMContentLoaded", {});
            return window.document.dispatchEvent(event);
          }
        }
      });
      return $(el).click();
    };

    return SiteView;

  })();

}).call(this);
