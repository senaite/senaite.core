(function() {
  /* Please use this command to compile this file into the parent `js` directory:
      coffee --no-header -w -o ../ -c bika.lims.site.coffee
  */
  window.SiteView = class SiteView {
    constructor() {
      this.load = this.load.bind(this);
      /* INITIALIZERS */
      this.bind_eventhandler = this.bind_eventhandler.bind(this);
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
      /* EVENT HANDLER */
      this.on_at_integer_field_keyup = this.on_at_integer_field_keyup.bind(this);
      this.on_at_float_field_keyup = this.on_at_float_field_keyup.bind(this);
      this.on_numeric_field_paste = this.on_numeric_field_paste.bind(this);
      this.on_numeric_field_keypress = this.on_numeric_field_keypress.bind(this);
      this.on_reference_definition_list_change = this.on_reference_definition_list_change.bind(this);
      this.on_overlay_panel_click = this.on_overlay_panel_click.bind(this);
    }

    load() {
      console.debug("SiteView::load");
      // initialze reference definition selection
      // @init_referencedefinition()

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
      $("body").on("click", "a.overlay_panel", this.on_overlay_panel_click);
      // Show loader on Ajax events
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
      console.warn("SiteView::get_authenticator: Please use site.authenticator instead");
      return window.site.authenticator();
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
      console.warn("SiteView::readCookie: Please use site.read_cookie instead");
      return window.site.read_cookie(cname);
    }

    read_cookie(cname) {
      /*
       * Read cookie value
       */
      console.warn("SiteView::read_cookie. Please use site.read_cookie instead");
      return window.site.read_cookie(cname);
    }

    setCookie(cname, cvalue) {
      /*
       * BBB: Use set_cookie
       */
      console.warn("SiteView::setCookie. Please use site.set_cookie instead");
      return window.site.set_cookie(cname, cvalue);
    }

    set_cookie(cname, cvalue) {
      /*
       * Read cookie value
       */
      console.warn("SiteView::set_cookie. Please use site.set_cookie instead");
      window.site.set_cookie(cname, cvalue);
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
      if (option.search(_t('(Blank)')) > -1 || option.search("(Blank)") > -1) {
        $('#Blank').prop('checked', true);
      } else {
        $('#Blank').prop('checked', false);
      }
      if (option.search(_t('(Hazardous)')) > -1 || option.search("(Hazardous)") > -1) {
        $('#Hazardous').prop('checked', true);
      } else {
        $('#Hazardous').prop('checked', false);
      }
      $('.bika-listing-table').load('referenceresults', {
        '_authenticator': authenticator,
        'uid': uid
      });
    }

    on_overlay_panel_click(event) {
      var el;
      /*
       * Eventhandler when the service info icon was clicked
       */
      console.debug("°°° SiteView::on_overlay_panel_click °°°");
      event.preventDefault();
      el = event.currentTarget;
      // https://jquerytools.github.io/documentation/overlay
      // https://github.com/plone/plone.app.jquerytools/blob/master/plone/app/jquerytools/browser/overlayhelpers.js
      $(el).prepOverlay({
        subtype: "ajax",
        width: '80%',
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

  };

}).call(this);
