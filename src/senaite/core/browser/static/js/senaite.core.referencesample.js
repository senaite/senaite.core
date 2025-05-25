/**
 * Reference Sample Controller
 *
 * This controller is loaded for the reference samples, e.g.
 * `/senaite/setup/suppliers/supplier-10/QC-001/analyses`.
 */
window.ReferenceSampleAnalysesView = class ReferenceSampleAnalysesView {
  constructor() {
    this.load = this.load.bind(this);
    this.filterRows = this.filterRows.bind(this);
    this.drawControlChart = this.drawControlChart.bind(this);
  }

  load() {
    const gd = $("#graphdata")
    // return if not found
    if (!gd.length) {
      console.warn("No element with graph data found!")
      return;
    };
    const data = $.parseJSON(gd.val());
    let qcrec = false;

    // Populate analyses selector
    $.each(data, (key, value) => {
      $("#selanalyses").append(`<option value="${key}">${key}</option>`);
      if (!qcrec) {
        $.each(value, (k) => {
          $("#selqcsample").val(k);
          return false; // break inner loop
        });
        qcrec = true;
      }
    });

    // Initial draw
    if ($("#selanalyses").val()) {
      this.filterRows();
      this.drawControlChart();
    }

    // Change handlers
    $(document).on("change", "#selanalyses", () => {
      this.drawControlChart();
      this.filterRows();
    });

    $(document).on("change", "#interpolation", this.drawControlChart);

    $(document).on("mouseover", ".item-listing-tbody tr", function () {
      const uid = $(this).attr("uid");
      if (uid) {
        $(this).addClass("selected");
        $(`#chart svg g circle#${uid}`).trigger("__onmouseover");
      }
    });

    $(document).on("mouseout", ".item-listing-tbody tr", function () {
      const uid = $(this).attr("uid");
      if (uid) {
        $(this).removeClass("selected");
        $(`#chart svg g circle#${uid}`).trigger("__onmouseout");
      }
    });

    $(document).on("listing:loaded", "body", (event) => {
      // wait until the listing view rendered the table
      setTimeout(() => {
        this.filterRows();
      }, 500);
    });

    $(document).on("click", "#printgraph", (e) => {
      e.preventDefault();

      const selectedValue = $("#selanalyses").val();
      $("#selanalyses option").prop("selected", false);
      $(`#selanalyses option[value="${selectedValue}"]`).prop("selected", true);

      const w = 670;
      const h = $("#chart").attr("height");
      this.drawControlChart(w, h);

      const win = window.open("", "", "width=800,height=900");
      const css = `<link href="${window.portal_url}/++plone++senaite.core.static/bundles/senaite.core.css" rel="stylesheet">`;
      const heading = $("span.documentFirstHeading").closest("h1").clone();
      const content = $("#content-core").clone();

      content.prepend(heading);
      content.find("#selanalyses").after(`<span class="font-weight-bold">${selectedValue}</span>`).hide();
      content.find("#interpolation").after(`<span class="font-weight-bold">${$("#interpolation").val()}</span>`).hide();
      content.find("a#printgraph").hide();
      content.find("div.listing-container").children().last().hide();

      win.document.write(`<html><head>${css}</head><body>${content.html()}</body></html>`);
      win.document.close();
      win.focus();
      win.print();
      win.close();

      $("#chart").css("width", "100%").removeAttr("height");
      this.drawControlChart();
    });

    $("div.bika-listing-table-container").fadeIn();
  }

  filterRows() {
    let service = null;

    const service_select = $("#selanalyses").val();
    if (service_select) {
      const matches = [...service_select.matchAll(/\([^()]*\)/g)];
      if (matches.length >= 2) {
        const last = matches[matches.length - 1][0];
        service = service_select.replace(last, "").trim();
      } else if (matches.length === 1) {
        service = service_select.replace(matches[0][0], '').trim();
      }
    }

    let count = 0;

    $("div.results-info").remove();

    $(".contentstable tr").each(function () {
      const match = $(this).find("td.Service strong").html() === service;
      if (match) {
        $(this).fadeIn();
        count++;
      } else {
        $(this).hide();
      }
    });

    $(".listing-container").closest("div").before(
      `<div class="results-info mb-2">${count} results found</div>`
    );
  }

  drawControlChart(width = null, height = null) {
    const analysisKey = $("#selanalyses").val();
    const refType = $("#selqcsample").val();
    const interpolation = $("#interpolation").val();
    const w = width || $("#chart").innerWidth();
    const h = height || $("#chart").innerHeight();

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

    const chart = new ControlChart();
    chart.setData(data);
    chart.setInterpolation(interpolation);
    chart.setXColumn("date");
    chart.setYColumn("result");
    chart.setPointId("id");
    chart.setYLabel(unit || "Result");
    chart.setXLabel("Date");
    chart.setUpperLimitText(`UCL (${upper}${unit})`);
    chart.setLowerLimitText(`LCL (${lower}${unit})`);
    chart.setCenterLimitText(`CL (${target}${unit})`);
    chart.setCenterLimit(target);
    chart.setUpperLimit(upper);
    chart.setLowerLimit(lower);
    chart.draw("#chart");
  }
}
