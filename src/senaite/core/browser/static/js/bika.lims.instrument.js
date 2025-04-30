/* Instrument Edit View Controller
 *
 * Handles the result folder rows when export interfaces are selected
 */
function InstrumentEditView() {
    const that = this;

    that.load = function() {
        $("#ResultFilesFolder_more").remove();
        const rows = $(".records_row_ResultFilesFolder");

        rows.each(function(index) {
            if (index > 0 && index === rows.length - 1) {
                $(this).remove();
            } else {
                $(this).children().eq(2).remove();
            }
        });
    };

    $(document).on("change", "#ImportDataInterface", function() {
        updateFolders();
    });

    function updateFolders() {
        const table = $("#ResultFilesFolder_table");
        const values = $("#ImportDataInterface").val() || [];
        const rows = $(".records_row_ResultFilesFolder");
        const templateRow = rows.last().clone();

        rows.remove();

        if (values.length === 0 || (values.length === 1 && values[0] === "")) {
            const newRow = templateRow.clone();
            newRow.find("input").val("");
            newRow.appendTo(table);
        } else {
            values.forEach(value => {
                if (value !== "") {
                    const newRow = templateRow.clone();
                    newRow.find("td").eq(0).find("input").val(value);
                    newRow.find("td").eq(1).find("input").val("");
                    newRow.appendTo(table);
                }
            });
            renameInputs();
        }
    }

    function renameInputs() {
        const rows = $(".records_row_ResultFilesFolder");
        rows.each(function(index) {
            $(this).find("input[id^='ResultFilesFolder']").each(function() {
                const parts = this.id.split("-");
                const newId = `${parts[0]}-${parts[1]}-${index}`;
                $(this).attr("id", newId);
            });
        });
    }
}


/* Instrument Certification Edit View Controller
 *
 * Shows/Hides the Agency field if the Internal checkbox is set
 */
function InstrumentCertificationEditView() {
    const that = this;

    that.load = function() {
        $(document).on("change", "#Internal", function() {
            loadAgency();
        });

        loadAgency();
    };

    function loadAgency() {
        if ($("#Internal").is(":checked")) {
            $("#archetypes-fieldname-Agency").hide();
        } else {
            $("#archetypes-fieldname-Agency").show();
        }
    }
}



/* Shows the D3 Graph for QC Analyses */
function InstrumentReferenceAnalysesView() {
    const that = this;

    that.load = function() {
        const data = $.parseJSON($("#graphdata").val());

        $.each(data, (key) => {
            $("#selanalyses").append(`<option value="${key}">${key}</option>`);
        });

        if ($("#selanalyses").val()) {
            updateQCSamples(data[$("#selanalyses").val()]);
            filterRows();
            drawControlChart(null, null);
        }

        $(document).on("change", "#selanalyses", function() {
            updateQCSamples(data[$(this).val()]);
            drawControlChart(null, null);
            filterRows();
        });

        $(document).on("change", "#selqcsample", function() {
            drawControlChart(null, null);
            filterRows();
        });

        $(document).on("change", "#interpolation", function() {
            drawControlChart(null, null);
        });

        $(document).on("mouseover", ".item-listing-tbody tr", function() {
            const uid = $(this).attr("uid");
            if (uid) {
                $(this).addClass("selected");
                $(`#chart svg g circle#${uid}`).trigger("__onmouseover");
            }
        });

        $(document).on("mouseout", ".item-listing-tbody tr", function() {
            $(this).removeClass("selected");
            const uid = $(this).attr("uid");
            if (uid) {
                $(`#chart svg g circle#${uid}`).trigger("__onmouseout");
            }
        });

        $(document).on("listing:loaded", "body", function(event) {
            filterRows();
        });

        $(document).on("click", "#printgraph", function(e) {
            e.preventDefault();
            const w = 670;
            const h = $("#chart").attr("height");
            drawControlChart(w, h);

            const WinPrint = window.open("", "", "width=800,height=900");
            const css = `<link href="${window.portal_url}/++plone++senaite.core.static/bundles/senaite.core.css" rel="stylesheet" type="text/css">`;
            const heading = $("span.documentFirstHeading").closest("h1").clone();
            const content = $("#content-core").clone();

            content.prepend(heading);
            content.find("#selanalyses").after(`<span class='bold'>${$("#selanalyses").val()}</span>`).hide();
            content.find("#interpolation").after(`<span class='bold'>${$("#interpolation").val()}</span>`).hide();
            content.find("#selqcsample").after(`<span class='bold'>${$("#selqcsample").val()}</span>`).hide();
            content.find("a#printgraph").hide();
            content.find("div.listing-container").children().last().hide();

            WinPrint.document.write(`<html><head>${css}</head><body>${content.html()}</body></html>`);
            WinPrint.document.close();
            WinPrint.focus();
            WinPrint.print();

            // Reset chart scaling
            $("#chart").css("width", "100%").removeAttr("height");
            drawControlChart(null, null);
            WinPrint.close();
        });

        $("div.bika-listing-table-container").fadeIn();
    };

    function updateQCSamples(qcsamples) {
        const selected = $("#selqcsample").val();
        $("#selqcsample").empty();
        $.each(qcsamples, (k, v) => {
            const selectedAttr = k === selected ? " selected" : "";
            $("#selqcsample").append(`<option value="${k}"${selectedAttr}>${k}</option>`);
        });
    }

    function filterRows() {
        const idqc = $("#selqcsample").val();
        const service = $("#selanalyses").val().split("(")[0].trim();
        let count = 0;

        $("div.results-info").remove();
        $(".contentstable tr").each(function() {
            const match = $(this).find("td.Service strong").html() === service &&
                          $(this).find("td.Partition a").html() === idqc;
            if (match) {
                $(this).fadeIn();
                count++;
            } else {
                $(this).hide();
            }
        });

        $(".listing-container").closest("div").before(`<div class="results-info mb-2">${count} results found</div>`);
    }

    function drawControlChart(width, height) {
        const analysisKey = $("#selanalyses").val();
        const refType = $("#selqcsample").val();
        const interpolation = $("#interpolation").val();
        const w = width || $("#chart").innerWidth();
        const h = height || $("#chart").innerHeight();

        const chartContainer = $("#chart").empty().css({ width: w, height: h }).show();
        let data = $.parseJSON($("#graphdata").val())[analysisKey];

        if (!data[refType] || data[refType].length === 0) {
            chartContainer.hide();
            return;
        }

        data = data[refType];
        const meta = data[data.length - 1];
        const unit = meta.unit || "";
        const uppertxt = `UCL (${meta.upper}${unit})`;
        const lowertxt = `LCL (${meta.lower}${unit})`;
        const centrtxt = `CL (${meta.target}${unit})`;

        const chart = new ControlChart();
        chart.setData(data);
        chart.setInterpolation(interpolation);
        chart.setXColumn("date");
        chart.setYColumn("result");
        chart.setPointId("id");
        chart.setYLabel(unit || "Result");
        chart.setXLabel("Date");
        chart.setUpperLimitText(uppertxt);
        chart.setLowerLimitText(lowertxt);
        chart.setCenterLimitText(centrtxt);
        chart.setCenterLimit(meta.target);
        chart.setUpperLimit(meta.upper);
        chart.setLowerLimit(meta.lower);
        chart.draw("#chart");
    }
}
