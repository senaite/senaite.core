/* Used in AT DataGridField, e.g. in Setup -> ID Server */
jQuery(function($) {
    function recordswidget_lookups(elements) {
        var inputs = elements === undefined
            ? $(".ArchetypesRecordsWidget [combogrid_options]").not(".has_combogrid_widget")
            : elements;

        inputs.each(function() {
            var $element = $(this);
            var options = $.parseJSON($element.attr("combogrid_options"));

            if (!options) {
                return;
            }

            options.select = function(event, ui) {
                event.preventDefault();
                var fieldName = $(this).attr("name").split(".")[0];
                var key = "";
                if ($(this).attr("name").includes(".")) {
                    key = $(this).attr("name").split(".")[1].split(":")[0];
                }
                var rowNr = parseInt(this.id.split("-").pop(), 10);
                $(this).val(ui.item[key]);

                var colModel = $.parseJSON($(this).attr("combogrid_options")).colModel || [];
                colModel.forEach(function(col) {
                    var colname = col.columnName;
                    if (colname !== key) {
                        var $field = $("#" + fieldName + "-" + colname + "-" + rowNr);
                        if ($field.length === 1) {
                            $field.val(ui.item[colname]);
                        }
                    }
                });
            };

            if (window.location.href.includes("portal_factory")) {
                options.url = window.location.href.split("/portal_factory")[0] + "/" + options.url;
            }

            options.url += "?_authenticator=" + $("input[name='_authenticator']").val();
            $element.combogrid(options);
        });
    }

    function recordswidget_loadEventHandlers() {
        $(document).on("focus", ".ArchetypesRecordsWidget [combogrid_options]", function() {
            var $this = $(this);
            var options = $.parseJSON($this.attr("combogrid_options"));

            if (!options) {
                return;
            }

            $this.val("");

            var fieldName = $this.attr("name").split(".")[0];
            var key = "";
            if ($this.attr("name").includes(".")) {
                key = $this.attr("name").split(".")[1].split(":")[0];
            }

            var colModel = options.colModel || [];
            var rowNr = parseInt(this.id.split("-").pop(), 10);

            colModel.forEach(function(col) {
                var colname = col.columnName;
                if (colname !== key) {
                    var $field = $("#" + fieldName + "-" + colname + "-" + rowNr);
                    if ($field.length === 1) {
                        $field.val("");
                    }
                }
            });
        });

        $(document).on("click", "input[id$='_more']", function() {
            var fieldname = $(this).attr("id").split("_")[0];
            var $table = $("#" + fieldname + "_table");
            var $rows = $(".records_row_" + fieldname);
            var $lastRow = $rows.last().clone();

            var $foundInputs = $lastRow.find("input[id^='" + fieldname + "'], select[id^='" + fieldname + "']");

            $foundInputs.each(function() {
                var idParts = this.id.split("-");
                var prefix = idParts[0] + "-" + idParts[1];
                var nr = parseInt(idParts[2], 10) + 1;

                $(this).attr("id", prefix + "-" + nr).val("");
            });

            // Validate required fields before adding
            var isValid = true;
            $foundInputs.each(function() {
                if ($(this).hasClass("required") && $(this).val() === "") {
                    window.bika.lims.portalMessage(this.id.split("-")[1] + ": " + _p("Input is required but not given."));
                    isValid = false;
                    return false; // break loop
                }
            });

            if (!isValid) {
                return false;
            }

            // Clear values
            $lastRow.children().each(function() {
                var $input = $(this).children().first();
                $input.val("").removeClass("hasDatepicker");
            });

            $lastRow.appendTo($table);
            recordswidget_lookups($lastRow.find("[combogrid_options]"));
        });

        $(document).on("click", ".rw_deletebtn", function() {
            var $row = $(this).closest("tr");
            var $siblings = $row.siblings("tr");
            if ($siblings.length >= 1) {
                $row.remove();
            }
        });
    }

    recordswidget_lookups();
    recordswidget_loadEventHandlers();
});
