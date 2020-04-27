
/* Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../js -c email.coffee
 */

(function() {
  var EmailController,
    bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  document.addEventListener("DOMContentLoaded", function() {
    var controller;
    console.debug("*** Loading Email Controller");
    controller = new EmailController();
    return controller.initialize();
  });

  EmailController = (function() {
    function EmailController() {
      this.on_attachments_select = bind(this.on_attachments_select, this);
      this.on_add_attachments_click = bind(this.on_add_attachments_click, this);
      this.toggle_attachments_container = bind(this.toggle_attachments_container, this);
      this.bind_eventhandler = bind(this.bind_eventhandler, this);
      this.bind_eventhandler();
      return this;
    }

    EmailController.prototype.initialize = function() {
      console.debug("senaite.impress:Email::initialize");
      return this.init_overlays();
    };

    EmailController.prototype.init_overlays = function() {

      /*
       * Initialize all overlays for later loading
       *
       */
      console.debug("senaite.impress:Email::init_overlays");
      return $("a.attachment-link,a.report-link").prepOverlay({
        subtype: "iframe",
        config: {
          closeOnClick: true,
          closeOnEsc: true,
          onLoad: function(event) {
            var iframe, overlay;
            overlay = this.getOverlay();
            iframe = overlay.find("iframe");
            return iframe.css({
              "background": "white"
            });
          }
        }
      });
    };

    EmailController.prototype.bind_eventhandler = function() {

      /*
       * Binds callbacks on elements
       *
       * N.B. We attach all the events to the body and refine the selector to
       * delegate the event: https://learn.jquery.com/events/event-delegation/
       *
       */
      console.debug("senaite.impress::bind_eventhandler");
      $("body").on("click", "#add-attachments", this.on_add_attachments_click);
      return $("body").on("change", ".attachments input[type='checkbox']", this.on_attachments_select);
    };

    EmailController.prototype.get_base_url = function() {

      /*
       * Calculate the current base url
       */
      return document.URL.split("?")[0];
    };

    EmailController.prototype.get_api_url = function(endpoint) {

      /*
       * Build API URL for the given endpoint
       * @param {string} endpoint
       * @returns {string}
       */
      var base_url;
      base_url = this.get_base_url();
      return base_url + "/" + endpoint;
    };

    EmailController.prototype.ajax_fetch = function(endpoint, init) {

      /*
       * Call resource on the server
       * @param {string} endpoint
       * @param {object} options
       * @returns {Promise}
       */
      var request, url;
      url = this.get_api_url(endpoint);
      if (init == null) {
        init = {};
      }
      if (init.method == null) {
        init.method = "POST";
      }
      if (init.credentials == null) {
        init.credentials = "include";
      }
      if (init.body == null) {
        init.body = null;
      }
      if (init.header == null) {
        init.header = null;
      }
      console.info("Email::fetch:endpoint=" + endpoint + " init=", init);
      request = new Request(url, init);
      return fetch(request).then(function(response) {
        return response.json();
      });
    };

    EmailController.prototype.is_visible = function(element) {

      /*
       * Checks if the element is visible
       */
      if ($(element).css("display") === "none") {
        return false;
      }
      return true;
    };

    EmailController.prototype.toggle_attachments_container = function(toggle) {
      var button, container, visible;
      if (toggle == null) {
        toggle = null;
      }

      /*
       * Toggle the visibility of the attachments container
       */
      button = $("#add-attachments");
      container = $("#additional-attachments-container");
      visible = this.is_visible(container);
      if (toggle !== null) {
        visible = toggle ? false : true;
      }
      if (visible === true) {
        container.hide();
        return button.text("+");
      } else {
        container.show();
        return button.text("-");
      }
    };

    EmailController.prototype.update_size_info = function(data) {

      /*
       * Update the total size of the selected attachments
       */
      var unit;
      if (!data) {
        console.warn("No valid size information: ", data);
        return null;
      }
      unit = "kB";
      $("#attachment-files").text("" + data.files);
      if (data.limit_exceeded) {
        $("#email-size").addClass("text-danger");
        $("#email-size").text(data.size + " " + unit + " > " + data.limit + " " + unit);
        return $("input[name='send']").prop("disabled", true);
      } else {
        $("#email-size").removeClass("text-danger");
        $("#email-size").text(data.size + " " + unit);
        return $("input[name='send']").prop("disabled", false);
      }
    };

    EmailController.prototype.on_add_attachments_click = function(event) {
      console.debug("°°° Email::on_add_attachments_click");
      event.preventDefault();
      return this.toggle_attachments_container();
    };

    EmailController.prototype.on_attachments_select = function(event) {
      var form, form_data, init;
      console.debug("°°° Email::on_attachments_select");
      form = $("#send_email_form");
      form_data = new FormData(form[0]);
      init = {
        body: form_data
      };
      return this.ajax_fetch("recalculate_size", init).then((function(_this) {
        return function(data) {
          return _this.update_size_info(data);
        };
      })(this));
    };

    return EmailController;

  })();

}).call(this);
