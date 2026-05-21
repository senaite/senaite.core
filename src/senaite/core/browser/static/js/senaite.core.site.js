/**
 * Site View Controller
 *
 * This controller is *always* loaded, i.e. for all templates.
 */
window.SiteView = class SiteView {
  constructor() {
    this.load = this.load.bind(this);
    this.bind_eventhandler = this.bind_eventhandler.bind(this);
    this.get_portal_url = this.get_portal_url.bind(this);
    this.get_authenticator = this.get_authenticator.bind(this);
    this.log = this.log.bind(this);
    this.readCookie = this.readCookie.bind(this);
    this.read_cookie = this.read_cookie.bind(this);
    this.setCookie = this.setCookie.bind(this);
    this.set_cookie = this.set_cookie.bind(this);
    this.notify_in_panel = this.notify_in_panel.bind(this);
    this.on_at_integer_field_keyup = this.on_at_integer_field_keyup.bind(this);
    this.on_at_float_field_keyup = this.on_at_float_field_keyup.bind(this);
    this.on_numeric_field_input = this.on_numeric_field_input.bind(this);
    this.on_numeric_field_keypress = this.on_numeric_field_keypress.bind(this);
    this.on_overlay_panel_click = this.on_overlay_panel_click.bind(this);
    this.on_modal_link_click = this.on_modal_link_click.bind(this);
    this.on_iframe_edit_link_click = this.on_iframe_edit_link_click.bind(this);
    this.open_iframe_edit_modal = this.open_iframe_edit_modal.bind(this);
  }

  load() {
    console.debug("SiteView::load");
    this.bind_eventhandler();
    this.allowed_keys = [8, 9, 13, 35, 36, 37, 39, 46, 44, 60, 62, 45, 69, 101, 61];
  }

  bind_eventhandler() {
    console.debug("SiteView::bind_eventhandler");

    $(document).on("keypress", ".numeric", this.on_numeric_field_keypress);
    $(document).on("input", ".numeric", this.on_numeric_field_input);

    // Integer and float fields using attribute checks instead of problematic selectors
    $(document).on("keyup", "input", (e) => {
      const name = e.target.name || "";
      if (name.includes(":int")) this.on_at_integer_field_keyup(e);
      if (name.includes(":float")) this.on_at_float_field_keyup(e);
    });

    $(document).on("click", "a.overlay_panel", this.on_overlay_panel_click);
    $(document).on("click", "a.modal_link", this.on_modal_link_click);
    $(document).on(
      "click", "a.iframe-edit-link", this.on_iframe_edit_link_click);

    $(document).on({
      ajaxStart: () => $("body").addClass("loading"),
      ajaxStop: () => $("body").removeClass("loading"),
      ajaxError: () => $("body").removeClass("loading")
    });
  }

  get_portal_url() {
    return window.portal_url;
  }

  get_authenticator() {
    console.warn("SiteView::get_authenticator is deprecated. Use site.authenticator()");
    return window.site.authenticator();
  }

  log(message) {
    console.debug(`SiteView::log: ${message}`);
    return senaite.core.globals.log(message);
  }

  readCookie(cname) {
    console.warn("Use read_cookie instead");
    return this.read_cookie(cname);
  }

  read_cookie(cname) {
    const nameEQ = `${cname}=`;
    const ca = document.cookie.split(';');
    for (let c of ca) {
      c = c.trim();
      if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length);
    }
    return null;
  }

  setCookie(cname, cvalue) {
    console.warn("Use set_cookie instead");
    return this.set_cookie(cname, cvalue);
  }

  set_cookie(cname, cvalue) {
    document.cookie = `${cname}=${cvalue}; path=/`;
  }

  notify_in_panel(data, mode) {
    console.debug(`notify_in_panel: ${mode} = ${data}`);
    $('#panel-notification').remove();
    const html = `
      <div id="panel-notification" style="display:none">
        <div class="${mode}-notification-item">${data}</div>
      </div>`;
    $('div#viewlet-above-content-title').append(html);
    $('#panel-notification').fadeIn('slow', () => {
      setTimeout(() => {
        $('#panel-notification').fadeOut('slow');
      }, 3000);
    });
  }

  on_at_integer_field_keyup(e) {
    const $el = $(e.currentTarget);
    const cleanVal = $el.val().replace(/\D/g, '');
    if ($el.val() !== cleanVal) {
      $el.val(cleanVal);
    }
  }

  on_at_float_field_keyup(e) {
    const $el = $(e.currentTarget);
    const cleanVal = $el.val().replace(/[^-.\d]/g, '');
    if ($el.val() !== cleanVal) {
      $el.val(cleanVal);
    }
  }

  on_numeric_field_keypress(e) {
    const key = e.which || e.keyCode;
    const char = String.fromCharCode(key);
    const $el = $(e.currentTarget);
    const value = $el.val();

    const isDigit = key >= 48 && key <= 57;
    const isComma = char === ',';
    const isDot = char === '.';
    const isMinus = char === '-';
    const isAllowed = this.allowed_keys.includes(key);

    // Allow digits and control keys
    if (isDigit || isAllowed) return;

    // Allow one comma or one dot (handled later)
    if ((isComma || isDot) && !value.includes('.')) return;

    // Allow one minus at the beginning of the line
    if (isMinus && $el[0].selectionStart === 0 && !value.includes('-')) return;

    // Block everything else
    e.preventDefault();
  }

  on_numeric_field_input(e) {
    const $el = $(e.currentTarget);
    let val = $el.val();

    // Replace comma with dot
    val = val.replace(/,/g, '.');

    // Strip characters not valid in numeric expressions
    // Allow: digits, dot, minus, plus, e/E (exponential),
    //        < and > (detection limit operators), spaces
    val = val.replace(/[^0-9.eE<>\-+\s]/g, '');

    $el.val(val);
  }

  on_modal_link_click(e) {
    e.preventDefault();
    var $el = $(e.currentTarget);
    var url = $el.attr("href");
    var form_id = $el.data("form_id");
    var listings = window.senaite &&
                   window.senaite.core &&
                   window.senaite.core.listings;
    // load the modal via the listing
    var listing = listings && listings[form_id];
    if (listing) {
      var parsed = new URL(url, window.location);
      var uid = parsed.searchParams.get("uid");
      listing.loadModal(url, [uid]);
    }
  }

  on_iframe_edit_link_click(e) {
    e.preventDefault();
    const $el = $(e.currentTarget);
    const url = $el.attr("href");
    const title = $el.data("title") || $el.text().trim() || "";
    // edit_view="" means the modal shows the object's own view (no /edit);
    // in that case the modal never auto-closes on navigation.
    const edit_view = $el.data("edit-view") !== undefined
      ? String($el.data("edit-view"))
      : "edit";
    // Collect hazard pictograms from the same row so they show up next
    // to the title in the modal header. Sibling cell of the pencil
    // contains the .hazard-pictogram-mini images.
    const $pictos = $el.closest("td, th").find(".hazard-pictogram-mini");
    const pictos_html = $pictos.map(function () {
      return this.outerHTML;
    }).get().join("");
    this.open_iframe_edit_modal(url, title, edit_view, pictos_html);
  }

  isolate_content_area(doc) {
    if (!doc || !doc.body) return;

    // AT edit forms use #content; Dexterity forms have #content-core
    const content = doc.getElementById("content-core")
                 || doc.getElementById("content");
    if (!content) return;

    // Walk up to body, collecting every ancestor of the content node
    const ancestors = new Set();
    let node = content;
    while (node && node !== doc.body) {
      ancestors.add(node);
      node = node.parentElement;
    }

    // Recursively hide every element not on the ancestor path.
    // Stop at the content node itself — its children must remain visible.
    // Inline display:none preserves DOM structure so MutationObservers
    // in editform.js / search.js keep working.
    function hide_non_ancestors(parent) {
      if (parent === content) return;
      Array.from(parent.children).forEach(function(child) {
        if (!ancestors.has(child)) {
          child.style.setProperty("display", "none", "important");
        } else {
          hide_non_ancestors(child);
        }
      });
    }
    hide_non_ancestors(doc.body);

    doc.body.style.padding = "0";
    doc.body.style.margin = "0";
    // Allow the iframe body to scroll so that absolutely-positioned
    // dropdowns extending below the viewport become reachable.
    // The extra padding-bottom ensures there is always scrollable space
    // below the last form field even when the form fills the viewport.
    doc.body.style.overflowY = "auto";
    content.style.paddingBottom = "30vh";

    // Suppress pencil icons inside the iframe to prevent nested modals.
    const style = doc.createElement("style");
    style.textContent = ".iframe-edit-icon { display: none !important; }";
    (doc.head || doc.body).appendChild(style);
  }

  inject_change_detector(iwin) {
    // Detect form saves: any form submit where the triggering button is
    // not a cancel action sends a postMessage to the parent.
    try {
      const idoc = iwin.document;
      idoc.querySelectorAll("form").forEach(function(form) {
        form.addEventListener("submit", function() {
          const active = idoc.activeElement;
          const label = active
            ? (active.name || active.value || "").toLowerCase()
            : "";
          if (label.indexOf("cancel") >= 0) return;
          window.parent.postMessage("senaite_changes_made", "*");
        });
      });
      // Detect AJAX writes (non-GET requests = data mutation)
      const orig_open = iwin.XMLHttpRequest.prototype.open;
      iwin.XMLHttpRequest.prototype.open = function(method) {
        if (method && method.toUpperCase() !== "GET") {
          window.parent.postMessage("senaite_changes_made", "*");
        }
        return orig_open.apply(this, arguments);
      };
    } catch (ex) {
      // Ignore cross-origin or access errors
    }
  }

  open_iframe_edit_modal(url, title, edit_view, pictos_html) {
    // edit_view controls the load behaviour:
    //   "edit" (default) — auto-close when the URL no longer looks like
    //                      an edit form (save/cancel detected).
    //   ""               — always hide chrome, never auto-close; the user
    //                      closes the modal manually (e.g. sample view).
    if (edit_view === undefined) edit_view = "edit";
    const MODAL_ID = "senaite-iframe-edit-modal";
    let $modal = $(`#${MODAL_ID}`);

    if (!$modal.length) {
      $modal = $(`
        <div id="${MODAL_ID}" class="modal fade" tabindex="-1" role="dialog">
          <style>
            #${MODAL_ID} .modal-dialog {
              max-width: 90vw;
              margin: 1rem auto;
              /* Bootstrap sets pointer-events:none on .modal-dialog;
                 override so jQuery UI resize handles receive events. */
              pointer-events: auto;
            }
            #${MODAL_ID} .modal-header {
              cursor: move;
            }
            @media (max-width: 576px) {
              #${MODAL_ID} .modal-dialog {
                max-width: 100%;
                width: 100%;
                margin: 0;
              }
              #${MODAL_ID} .modal-content {
                border-radius: 0;
                min-height: 100vh;
              }
              #${MODAL_ID} iframe {
                height: calc(100vh - 56px) !important;
              }
            }
          </style>
          <div class="modal-dialog modal-xl" role="document">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title"></h5>
                <button type="button" class="close" data-dismiss="modal">
                  <span aria-hidden="true">&times;</span>
                </button>
              </div>
              <div class="modal-body p-0">
                <iframe style="width:100%;height:80vh;border:0;opacity:0;"
                        src="about:blank"></iframe>
              </div>
            </div>
          </div>
        </div>`);
      $("body").append($modal);
    }

    // Set the title as text, then append hazard pictograms (if any) as
    // HTML so the modal header mirrors what the listing row shows.
    const $title = $modal.find(".modal-title");
    $title.text(title);
    if (pictos_html) {
      $title.append(" ").append(pictos_html);
    }

    const $iframe = $modal.find("iframe");
    $iframe.off("load").on("load", () => {
      try {
        const iwin = $iframe[0].contentWindow;
        const href = iwin.location.href;
        // Forward ESC from the iframe document to close the parent modal.
        // Bootstrap's keyboard handler only listens on the parent document,
        // but focus lives inside the iframe when the user interacts with it.
        $(iwin.document).off("keydown.iframe_esc").on("keydown.iframe_esc", (ev) => {
          if (ev.key === "Escape" || ev.keyCode === 27) {
            $modal.modal("hide");
          }
        });

        const is_edit_form = edit_view === "edit";
        if (!is_edit_form) {
          // Non-edit view (e.g. sample view, manage_results): always hide
          // surrounding page elements and keep the modal open until the
          // user closes it manually.
          this.isolate_content_area(iwin.document);
          this.inject_change_detector(iwin);
          $iframe.css("opacity", "1");
        } else if (href.match(/\/(@@)?(base_)?edit(\?.*)?$/)) {
          // Still on an edit form (AT uses base_edit as form action,
          // so a validation error lands on /base_edit not /edit) —
          // isolate content on every load
          // (initial load and re-render on validation errors)
          this.isolate_content_area(iwin.document);
          this.inject_change_detector(iwin);
          $iframe.css("opacity", "1");
        } else {
          // Navigated away from the edit form: save or cancel triggered
          $modal.modal("hide");
        }
      } catch (ex) {
        // Ignore cross-origin access errors
      }
    });

    // Track whether changes were saved in the iframe.
    // Set to true by postMessage from inject_change_detector().
    let changes_made = false;
    $(window).off("message.iframe_edit").on("message.iframe_edit", (ev) => {
      if (ev.originalEvent.data === "senaite_changes_made") {
        changes_made = true;
      }
    });

    $iframe.css("opacity", "0").attr("src", url);

    // Reload only when changes were actually saved.
    $modal.off("hidden.bs.modal").on("hidden.bs.modal", () => {
      $(window).off("message.iframe_edit");
      if (changes_made) {
        window.location.reload();
      }
    });

    // Enable dragging and resizing once the modal is visible.
    // Bootstrap's margin:auto conflicts with jQuery UI's position
    // management, so we reset margin to 0 before the first drag/resize.
    $modal.off("shown.bs.modal").on("shown.bs.modal", () => {
      const $dialog = $modal.find(".modal-dialog");
      const $iframe = $modal.find("iframe");

      const reset_margin = () => $dialog.css("margin", "0");

      if (typeof $dialog.draggable === "function") {
        $dialog.draggable({
          handle: ".modal-header",
          // No containment — allow dragging partially off-screen
          start: reset_margin
        });
      }

      if (typeof $dialog.resizable === "function") {
        $dialog.resizable({
          handles: "ne, nw, se, sw",
          start: reset_margin,
          resize(_event, ui) {
            // Keep the iframe filling the modal body as it resizes
            const header_h = $dialog.find(".modal-header").outerHeight();
            $iframe.css("height", (ui.size.height - header_h) + "px");
          }
        });
      }
    });

    $modal.modal("show");
  }

  on_overlay_panel_click(e) {
    e.preventDefault();
    const $el = $(e.currentTarget);

    if (typeof $el.prepOverlay === 'function') {
      $el.prepOverlay({
        subtype: 'ajax',
        width: '80%',
        filter: '#content>*:not(div#portal-column-content)',
        config: {
          closeOnClick: true,
          closeOnEsc: true,
          onBeforeLoad: function () {
            this.getOverlay().draggable();
          },
          onLoad: function () {
            document.dispatchEvent(new Event("DOMContentLoaded"));
          }
        }
      });
      $el.click();
    } else {
      console.warn('prepOverlay not available. Consider updating or replacing it.');
    }
  }
};
