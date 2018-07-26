
/* Please use this command to compile this file into the proper folder:
    coffee --no-header -w -o ../../../../skins/bika/bika_widgets -c remarkswidget.coffee
 */

(function() {
  var bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  window.RemarksWidgetView = (function() {
    function RemarksWidgetView() {
      this.get_portal_url = bind(this.get_portal_url, this);
      this.ajax_submit = bind(this.ajax_submit, this);
      this.on_remarks_submit = bind(this.on_remarks_submit, this);
      this.post_remarks = bind(this.post_remarks, this);
      this.fetch_remarks = bind(this.fetch_remarks, this);
      this.set_remarks = bind(this.set_remarks, this);
      this.get_remarks = bind(this.get_remarks, this);
      this.clear_remarks_textarea = bind(this.clear_remarks_textarea, this);
      this.update_remarks_history = bind(this.update_remarks_history, this);
      this.format = bind(this.format, this);
      this.get_remarks_widget = bind(this.get_remarks_widget, this);
      this.bind_eventhandler = bind(this.bind_eventhandler, this);
      this.load = bind(this.load, this);
    }

    RemarksWidgetView.prototype.load = function() {
      console.debug("RemarksWidgetView::load");
      return this.bind_eventhandler();
    };


    /* INITIALIZERS */

    RemarksWidgetView.prototype.bind_eventhandler = function() {

      /*
       * Binds callbacks on elements
       *
       * N.B. We attach all the events to the form and refine the selector to
       * delegate the event: https://learn.jquery.com/events/event-delegation/
       */
      console.debug("RemarksWidgetView::bind_eventhandler");
      $("body").on("click", "input.saveRemarks", this.on_remarks_submit);
      return window.rem = this;
    };


    /* METHODS */

    RemarksWidgetView.prototype.get_remarks_widget = function(uid) {

      /*
       * Shortcut to retrieve remarks widget from current page.
       * if uid is not specified, attempts to find widget.
       */
      var msg, widgets;
      if (uid != null) {
        widgets = $(".ArchetypesRemarksWidget[data-uid='" + uid + "']");
        if (widgets.length === 0) {
          console.warn("[RemarksWidgetView] No widget found with uid " + uid);
          return null;
        }
        return $(widgets[0]);
      } else {
        widgets = $(".ArchetypesRemarksWidget");
        if (widgets.length === 0) {
          console.warn("[RemarksWidgetView] No widget found");
          return null;
        }
        if (widgets.length > 1) {
          msg = "[RemarksWidgetView] Multiple widgets found, please specify uid";
          console.warn(msg);
          return null;
        }
      }
      return $(widgets[0]);
    };

    RemarksWidgetView.prototype.format = function(value) {

      /*
       * Output HTML string.
       */
      var remarks;
      remarks = value.replace(new RegExp("\n", "g"), "<br/>");
      return remarks;
    };

    RemarksWidgetView.prototype.update_remarks_history = function(value, uid) {

      /*
       * Clear and update the widget's History with the provided value.
       */
      var el, widget;
      widget = this.get_remarks_widget(uid);
      if (widget === null) {
        return;
      }
      el = widget.find('.remarks_history');
      return el.html(this.format(value));
    };

    RemarksWidgetView.prototype.clear_remarks_textarea = function(uid) {

      /*
       * Clear textarea contents
       */
      var el, widget;
      widget = this.get_remarks_widget(uid);
      if (widget === null) {
        return;
      }
      el = widget.find('textarea');
      return el.val("");
    };

    RemarksWidgetView.prototype.get_remarks = function(uid) {

      /*
       * Return the value currently displayed for the widget's remarks
       (HTML value)
       *
       */
      var widget;
      widget = this.get_remarks_widget(uid);
      if (widget === null) {
        return;
      }
      return widget.find('.remarks_history').html();
    };

    RemarksWidgetView.prototype.set_remarks = function(value, uid) {

      /*
       * Single function to post remarks, update widget, and clear textarea.
       *
       */
      return this.post_remarks(value, uid).done(function(data) {
        return this.fetch_remarks(uid).done(function(remarks) {
          this.update_remarks_history(remarks, uid);
          return this.clear_remarks_textarea(uid);
        }).fail(function() {
          return console.warn("Failed to get remarks");
        });
      }).fail(function() {
        return console.warn("Failed to set remarks");
      });
    };


    /* ASYNC DATA METHODS */

    RemarksWidgetView.prototype.fetch_remarks = function(uid) {

      /*
       * Get current value of field from /@@API/read
       */
      var deferred, fieldname, widget;
      deferred = $.Deferred();
      widget = this.get_remarks_widget(uid);
      if (widget === null) {
        return deferred.reject();
      }
      fieldname = widget.attr("data-fieldname");
      this.ajax_submit({
        url: this.get_portal_url() + "/@@API/read",
        data: {
          catalog_name: "uid_catalog",
          UID: widget.attr('data-uid'),
          include_fields: [fieldname]
        }
      }).done(function(data) {
        return deferred.resolveWith(this, [data.objects[0][fieldname]]);
      });
      return deferred.promise();
    };

    RemarksWidgetView.prototype.post_remarks = function(value, uid) {

      /*
       * Submit the value to the field setter via /@@API/update.
       *
       */
      var deferred, fieldname, options, widget;
      deferred = $.Deferred();
      widget = this.get_remarks_widget(uid);
      if (widget === null) {
        return deferred.reject();
      }
      fieldname = widget.attr("data-fieldname");
      options = {
        url: this.get_portal_url() + "/@@API/update",
        data: {
          obj_uid: widget.attr('data-uid')
        }
      };
      options.data[fieldname] = value;
      this.ajax_submit(options).done(function(data) {
        return deferred.resolveWith(this, [[]]);
      });
      return deferred.promise();
    };


    /* EVENT HANDLERS */

    RemarksWidgetView.prototype.on_remarks_submit = function(event) {

      /*
       * Eventhandler for RemarksWidget"s "Save Remarks" button
       *
       */
      var widget;
      console.debug("°°° RemarksWidgetView::on_remarks_submit °°°");
      event.preventDefault();
      widget = $(event.currentTarget).parents(".ArchetypesRemarksWidget");
      return this.set_remarks(widget.children("textarea").val(), widget.attr('data-uid'));
    };


    /* HELPERS */

    RemarksWidgetView.prototype.ajax_submit = function(options) {

      /**
       * Ajax Submit with automatic event triggering and some sane defaults
       *
       * @param {object} options
       *    jQuery ajax options
       * @returns {Deferred} XHR request
       */
      var done;
      console.debug("°°° ajax_submit °°°");
      if (options == null) {
        options = {};
      }
      if (options.type == null) {
        options.type = "POST";
      }
      if (options.url == null) {
        options.url = this.get_portal_url();
      }
      if (options.context == null) {
        options.context = this;
      }
      if (options.dataType == null) {
        options.dataType = "json";
      }
      if (options.data == null) {
        options.data = {};
      }
      console.debug(">>> ajax_submit::options=", options);
      $(this).trigger("ajax:submit:start");
      done = function() {
        return $(this).trigger("ajax:submit:end");
      };
      return $.ajax(options).done(done);
    };

    RemarksWidgetView.prototype.get_portal_url = function() {

      /*
       * Return the portal url (calculated in code)
       */
      var url;
      url = $("input[name=portal_url]").val();
      return url || window.portal_url;
    };

    return RemarksWidgetView;

  })();

}).call(this);
