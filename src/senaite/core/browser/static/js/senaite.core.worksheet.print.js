/**
 * Worksheet Print Controller
 *
 * This controller is loaded in the worksheet print popup
 */
window.WorksheetPrintView = class WorksheetPrintView {
  constructor() {
    this.referrerCookieName = "ws.print.urlback";
    this.load = this.load.bind(this);
    this.loadBarcodes = this.loadBarcodes.bind(this);
    this.updateWorksheetView = this.updateWorksheetView.bind(this);
  }

  load() {
    let backUrl = document.referrer || window.site.read_cookie(this.referrerCookieName) || portal_url;
    window.site.set_cookie(this.referrerCookieName, backUrl);

    this.loadBarcodes();

    $("#print_button").on("click", (e) => {
      e.preventDefault();
      window.print();
    });

    $("#cancel_button").on("click", (e) => {
      e.preventDefault();
      window.location.href = backUrl;
    });

    $("#template, #numcols").on("change", () => {
      this.updateWorksheetView($("#template").val(), $("#numcols").val());
    });
  }

  updateWorksheetView(template, numCols) {
    const url = window.location.href;
    const $worksheet = $("#worksheet-printview");

    $worksheet.animate({ opacity: 0.2 }, "slow");

    $.ajax({
      url: url,
      type: "POST",
      data: {
        template: template,
        numcols: numCols,
      },
    }).always((response) => {
      const $response = $(response);
      const cssData = $response.find("#report-style").html();
      const htmlData = $response.find("#worksheet-printview").html();

      $("#report-style").html(cssData);
      $worksheet.html(htmlData);
      $worksheet.animate({ opacity: 1 }, "slow");

      this.loadBarcodes();
    });
  }

  loadBarcodes() {
    $(".barcode").each(function () {
      const $el = $(this);
      const id = $el.data("id");
      const code = $el.data("code");
      const barHeight = parseInt($el.data("barheight"), 10);
      const addQuietZone = Boolean($el.data("addquietzone"));
      const showHRI = Boolean($el.data("showhri"));

      $el.barcode(id, code, {
        barHeight: barHeight,
        addQuietZone: addQuietZone,
        showHRI: showHRI,
      });
    });
  }
}
