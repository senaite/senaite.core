/**
 * Instrument Edit Form Controller
 *
 * This controller is loaded for the instrument edit view, e.g.
 * `/senaite/bika_setup/bika_instruments/instrument-1`.
 */
window.InstrumentEditView = class InstrumentEditView {
  constructor() {
    this.load = this.load.bind(this);
    this.updateFolders = this.updateFolders.bind(this);
    this.renameInputs = this.renameInputs.bind(this);

    $(document).on("change", "#ImportDataInterface", this.updateFolders);
  }

  load() {
    $("#ResultFilesFolder_more").remove();
    const rows = $(".records_row_ResultFilesFolder");

    rows.each(function (index) {
      if (index > 0 && index === rows.length - 1) {
        $(this).remove();
      } else {
        $(this).children().eq(2).remove();
      }
    });
  }

  updateFolders() {
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
      this.renameInputs();
    }
  }

  renameInputs() {
    const rows = $(".records_row_ResultFilesFolder");
    rows.each(function (index) {
      $(this).find("input[id^='ResultFilesFolder']").each(function () {
        const parts = this.id.split("-");
        const newId = `${parts[0]}-${parts[1]}-${index}`;
        $(this).attr("id", newId);
      });
    });
  }
}


/**
 * Instrument Certification Edit Form Controller
 *
 * This controller is loaded for the instrument certification edit view, e.g.
 * `/senaite/bika_setup/bika_instruments/instrument-1/instrumentcertification-1`.
 */
window.InstrumentCertificationEditView = class InstrumentCertificationEditView {
  constructor() {
    this.load = this.load.bind(this);
    this.toggleAgency = this.toggleAgency.bind(this);
  }

  load() {
    $(document).on("change", "#Internal", this.toggleAgency);
    this.toggleAgency();
  }

  toggleAgency() {
    if ($("#Internal").is(":checked")) {
      $("#archetypes-fieldname-Agency").hide();
    } else {
      $("#archetypes-fieldname-Agency").show();
    }
  }
}


/**
 * Instrument QC Results Form Controller
 *
 * This controller is loaded for the instrument QC results view, e.g.
 * `/senaite/bika_setup/bika_instruments/instrument-1/referenceanalyses`.
 */
window.InstrumentReferenceAnalysesView = class InstrumentReferenceAnalysesView {
  constructor() {
    this.load = this.load.bind(this);
    this.updateQCSamples = this.updateQCSamples.bind(this);
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

    $.each(data, (key) => {
      $("#selanalyses").append(`<option value="${key}">${key}</option>`);
    });

    if ($("#selanalyses").val()) {
      this.updateQCSamples(data[$("#selanalyses").val()]);
      this.filterRows();
      this.drawControlChart();
    }

    $(document).on("change", "#selanalyses", () => {
      this.updateQCSamples(data[$("#selanalyses").val()]);
      this.drawControlChart();
      this.filterRows();
    });

    $(document).on("change", "#selqcsample", () => {
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
      $(this).removeClass("selected");
      const uid = $(this).attr("uid");
      if (uid) {
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
      const w = 670;
      const h = $("#chart").attr("height");

      this.drawControlChart(w, h);

      const win = window.open("", "", "width=800,height=900");
      const css = `<link href="${window.portal_url}/++plone++senaite.core.static/bundles/senaite.core.css" rel="stylesheet">`;
      const heading = $("span.documentFirstHeading").closest("h1").clone();
      const content = $("#content-core").clone();

      content.prepend(heading);
      content.find("#selanalyses").after(`<span class='bold'>${$("#selanalyses").val()}</span>`).hide();
      content.find("#interpolation").after(`<span class='bold'>${$("#interpolation").val()}</span>`).hide();
      content.find("#selqcsample").after(`<span class='bold'>${$("#selqcsample").val()}</span>`).hide();
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

  updateQCSamples(qcsamples) {
    const selected = $("#selqcsample").val();
    $("#selqcsample").empty();

    $.each(qcsamples, (k, v) => {
      const selectedAttr = k === selected ? " selected" : "";
      $("#selqcsample").append(`<option value="${k}"${selectedAttr}>${k}</option>`);
    });
  }

  filterRows() {
    let service = null;
    let idqc = $("#selqcsample").val();

    let service_select = $("#selanalyses").val();
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
      const match =
        $(this).find("td.Service strong").html() === service &&
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

  drawControlChart(width, height) {
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
    const chart = new ControlChart();

    chart.setData(data);
    chart.setInterpolation(interpolation);
    chart.setXColumn("date");
    chart.setYColumn("result");
    chart.setPointId("id");
    chart.setYLabel(unit);
    chart.setXLabel("Date");
    chart.setUpperLimitText(`UCL (${meta.upper}${unit})`);
    chart.setLowerLimitText(`LCL (${meta.lower}${unit})`);
    chart.setCenterLimitText(`CL (${meta.target}${unit})`);
    chart.setCenterLimit(meta.target);
    chart.setUpperLimit(meta.upper);
    chart.setLowerLimit(meta.lower);
    chart.draw("#chart");
  }
}
