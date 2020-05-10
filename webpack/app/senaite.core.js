import $ from "jquery";

document.addEventListener("DOMContentLoaded", () => {
  console.debug("*** SENAITE JS LOADED ***");

  // global variables for backward compatibility
  window.portal_url = document.querySelector("body").dataset.portalUrl

  $("#sidebar-header").on("click", function () {
    $("#sidebar").toggleClass("minimized");
  });

});
