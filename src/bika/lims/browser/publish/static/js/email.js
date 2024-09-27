(function() {
  /* Please use this command to compile this file into the parent `js` directory:
      coffee --no-header -w -o ../js -c email.coffee
  */
  var EmailController;

  // DOCUMENT READY ENTRY POINT
  document.addEventListener("DOMContentLoaded", function() {
    var controller;
    console.debug("*** Loading Email Controller");
    controller = new EmailController();
    return controller.initialize();
  });

  EmailController = class EmailController {
    constructor() {
      this.bind_eventhandler = this.bind_eventhandler.bind(this);
      this.toggle_attachments_container = this.toggle_attachments_container.bind(this);
      this.on_add_attachments_click = this.on_add_attachments_click.bind(this);
      this.on_attachments_select = this.on_attachments_select.bind(this);
      this.on_change_select_all_attachments = this.on_change_select_all_attachments.bind(this);
      this.bind_eventhandler();
      return this;
    }

    initialize() {
      console.debug("senaite.core:Email::initialize");
      // Initialize overlays
      return this.init_overlays();
    }

    init_overlays() {
      /*
       * Initialize all overlays for later loading
       *
       */
      console.debug("senaite.core:Email::init_overlays");
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
    }

    bind_eventhandler() {
      /*
       * Binds callbacks on elements
       *
       * N.B. We attach all the events to the body and refine the selector to
       * delegate the event: https://learn.jquery.com/events/event-delegation/
       *
       */
      console.debug("senaite.core::bind_eventhandler");
      // Toggle additional attachments visibility
      $("body").on("click", "#add-attachments", this.on_add_attachments_click);
      // Select/deselect additional attachments
      $("body").on("change", ".attachment input[type='checkbox']", this.on_attachments_select);
      // Select/deselect all additional attachments
      return $("body").on("change", "#select-all-attachments", this.on_change_select_all_attachments);
    }

    get_base_url() {
      /*
       * Calculate the current base url
       */
      return document.URL.split("?")[0];
    }

    get_api_url(endpoint) {
      /*
       * Build API URL for the given endpoint
       * @param {string} endpoint
       * @returns {string}
       */
      var base_url;
      base_url = this.get_base_url();
      return `${base_url}/${endpoint}`;
    }

    ajax_fetch(endpoint, init) {
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
      console.info(`Email::fetch:endpoint=${endpoint} init=`, init);
      request = new Request(url, init);
      return fetch(request).then(function(response) {
        return response.json();
      });
    }

    is_visible(element) {
      /*
       * Checks if the element is visible
       */
      if ($(element).css("display") === "none") {
        return false;
      }
      return true;
    }

    toggle_attachments_container(toggle = null) {
      /*
       * Toggle the visibility of the attachments container
       */
      var button, container, visible;
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
    }

    update_size_info(data) {
      var unit;
      /*
       * Update the total size of the selected attachments
       */
      if (!data) {
        console.warn("No valid size information: ", data);
        return null;
      }
      unit = "kB";
      $("#attachment-files").text(`${data.files}`);
      if (data.limit_exceeded) {
        $("#email-size").addClass("text-danger");
        $("#email-size").text(`${data.size} ${unit} > ${data.limit} ${unit}`);
        return $("input[name='send']").prop("disabled", true);
      } else {
        $("#email-size").removeClass("text-danger");
        $("#email-size").text(`${data.size} ${unit}`);
        return $("input[name='send']").prop("disabled", false);
      }
    }

    on_add_attachments_click(event) {
      console.debug("°°° Email::on_add_attachments_click");
      event.preventDefault();
      return this.toggle_attachments_container();
    }

    on_attachments_select(event) {
      var count_attachments, form, form_data, init, select_all_checked, select_attachments;
      console.debug("°°° Email::on_attachments_select");
      // extract the form data
      form = $("#send_email_form");
      // form.serialize does not include file attachments
      // form_data = form.serialize()
      form_data = new FormData(form[0]);
      count_attachments = $("input[name='attachment_uids:list']").length;
      select_attachments = form_data.getAll("attachment_uids:list").length;
      select_all_checked = count_attachments === select_attachments;
      $("#select-all-attachments").prop("checked", select_all_checked);
      init = {
        body: form_data
      };
      return this.ajax_fetch("recalculate_size", init).then((data) => {
        return this.update_size_info(data);
      });
    }

    on_change_select_all_attachments(event) {
      var checked;
      console.debug("°°° Email::on_change_select_all_attachments");
      checked = event.target.checked;
      $("input[name='attachment_uids:list']").each(function(index, element) {
        return $(element).prop("checked", checked);
      });
      return this.on_attachments_select();
    }

  };

}).call(this);
