
/** Helper JS to change classnames and HTML on the fly
 *
 * Please use this command to compile this file into the parent `js` directory:
 *
 * coffee --no-header -w -o ../js -c bootstrap-integration.coffee
 */

(function() {
  var Bootstrap;

  Bootstrap = (function() {

    /*
     * Bootstrap Fixtures for SENAITE
     */
    function Bootstrap() {
      $("h1").next("p").addClass("text-info");
      $("div.documentDescription").addClass("text-info");
      $("table").not(".ordered-selection-field").not(".recordswidget").addClass("table table-condensed table-bordered table-striped");
      $(".hiddenStructure").addClass("hidden");
      $(".alert-error").removeClass("alert-error").addClass("alert-danger");
      $(".managePortletsLink a").addClass("btn btn-default btn-xs");
      $(".portletWrapper dl").addClass("panel panel-default");
      $("#content-core ul.configlets").addClass("nav nav-stacked well");
      $(".portletItem ul.configlets").addClass("nav");
      $("a#setup-link").addClass("btn btn-link");
      $("a.link-parent").addClass("btn btn-link");
      $("button").not(".navbar-toggle").addClass("btn btn-default");
      $("input[type='submit']").addClass("btn btn-default");
      return this;
    }

    Bootstrap.prototype.fix_form = function(el) {
      var $el, foundPrimary;
      console.debug("Bootstrap::fix_form");
      $el = $(el);
      if (!$el.is("form")) {
        console.error("Element is not a form");
        return;
      }
      $el.addClass("form");
      $el.find("input").not(".bika-listing-table :checkbox").addClass("input-sm");
      $el.find("select").addClass("input-sm");
      $("textarea").addClass("form-control");
      $el.find("div.formQuestion").removeClass("label");
      $el.find("div.plone_jscalendar").addClass("form-inline");
      $el.find("span.label").removeClass("label");
      $el.find(".formHelp").addClass("help-block small").removeClass("formHelp");
      $el.find("div.field").addClass("form-group");
      $el.find(".fieldTextFormat").addClass("form-inline").addClass("pull-right");
      $el.find("input[type='submit'], input[type='button']").addClass("btn btn-default");
      $el.find("button").addClass("btn btn-default");
      $el.find(".datagridwidget-add-button").addClass("btn btn-default");
      foundPrimary = false;
      return $("div.formControls input[type='submit']").each(function() {
        var button, input;
        input = $(this);
        button = $('<button type="submit" class="btn btn-sm btn-default" name="' + input.attr('name') + '"value="' + input.attr('value') + '">' + input.attr('value') + '</button>');
        if (input.hasClass("context") && !foundPrimary) {
          button.addClass("btn-primary");
          foundPrimary = true;
        }
        return input.replaceWith(button);
      });
    };

    Bootstrap.prototype.fix_portal_message = function(el, remove_others) {
      var $el, cls, facility, mapping, message, replacement, title;
      if (remove_others == null) {
        remove_others = true;
      }
      console.debug("Bootstrap::fix_portal_message");
      $el = $(el);
      if (!$el.hasClass("portalMessage")) {
        console.error("Element is not a portal message");
        return;
      }
      mapping = {
        "error": "danger",
        "warn": "warning"
      };
      if (remove_others) {
        $("#viewlet-above-content div[data-alert='alert']").remove();
      }
      $el.removeClass("portalMessage");
      cls = $el[0].className;
      title = $el.find("dt").html();
      message = $el.find("dd").html();
      facility = cls in mapping ? mapping[cls] : cls;
      replacement = $("<div data-alert=\"alert\" class=\"alert alert-dismissible alert-" + facility + "\">\n  <button type=\"button\" class=\"close\" data-dismiss=\"alert\" aria-label=\"Close\">\n    <span aria-hidden=\"true\">×</span>\n  </button>\n  <strong>" + title + "</strong>\n  <p>" + message + "</p>\n</div>");
      replacement.attr("style", $el.attr("style"));
      return $el.replaceWith(replacement);
    };

    Bootstrap.prototype.fix_header_table = function(el) {
      var $el;
      console.debug("Bootstrap::fix_header_table");
      $el = $(el);
      if (!$el.hasClass("header_table")) {
        console.error("Element is not a header table");
        return;
      }
      $el.addClass("table-sm").removeClass("table-striped");
      $el.find("td:first-child()").addClass("active");
      $el.find("td.key").addClass("active");
      $el.find("td").addClass("small");
      return $el.find("div.field").removeClass("form-group");
    };

    Bootstrap.prototype.fix_results_interpretation = function(el) {
      var $el;
      console.debug("Bootstrap::fix_results_interpretation");
      $el = $(el);
      if (!$el.hasClass("arresultsinterpretation-container")) {
        console.error("Element is not a results interpretation container");
        return;
      }
      return this.activate_form_tabbing($el);
    };

    Bootstrap.prototype.fix_manage_viewlets = function(el) {
      var $el, hiddenviewlet;
      console.debug("Bootstrap::fix_manage_viewlets");
      $el = $(el);
      if (!$el.hasClass("template-manage-viewlets")) {
        console.error("Element is not the manage viewlets view");
        return;
      }
      $el.find(".hide").removeClass("hide");
      $el.find(".show").removeClass("show");
      hiddenviewlet = $("<span>This viewlet is hidden and will not be shown</span>");
      $(hiddenviewlet).addClass("text-danger");
      return $el.find(".hiddenViewlet").prepend(hiddenviewlet);
    };

    Bootstrap.prototype.fix_form_tabs = function(el) {
      var $el;
      console.debug("Bootstrap::fix_form_tabs");
      $el = $(el);
      if (!$el.is("ul")) {
        console.error("Element is not a list element");
        return;
      }
      if ($el.hasClass("dropdown-menu")) {
        return;
      }
      $el.addClass("nav nav-tabs");
      return this.activate_form_tabbing($el);
    };

    Bootstrap.prototype.activate_form_tabbing = function(el) {
      var $el;
      console.debug("Bootstrap::activate_form_tabbing");
      $el = $(el);
      $el.find(".selected").parent("li").addClass("active");
      if ($el.find(".active").length === 0) {
        $el.find("li").first().addClass("active");
      }
      return $el.find("li").on("click", function() {
        $(this).parent().find("li.active").removeClass("active");
        return $(this).addClass("active");
      });
    };

    return Bootstrap;

  })();

  $(document).ready(function() {
    var bs, observer;
    console.log('** SENAITE BOOTSTRAP INTEGRATION **');
    bs = new Bootstrap();
    if (window.senaite == null) {
      window.senaite = {};
    }
    window.senaite.bootstrap = bs;
    observer = new MutationObserver(function(mutations) {
      return $.each(mutations, function(index, record) {
        return $.each(record.addedNodes, function(index, el) {
          return $(document).trigger("onCreate", el);
        });
      });
    });
    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
    $(document).on("onCreate", function(event, el) {
      var $el;
      $el = $(el);
      if ($el.hasClass("portalMessage")) {
        return bs.fix_portal_message($el);
      }
    });
    $("form").each(function() {
      return bs.fix_form(this);
    });
    $("table.header_table").each(function() {
      return bs.fix_header_table(this);
    });
    $("dl.portalMessage").each(function() {
      return bs.fix_portal_message(this);
    });
    $("div.arresultsinterpretation-container").each(function() {
      return bs.fix_results_interpretation(this);
    });
    $("ul.formTabs").each(function() {
      return bs.fix_form_tabs(this);
    });
    $("div#editing-bar ul").each(function() {
      return bs.fix_form_tabs(this);
    });
    $("div#edit-bar ul").each(function() {
      return bs.fix_form_tabs(this);
    });
    return $(".template-manage-viewlets").each(function() {
      return bs.fix_manage_viewlets(this);
    });
  });

}).call(this);
