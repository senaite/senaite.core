/**
 * Global utility class
 */
function CommonUtils() {
    const that = this;

    /**
     * Entry-point method
     */
    that.load = function () {
        // Ensure namespace exists
        window.senaite = window.senaite || {};
        window.senaite.core = window.senaite.core || {};
        window.senaite.core.globals = window.senaite.core.globals || {};

        /**
         * Displays a Bootstrap 4-compatible dismissible alert
         * @param {string|string[]} message - The message or messages to display
         * @param {string} level - One of: "info", "warning", "error" (default: "error")
         */
        that.portalMessage = window.senaite.core.globals.portalMessage = function (message, level = "error") {
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

            // Normalize message to array
            const messages = Array.isArray(message) ? message : [message];

            const listItems = messages.map(msg => `<li>${msg}</li>`).join("");

            const alertHtml = `
                <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
                    <strong>${title}:</strong>
                    <ul class="mb-0">${listItems}</ul>
                    <button type="button" class="close" data-dismiss="alert" aria-label="${_t("Close")}">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>`;

            $(".portalMessage").remove(); // clean up any previous custom messages
            $("#viewlet-above-content").append(alertHtml);
        };

        /**
         * Logs a message to the backend (if window.location is available)
         */
        that.log = window.senaite.core.globals.log = function (e) {
            const url = window.location?.href;
            if (!url) return;

            $.post("js_log", {
                message: `(${url}): ${e}`,
                _authenticator: $("input[name='_authenticator']").val()
            });
        };

        /**
         * Sends a warning to the backend
         */
        that.warning = window.senaite.core.globals.warning = function (e) {
            $.post("js_warn", {
                message: `(${window.location.href}): ${e}`,
                _authenticator: $("input[name='_authenticator']").val()
            });
        };

        /**
         * Sends an error to the backend
         */
        that.error = window.senaite.core.globals.error = function (e) {
            $.post("js_err", {
                message: `(${window.location.href}): ${e}`,
                _authenticator: $("input[name='_authenticator']").val()
            });
        };

        /**
         * JSON API reader with caching
         */
        window.senaite.core.globals.jsonapi_cache = {};

        that.jsonapi_read = window.senaite.core.globals.jsonapi_read = function (request_data, handler) {
            const cache = window.senaite.core.globals.jsonapi_cache;

            // Ensure page_size is explicitly set
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
        };
    };
}
