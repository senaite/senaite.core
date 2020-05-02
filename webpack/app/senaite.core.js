import "./senaite.core.scss";
import "bootstrap";


document.addEventListener("DOMContentLoaded", () => {
  console.debug("*** SENAITE JS LOADED ***");

  $('#sidebar-header').on('click', function () {
    $("#sidebar").toggleClass("active");
  });

});
