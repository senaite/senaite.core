import "./senaite.core.scss";
import "bootstrap";


document.addEventListener("DOMContentLoaded", () => {
  console.debug("*** SENAITE JS LOADED ***");

  $('#sidebarCollapse').on('click', function () {
    $("#sidebar").toggleClass("active");
  });

});
