(function() {
  window.RemarksWidgetView = class RemarksWidgetView {
    constructor() {
      // BINDING CONTEXT
      this.load = this.load.bind(this);
      this.bind_eventhandler = this.bind_eventhandler.bind(this);
      this.get_remarks_widget = this.get_remarks_widget.bind(this);
      this.format = this.format.bind(this);
      this.update_remarks_history = this.update_remarks_history.bind(this);
      this.clear_remarks_textarea = this.clear_remarks_textarea.bind(this);
      this.get_remarks = this.get_remarks.bind(this);
      this.set_remarks = this.set_remarks.bind(this);
      this.fetch_remarks = this.fetch_remarks.bind(this);
      this.post_remarks = this.post_remarks.bind(this);
      this.on_remarks_change = this.on_remarks_change.bind(this);
      this.on_remarks_submit = this.on_remarks_submit.bind(this);
      this.on_remarks_toggle = this.on_remarks_toggle.bind(this);
      this.ajax_submit = this.ajax_submit.bind(this);
      this.get_portal_url = this.get_portal_url.bind(this);
    }

    load() {
      console.debug("RemarksWidgetView::load");
      this.bind_eventhandler();
    }

    bind_eventhandler() {
      console.debug("RemarksWidgetView::bind_eventhandler");

      // jQuery 3-compatible delegated event handling
      $(document).on("click", "input.saveRemarks", this.on_remarks_submit);
      $(document).on("click", "button.toggleRemarks", this.on_remarks_toggle);
      $(document).on("keyup", "textarea[name='Remarks']", this.on_remarks_change);

      // For dev access
      window.rem = this;
    }

    get_remarks_widget(uid) {
      let widgets;
      if (uid) {
        widgets = $(`.ArchetypesRemarksWidget[data-uid='${uid}']`);
        if (!widgets.length) {
          console.warn(`[RemarksWidgetView] No widget found with uid ${uid}`);
          return null;
        }
        return $(widgets[0]);
      }

      widgets = $(".ArchetypesRemarksWidget");
      if (!widgets.length) {
        console.warn("[RemarksWidgetView] No widget found");
        return null;
      }
      if (widgets.length > 1) {
        console.warn("[RemarksWidgetView] Multiple widgets found, please specify uid");
        return null;
      }
      return $(widgets[0]);
    }

    format(value) {
      return value.replace(/\n/g, "<br/>");
    }

    update_remarks_history(value, uid) {
      if (!value.length) return;

      const widget = this.get_remarks_widget(uid);
      if (!widget) return;

      const el = widget.find(".remarks_history");
      const val = value[0];

      const record_header = $("<div class='record-header'/>")
        .append(`<span class='record-user'>${val.user_id}</span>`)
        .append(`<span class='record-username'>${val.user_name}</span>`)
        .append(`<span class='record-date'>${val.created}</span>`);

      const record_content = $("<div class='record-content'/>").html(this.format(val.content));

      const record = $("<div class='record'/>").attr("id", val.id)
        .append(record_header)
        .append(record_content);

      el.prepend(record);
    }

    toggle_remarks(button) {
      /*
       * Toggle visibility of remarks beyond the first 3
       */
      const widget = $(button).closest(".remarks-widget");
      const hiddenRemarks = widget.find(".extra-remark");
      const showMoreText = $(button).find(".show-more-text");
      const showLessText = $(button).find(".show-less-text");

      const isCollapsed = showMoreText.is(":visible");

      hiddenRemarks.toggleClass("d-none", !isCollapsed);
      showMoreText.toggleClass("d-none", isCollapsed);
      showLessText.toggleClass("d-none", !isCollapsed);
    }


    clear_remarks_textarea(uid) {
      const widget = this.get_remarks_widget(uid);
      if (widget) widget.find("textarea").val("");
    }

    get_remarks(uid) {
      const widget = this.get_remarks_widget(uid);
      return widget ? widget.find(".remarks_history").html() : "";
    }

    set_remarks(value, uid) {
      return this.post_remarks(value, uid)
        .done((data) => {
          this.fetch_remarks(uid)
            .done((remarks) => {
              this.update_remarks_history(remarks, uid);
              this.clear_remarks_textarea(uid);
            })
            .fail(() => console.warn("Failed to fetch remarks"));
        })
        .fail(() => console.warn("Failed to set remarks"));
    }

    fetch_remarks(uid) {
      const deferred = $.Deferred();
      const widget = this.get_remarks_widget(uid);
      if (!widget) return deferred.reject();

      const fieldname = widget.attr("data-fieldname");

      this.ajax_submit({
        url: this.get_portal_url() + "/@@API/read",
        data: {
          catalog_name: "uid_catalog",
          UID: widget.attr("data-uid"),
          include_fields: [fieldname]
        }
      }).done((data) => {
        deferred.resolve(data.objects[0][fieldname]);
      }).fail(() => {
        deferred.reject();
      });

      return deferred.promise();
    }

    post_remarks(value, uid) {
      const deferred = $.Deferred();
      const widget = this.get_remarks_widget(uid);
      if (!widget) return deferred.reject();

      const fieldname = widget.attr("data-fieldname");
      const data = {
        obj_uid: widget.attr("data-uid")
      };
      data[fieldname] = value;

      this.ajax_submit({
        url: this.get_portal_url() + "/@@API/update",
        data: data
      }).done(() => {
        deferred.resolve([]);
      }).fail(() => {
        deferred.reject();
      });

      return deferred.promise();
    }

    on_remarks_change(event) {
      const el = event.target;
      if (!el.value) return;

      const widget = el.closest(".ArchetypesRemarksWidget");
      if (!widget) return;

      const btn = widget.querySelector("input.saveRemarks");
      if (btn) btn.disabled = false;
    }

    on_remarks_submit(event) {
      event.preventDefault();
      const $widget = $(event.currentTarget).closest(".ArchetypesRemarksWidget");
      const value = $widget.find("textarea").val();
      const uid = $widget.attr("data-uid");
      this.set_remarks(value, uid);
    }

    on_remarks_toggle(event) {
      event.preventDefault();
      const el = event.currentTarget;
      this.toggle_remarks(el);
    }

    ajax_submit(options = {}) {
      console.debug("°°° ajax_submit °°°");

      const defaults = {
        type: "POST",
        url: this.get_portal_url(),
        context: this,
        dataType: "json",
        data: {},
        timeout: 600000 // 10 min
      };
      const finalOpts = $.extend({}, defaults, options);

      $(this).trigger("ajax:submit:start");

      return $.ajax(finalOpts)
        .done(() => $(this).trigger("ajax:submit:end"))
        .fail((request, status) => {
          const msg = _t(`Sorry, an error occurred: ${status}`);
          window.bika?.lims?.portalMessage(msg);
          window.scrollTo(0, 0);
        });
    }

    get_portal_url() {
      return $("input[name='portal_url']").val() || window.portal_url;
    }
  };
})();
