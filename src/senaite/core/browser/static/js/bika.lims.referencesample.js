/**
 * Controller class for Reference Sample Analyses View
 */
function ReferenceSampleAnalysesView() {
    const that = this;

    /**
     * Entry-point method
     */
    that.load = function() {
        const data = $.parseJSON($("#graphdata").val());
        let qcrec = false;

        // Populate analyses selector
        $.each(data, function(key, value) {
            $("#selanalyses").append(`<option value="${key}">${key}</option>`);
            if (!qcrec) {
                $.each(value, function(k) {
                    $("#selqcsample").val(k);
                    return false; // break inner loop
                });
                qcrec = true;
            }
        });

        // Initial draw
        if ($("#selanalyses").val()) {
            filterRows();
            drawControlChart(null, null);
        }

        // Change handlers
        $(document).on("change", "#selanalyses", function() {
            drawControlChart(null, null);
            filterRows();
        });

        $(document).on("change", "#interpolation", function() {
            drawControlChart(null, null);
        });

        // Mouseover/mouseout on table rows
        $(document).on("mouseover", ".item-listing-tbody tr", function() {
            const uid = $(this).attr("uid");
            if (uid) {
                $(this).addClass("selected");
                $(`#chart svg g circle#${uid}`).trigger("__onmouseover");
            }
        });

        $(document).on("mouseout", ".item-listing-tbody tr", function() {
            const uid = $(this).attr("uid");
            if (uid) {
                $(this).removeClass("selected");
                $(`#chart svg g circle#${uid}`).trigger("__onmouseout");
            }
        });

        $(document).on("listing:loaded", "body", function(event) {
            filterRows();
        });

        // Print graph handler
        $(document).on("click", "#printgraph", function(e) {
            e.preventDefault();

            const selectedValue = $("#selanalyses").val();
            $("#selanalyses option").prop("selected", false);
            $(`#selanalyses option[value="${selectedValue}"]`).prop("selected", true);

            const w = 670;
            const h = $("#chart").attr("height");
            drawControlChart(w, h);

            const WinPrint = window.open("", "", "width=800,height=900");
            const css = `<link href="${window.portal_url}/++plone++senaite.core.static/bundles/senaite.core.css" rel="stylesheet" type="text/css">`;
            const heading = $("span.documentFirstHeading").closest("h1").clone();
            const content = $("#content-core").clone();

            content.prepend(heading);
            content.find("#selanalyses").after(`<span class="font-weight-bold">${selectedValue}</span>`).hide();
            content.find("#interpolation").after(`<span class="font-weight-bold">${$("#interpolation").val()}</span>`).hide();
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

    /**
     * Hide/Show the reference analyses rows from the table
     */
    function filterRows() {
        const idqc = $("#selanalyses").val();
        const service = $("#selanalyses").val().split("(")[0].trim();
        let count = 0;

        $("div.results-info").remove();
        $(".contentstable tr").each(function() {
            const match = $(this).find("td.Service strong").html() === service
            if (match) {
                $(this).fadeIn();
                count++;
            } else {
                $(this).hide();
            }
        });

        $(".listing-container").closest("div").before(`<div class="results-info mb-2">${count} results found</div>`);
    }

    /**
     * Draws the control chart
     */
    function drawControlChart(width, height) {
        const analysisKey = $("#selanalyses").val();
        const refType = $("#selqcsample").val();
        const interpolation = $("#interpolation").val();
        const w = width === null ? $("#chart").innerWidth() : width;
        const h = height === null ? $("#chart").innerHeight() : height;

        $("#chart").css({ width: w, height: h }).empty().show();

        let data = $.parseJSON($("#graphdata").val())[analysisKey];

        if (!data || !data[refType] || data[refType].length === 0) {
            $("#chart").hide();
            return;
        }

        data = data[refType];
        const lastPoint = data[data.length - 1];
        const unit = lastPoint.unit || "";
        const upper = lastPoint.upper;
        const lower = lastPoint.lower;
        const target = lastPoint.target;

        const ylabel = unit ? unit : "Result";

        const uppertxt = `UCL (${upper}${unit})`;
        const lowertxt = `LCL (${lower}${unit})`;
        const centrtxt = `CL (${target}${unit})`;

        const chart = new ControlChart();
        chart.setData(data);
        chart.setInterpolation(interpolation);
        chart.setXColumn("date");
        chart.setYColumn("result");
        chart.setPointId("id");
        chart.setYLabel(ylabel);
        chart.setXLabel("Date");
        chart.setUpperLimitText(uppertxt);
        chart.setLowerLimitText(lowertxt);
        chart.setCenterLimitText(centrtxt);
        chart.setCenterLimit(target);
        chart.setUpperLimit(upper);
        chart.setLowerLimit(lower);
        chart.draw("#chart");
    }
}
