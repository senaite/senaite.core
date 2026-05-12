/* SENAITE Remarks Widget Handler
 */

// IE NodeList.forEach polyfill.
// See: https://developer.mozilla.org/en-US/docs/Web/API/NodeList/forEach#polyfill
if (window.NodeList && !NodeList.prototype.forEach) {
  NodeList.prototype.forEach = Array.prototype.forEach;
}

window.widgets = window.widgets || {};

document.addEventListener("DOMContentLoaded", () => {

    class RemarksWidget {

        constructor() {
            this.remarksWidgets = document.querySelectorAll(".remarks-widget");
            for(const remarkWidget of this.remarksWidgets) {
                this.init_toggle_button(remarkWidget);
                this.init_add_widget(remarkWidget);
            }

            return this;
        }

        init_toggle_button(remarkWidget) {
            $(remarkWidget).on("click", "button.toggleRemarks", (event) => {
                event.preventDefault();
                const button = event.currentTarget;

                const widget = $(button).closest(".remarks-widget");
                const hiddenRemarks = widget.find(".extra-remark");
                const showMoreText = $(button).find(".show-more-text");
                const showLessText = $(button).find(".show-less-text");

                const isCollapsed = showMoreText.is(":visible");

                hiddenRemarks.toggleClass("d-none", !isCollapsed);
                showMoreText.toggleClass("d-none", isCollapsed);
                showLessText.toggleClass("d-none", !isCollapsed);
            });
        }

        init_add_widget(remarkWidget) {
            $(remarkWidget).on("keyup", "textarea", (event) => {
                const widget = $(event.target).closest(".remarks-widget");
                const saveBtn = $(widget).find("#save-remarks");
                if(saveBtn) {
                    saveBtn.prop("disabled", !event.target.value);
                }
            });
            $(remarkWidget).on("click", "input#save-remarks", (event) => {
                event.preventDefault();
                const widget = $(event.target).closest(".remarks-widget");
                const uid = widget.attr("data-uid");
                const fieldName = widget.attr("data-fieldname");
                const textarea = widget.find("textarea")[0];
                const value = textarea.value;
                this.post_remarks(uid, fieldName, value).done((data) => {
                    textarea.value = "";
                    $(textarea).keyup();
                    this.fetch_remarks(uid, fieldName).done((data) => {
                        if(data.success && data.remarks.length) {
                            this.update_remarks_history(uid, data.remarks);
                        }
                    });
                });
            });
        }

        format(value) {
            return value.replace(/\n/g, "<br/>");
        }

        update_remarks_history(uid, remarks) {
            const widget = this.get_remarks_widget(uid);
            if (!widget) return;

            const el = widget.find(".remarks-history");
            const val = remarks[0];

            const record_header = $("<div class='record-header'/>")
                .append(`<span class='record-user'>${val.user_id}</span>`)
                .append(`<span class='record-username'>${val.user_name}</span>`)
                .append(`<span class='record-date'>${val.created}</span>`);

            const record_content = $("<div class='record-content'/>")
                .html(this.format(val.content));

            const record = $("<div class='record'/>").attr("id", val.id)
                .append(record_header)
                .append(record_content);

            el.prepend(record);
        }

        fetch_remarks(uid, fieldName) {
            const data = {
                uid,
                fieldName,
            };
            return this.ajax_submit({
                url: this.get_portal_url() + "/fetch_remarks",
                data,
            });
        }

        post_remarks(uid, fieldName, value) {
            const data = {
                uid,
                fieldName,
                value,
            };
            return this.ajax_submit({
                url: this.get_portal_url() + "/add_remark",
                data,
            });
        }

        ajax_submit(options = {}) {
            const defaults = {
                type: "POST",
                url: this.get_portal_url(),
                context: this,
                cache: false,
                dataType: "json",
                data: {},
                timeout: 600000 // 10 min
            };
            const finalOpts = $.extend({}, defaults, options);

            $(this).trigger("ajax:submit:start");
            return $.ajax(finalOpts)
                .always(() => $(this).trigger("ajax:submit:end"))
                .fail((request, status) => {
                    const msg = _t(`Sorry, an error occurred: ${status}`);
                    window.senaite.core.globals.portalMessage(msg);
                    window.scrollTo(0, 0);
                });
        }

        get_remarks_widget(uid) {
            let widgets;
            if (uid) {
                widgets = $(`.remarks-widget[data-uid='${uid}']`);
                if (!widgets.length) {
                    console.warn(`[RemarksWidget] No widget found with uid ${uid}`);
                    return null;
                }
                return $(widgets[0]);
            }

            widgets = $(".remarks-widget");
            if (!widgets.length) {
                console.warn("[RemarksWidget] No widget found");
                return null;
            }
            if (widgets.length > 1) {
                console.warn("[RemarksWidget] Multiple widgets found, please specify uid");
                return null;
            }
            return $(widgets[0]);
        }

        get_portal_url() {
            return $("input[name='portal_url']").val() || window.portal_url;
        }

    }

    // Initialize RemarksWidget's
    if (window.widgets.remarkwidget === undefined) {
        window.widgets.remarkwidget = new RemarksWidget();
    }
});
