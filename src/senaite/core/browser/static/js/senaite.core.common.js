/** Common global utility functions
 *
 * This controller is *always* loaded, i.e. for all templates.
 * It provides common utility functions in `senaite.core.globals`.
 *
 */
window.CommonUtils = class CommonUtils {
  constructor() {
    this.load = this.load.bind(this);
    this.portalMessage = this.portalMessage.bind(this);
    this.log = this.log.bind(this);
    this.warning = this.warning.bind(this);
    this.error = this.error.bind(this);
    this.jsonapi_read = this.jsonapi_read.bind(this);
  }

  /**
   * Entry-point method
   */
  load() {
    // Ensure namespace exists
    window.senaite = window.senaite || {};
    window.senaite.core = window.senaite.core || {};
    window.senaite.core.globals = window.senaite.core.globals || {};

    // Expose methods globally
    window.senaite.core.globals.portalMessage = this.portalMessage;
    window.senaite.core.globals.log = this.log;
    window.senaite.core.globals.warning = this.warning;
    window.senaite.core.globals.error = this.error;
    window.senaite.core.globals.jsonapi_read = this.jsonapi_read;
    window.senaite.core.globals.jsonapi_cache = {};
  }

  /**
   * Displays a Bootstrap 4-compatible dismissible alert
   * @param {string|string[]} message - Message(s) to display
   * @param {string} level - "info", "warning", or "error" (default: "error")
   */
  portalMessage(message, level = "error") {
    const levelClassMap = {
      info: "alert-info",
      warning: "alert-warning",
      error: "alert-danger"
    };

    const alertClass = levelClassMap[level] || levelClassMap.error;
    const titleMap = {
      info: _t("Information"),
      warning: _t("Warning"),
      error: _t("Error")
    };

    const title = titleMap[level] || titleMap.error;
    const messages = Array.isArray(message) ? message : [message];
    const listItems = messages.map(msg => `<li>${msg}</li>`).join("");

    const alertHtml = `
      <div class="alert ${alertClass} alert-dismissible fade show portalMessage" role="alert">
        <strong>${title}:</strong>
        <ul class="mb-0">${listItems}</ul>
        <button type="button" class="close" data-dismiss="alert" aria-label="${_t("Close")}">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>`;

    $(".portalMessage").remove();
    $("#viewlet-above-content").append(alertHtml);
  }

  /**
   * Logs a message to the backend
   */
  log(e) {
    const url = window.location?.href;
    if (!url) return;

    $.post("js_log", {
      message: `(${url}): ${e}`,
      _authenticator: $("input[name='_authenticator']").val()
    });
  }

  /**
   * Sends a warning to the backend
   */
  warning(e) {
    $.post("js_warn", {
      message: `(${window.location.href}): ${e}`,
      _authenticator: $("input[name='_authenticator']").val()
    });
  }

  /**
   * Sends an error to the backend
   */
  error(e) {
    $.post("js_err", {
      message: `(${window.location.href}): ${e}`,
      _authenticator: $("input[name='_authenticator']").val()
    });
  }

  /**
   * JSON API reader with caching
   */
  jsonapi_read(request_data, handler) {
    const cache = window.senaite.core.globals.jsonapi_cache;

    if (typeof request_data.page_size === "undefined") {
      request_data.page_size = 0;
    }

    const cacheKey = $.param(request_data);

    if (!cache[cacheKey]) {
      $.ajax({
        type: "POST",
        dataType: "json",
        url: `${window.portal_url}/@@API/read`,
        data: request_data,
        success: function (data) {
          cache[cacheKey] = data;
          handler(data);
        }
      });
    } else {
      handler(cache[cacheKey]);
    }
  }
}
