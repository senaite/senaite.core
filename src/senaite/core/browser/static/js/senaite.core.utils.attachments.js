/**
 * Attachments Controller
 *
 * This controller is loaded if the attachments viewlet is displayed, e.g. for samples or worksheets
 */
window.AttachmentsUtils = class AttachmentsUtils {
  constructor() {
    this.load = this.load.bind(this);
  }

  load() {
    // Worksheets need to check these before enabling Add button
    $("#AttachFile, #Service, #Analysis").on("change", (event) => {
      const attachfile = $("#AttachFile").val() || "";
      let service = $("#Service").val() || "";
      let analysis = $("#Analysis").val() || "";

      if (event.target.id === "Service") {
        $("#Analysis").val("");
        analysis = "";
      }

      if (event.target.id === "Analysis") {
        $("#Service").val("");
        service = "";
      }

      if (attachfile !== "" && (service !== "" || analysis !== "")) {
        $("#addButton").removeAttr("disabled");
      } else {
        $("#addButton").prop("disabled", true);
      }
    });
  }
}
