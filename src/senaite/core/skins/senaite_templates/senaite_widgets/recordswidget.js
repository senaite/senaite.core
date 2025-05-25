jQuery(function ($) {

  // Add row handler
  $(document).on("click", "input[id$='_more']", function () {
    var fieldName = this.id.split("_")[0];
    var $table = $("#" + fieldName + "_table");
    var $rows = $(".records_row_" + fieldName);
    var $lastRow = $rows.last().clone();
    $table.append($lastRow);
  });

  // Delete row handler
  $(document).on("click", ".rw_deletebtn", function () {
    var $row = $(this).closest("tr");
    if ($row.siblings("tr").length > 0) {
      $row.remove();
    }
  });

});
