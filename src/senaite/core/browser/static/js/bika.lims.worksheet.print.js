/**
 * Controller class for Worksheed Print View
 */
function WorksheetPrintView() {

  const referrerCookieName = "ws.print.urlback";

  this.load = function () {
    let backUrl = document.referrer || senaite.core.controllers.SiteView.readCookie(referrerCookieName) || portal_url;
    senaite.core.controllers.SiteView.setCookie(referrerCookieName, backUrl);

    loadBarcodes();

    $("#print_button").on("click", function (e) {
      e.preventDefault();
      window.print();
    });

    $("#cancel_button").on("click", function (e) {
      e.preventDefault();
      window.location.href = backUrl;
    });

    $("#template, #numcols").on("change", function () {
      updateWorksheetView($("#template").val(), $("#numcols").val());
    });
  };

  function updateWorksheetView(template, numCols) {
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
    }).always(function (response) {
      const cssData = $(response).find("#report-style").html();
      const htmlData = $(response).find("#worksheet-printview").html();

      $("#report-style").html(cssData);
      $worksheet.html(htmlData);
      $worksheet.animate({ opacity: 1 }, "slow");

      loadBarcodes();
    });
  }

  function loadBarcodes() {
    $(".barcode").each(function () {
      const $this = $(this);
      const id = $this.data("id");
      const code = $this.data("code");
      const barHeight = parseInt($this.data("barheight"));
      const addQuietZone = Boolean($this.data("addquietzone"));
      const showHRI = Boolean($this.data("showhri"));

      $this.barcode(id, code, {
        barHeight: barHeight,
        addQuietZone: addQuietZone,
        showHRI: showHRI,
      });
    });
  }

}
