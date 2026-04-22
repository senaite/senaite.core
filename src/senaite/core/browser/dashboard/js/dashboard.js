/**
 * SENAITE Dashboard
 *
 * Async loading of status cards and statistics sections.
 * Reads configuration from #dashboard-config data attributes.
 */
document.addEventListener("DOMContentLoaded", function () {

  var config = document.getElementById("dashboard-config");
  if (!config) return;

  var baseUrl = config.getAttribute("data-base-url");
  var periodicity = config.getAttribute("data-periodicity");
  var canViewStats = config.getAttribute(
    "data-can-view-stats") === "true";
  var portalUrl = config.getAttribute("data-portal-url");
  var dateFrom = config.getAttribute("data-date-from");
  var dateTo = config.getAttribute("data-date-to");

  // Load overview (cards + links) together
  Promise.all([
    fetchSection("status_cards"),
    fetchSection("quick_links")
  ]).then(function (results) {
    renderOverview(results[0], results[1]);
  });

  // Load statistics sections
  if (canViewStats) {
    ["analysisrequests", "analyses", "worksheets"].forEach(
      function (id) {
        fetchSection(id).then(function (data) {
          renderStatisticsSection(id, data);
        });
      }
    );
  }

  function fetchSection(section) {
    var url = baseUrl
      + "?section=" + section
      + "&p=" + periodicity;
    return fetch(url, { credentials: "same-origin" })
      .then(function (r) { return r.json(); })
      .catch(function (err) {
        console.error(
          "Dashboard: failed to load " + section, err);
        return null;
      });
  }

  // --- Overview (cards + links + empty state) ---

  function renderOverview(cards, links) {
    var el = document.getElementById("dashboard-overview");
    if (!el) return;
    el.textContent = "";

    var hasCards = cards && cards.length > 0;
    var hasLinks = links && links.length > 0;

    // No permissions at all -- show friendly message
    if (!hasCards && !hasLinks) {
      var msg = document.createElement("div");
      msg.className = "text-muted py-4";
      var icon = document.createElement("i");
      icon.className = "fas fa-info-circle mr-2";
      msg.appendChild(icon);
      msg.appendChild(document.createTextNode(
        "No actions available. Please contact your "
        + "laboratory manager to get permissions "
        + "assigned."));
      el.appendChild(msg);
      return;
    }

    // Status cards
    if (hasCards) {
      var heading = document.createElement("h2");
      heading.className = "h6 text-uppercase text-muted "
        + "font-weight-bold mb-3";
      heading.textContent = "Status";
      el.appendChild(heading);

      var wrap = document.createElement("div");
      wrap.className = "d-flex flex-wrap mb-4";
      wrap.style.cssText = "gap: 15px;";
      cards.forEach(function (card) {
        wrap.appendChild(buildStatusCard(card));
      });
      el.appendChild(wrap);
    }

    // Quick links
    if (hasLinks) {
      var heading2 = document.createElement("h2");
      heading2.className = "h6 text-uppercase text-muted "
        + "font-weight-bold mb-3";
      heading2.textContent = "Quick Actions";
      el.appendChild(heading2);

      var linkWrap = document.createElement("div");
      linkWrap.className = "mb-4";
      links.forEach(function (link) {
        var a = document.createElement("a");
        a.className =
          "btn btn-outline-secondary btn-sm mr-2 mb-2";
        a.href = link.url;
        var i = document.createElement("i");
        i.className = "fas " + link.icon + " mr-1";
        a.appendChild(i);
        a.appendChild(
          document.createTextNode(link.title));
        linkWrap.appendChild(a);
      });
      el.appendChild(linkWrap);
    }
  }

  function buildStatusCard(card) {
    var a = document.createElement("a");
    a.className = "card text-decoration-none";
    a.style.cssText = "flex:1 1 140px;max-width:200px;";
    a.href = card.url;

    var body = document.createElement("div");
    body.className = "card-body text-center py-3 px-3";

    var iconDiv = document.createElement("div");
    iconDiv.className = "text-muted mb-2";
    var i = document.createElement("i");
    i.className = "fas " + card.icon;
    iconDiv.appendChild(i);

    var count = document.createElement("div");
    count.className = "h2 mb-1 font-weight-bold";
    count.textContent = card.count;

    var title = document.createElement("div");
    title.className = "small text-muted text-nowrap";
    title.textContent = card.title;

    body.appendChild(iconDiv);
    body.appendChild(count);
    body.appendChild(title);
    a.appendChild(body);
    return a;
  }

  // --- Statistics Sections ---

  function renderStatisticsSection(sectionId, section) {
    var container = document.getElementById(
      "dashboard-section-" + sectionId);
    if (!container || !section) return;

    var panels = section.panels || [];
    var simplePanels = panels.filter(function (p) {
      return p.type === "simple-panel";
    });
    var chartPanels = panels.filter(function (p) {
      return p.type === "bar-chart-panel";
    });

    container.textContent = "";

    // Section heading
    var head = document.createElement("div");
    head.className = "dashboard-section-head";
    var h2 = document.createElement("h2");
    h2.className = "h6 text-uppercase text-muted"
      + " font-weight-bold border-bottom pb-2";
    h2.textContent = section.title;
    head.appendChild(h2);
    container.appendChild(head);

    // Chart toggle + chart container
    chartPanels.forEach(function (panel, idx) {
      var chartId = "bar-chart-" + sectionId + "-" + idx;
      var data = panel.data || "[]";
      if (data === "[]") return;

      var btnWrap = document.createElement("div");
      btnWrap.className = "mb-3";
      var btn = document.createElement("a");
      btn.className = "btn btn-outline-secondary btn-sm";
      btn.href = "#";
      btn.setAttribute("target-id", chartId);
      var btnIcon = document.createElement("i");
      btnIcon.className = "fas fa-chart-bar mr-1";
      btn.appendChild(btnIcon);
      btn.appendChild(
        document.createTextNode("Show/hide timeline"));
      btnWrap.appendChild(btn);
      container.appendChild(btnWrap);

      var period = document.createElement("div");
      period.className = "bar-chart-period";
      period.id = chartId + "-period";
      period.style.display = "none";

      var h3 = document.createElement("h3");
      h3.className = "h6";
      h3.textContent = panel.name || "";
      period.appendChild(h3);

      var legendDiv = document.createElement("div");
      legendDiv.className = "h2-legend mb-3";
      legendDiv.textContent = "From " + dateFrom
        + " to " + dateTo + " (updated every 2 hours)";
      period.appendChild(legendDiv);

      period.appendChild(buildNavPills());
      container.appendChild(period);

      var chartDiv = document.createElement("div");
      chartDiv.className = "bar-chart";
      chartDiv.id = chartId;
      chartDiv.setAttribute("data", data);
      chartDiv.setAttribute(
        "data-colors", panel.datacolors || "{}");
      chartDiv.style.display = "none";
      var noData = document.createElement("div");
      noData.className = "bar-chart-no-data";
      noData.textContent =
        "No data for the selected period";
      chartDiv.appendChild(noData);
      container.appendChild(chartDiv);
    });

    // Simple panel cards
    if (simplePanels.length > 0) {
      var wrap = document.createElement("div");
      wrap.className = "d-flex flex-wrap mb-3";
      wrap.style.cssText = "gap: 15px;";

      simplePanels.forEach(function (panel) {
        wrap.appendChild(buildPanelCard(panel));
      });

      container.appendChild(wrap);
    }

    initChartToggles(container);
  }

  function buildPanelCard(panel) {
    var a = document.createElement("a");
    a.className = "card text-decoration-none";
    a.style.cssText =
      "flex:1 1 140px;max-width:200px;overflow:hidden;";
    a.href = panel.link;

    var body = document.createElement("div");
    body.className = "card-body text-center py-3 px-3";

    var num = document.createElement("div");
    num.className = "h2 mb-1 font-weight-bold"
      + (panel.number === 0 ? " text-muted" : "");
    num.textContent = panel.number;

    var desc = document.createElement("div");
    desc.className = "small text-muted text-nowrap";
    desc.textContent = panel.description;

    body.appendChild(num);
    body.appendChild(desc);

    if (panel.legend) {
      var leg = document.createElement("div");
      leg.className = "small text-muted text-nowrap mt-1";
      leg.textContent = panel.legend;
      body.appendChild(leg);
    }

    a.appendChild(body);

    // Progress bar
    var progress = document.createElement("div");
    progress.className = "progress";
    progress.style.cssText =
      "height: 4px; border-radius: 0;";
    var bar = document.createElement("div");
    bar.className = "progress-bar";
    bar.setAttribute("role", "progressbar");
    var pct = panel.percentage || 0;
    bar.style.width = pct + "%";
    bar.setAttribute("aria-valuenow", pct);
    bar.setAttribute("aria-valuemin", "0");
    bar.setAttribute("aria-valuemax", "100");
    progress.appendChild(bar);
    a.appendChild(progress);

    return a;
  }

  function buildNavPills() {
    var pills = [
      { label: "Daily", value: "d" },
      { label: "Weekly", value: "w" },
      { label: "Monthly", value: "m" },
      { label: "Quarterly", value: "q" },
      { label: "Biannual", value: "b" },
      { label: "Yearly", value: "y" }
    ];
    var ul = document.createElement("ul");
    ul.className = "nav nav-pills nav-pills-sm mb-3";
    pills.forEach(function (pill) {
      var li = document.createElement("li");
      li.className = "nav-item";
      var a = document.createElement("a");
      a.className = "nav-link py-1 px-2 small"
        + (pill.value === periodicity ? " active" : "");
      a.href = portalUrl
        + "/senaite-dashboard?p=" + pill.value;
      a.textContent = pill.label;
      li.appendChild(a);
      ul.appendChild(li);
    });
    return ul;
  }

  // --- Chart Toggle + D3 Rendering ---

  function initChartToggles(container) {
    $(container).find("a[target-id]").on(
      "click", function (e) {
        e.preventDefault();
        var chartId = $(this).attr("target-id");
        if ($("#" + chartId).is(":visible")) {
          senaite.core.controllers.SiteView.set_cookie(
            "visible." + chartId, 0);
          $("#" + chartId + "-period").hide();
          $("#" + chartId).hide();
        } else {
          senaite.core.controllers.SiteView.set_cookie(
            "visible." + chartId, 1);
          $("#" + chartId + "-period").show();
          $("#" + chartId).show();
          loadBarChart(chartId);
        }
      }
    );

    // Auto-show previously visible charts
    $(container).find(".bar-chart").each(function () {
      var id = $(this).attr("id");
      var vis = senaite.core.controllers.SiteView.read_cookie(
        "visible." + id);
      if (vis == 1) {
        $("#" + id).show();
        $("#" + id + "-period").show();
        loadBarChart(id);
      }
    });
  }

  function loadBarChart(id) {
    var container = $("#" + id);
    container.find("svg").remove();
    var raw_data = JSON.parse(container.attr("data"));
    var data = raw_data.data;
    if (data.length === 0
        || Object.keys(data[0]).length < 2) return;
    var states = raw_data.states.filter(function (key) {
      return key in data[0];
    });

    container.html("");
    var margin = {
      top: 20, right: 200, bottom: 70, left: 50
    };
    var width = container.innerWidth()
      - margin.left - margin.right;
    var height = 320 - margin.top - margin.bottom;

    var x = d3.scaleBand()
      .rangeRound([0, width]).padding(0.1);
    var y = d3.scaleLinear().range([height, 0]);
    var colors = JSON.parse(
      container.attr("data-colors"));
    var color = d3.scaleOrdinal().range(colors);
    color.domain(states);

    var xAxis = d3.axisBottom(x).ticks(10);
    var yAxis = d3.axisLeft(y)
      .tickSize(-width)
      .tickFormat(d3.format(".2s"));

    var svg = d3.select("#" + id).append("svg")
      .attr("width",
        width + margin.left + margin.right)
      .attr("height",
        height + margin.top + margin.bottom)
      .append("g")
      .attr("transform",
        "translate(" + margin.left
        + "," + margin.top + ")");

    data.forEach(function (d) {
      var y0 = 0;
      d.statuses = color.domain().map(function (name) {
        return { name: name, y0: y0, y1: y0 += +d[name] };
      });
      d.total = d.statuses[d.statuses.length - 1].y1;
    });

    x.domain(data.map(function (d) {
      return d.date;
    }));
    y.domain([0, d3.max(data, function (d) {
      return d.total;
    })]);

    svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis)
      .selectAll("text")
      .style("text-anchor", "end")
      .style("font-size", "9px")
      .attr("dx", "-.6em")
      .attr("dy", ".15em")
      .attr("transform", "rotate(-45)");

    svg.append("g")
      .attr("class", "y axis")
      .call(yAxis);

    var state = svg.selectAll(".state")
      .data(data).enter().append("g")
      .attr("class", "g")
      .attr("transform", function (d) {
        return "translate(" + x(d.date) + ",0)";
      });

    state.selectAll("rect")
      .data(function (d) { return d.statuses; })
      .enter()
      .append("rect")
      .attr("width", x.bandwidth())
      .attr("y", function (d) { return y(d.y1); })
      .attr("height", function (d) {
        return y(d.y0) - y(d.y1);
      })
      .attr("data-value", function (d) {
        return d.y1 - d.y0;
      })
      .attr("data-name", function (d) {
        return d.name;
      })
      .style("fill", function (d) {
        return colors[d.name];
      })
      .on("mouseover", function () {
        var name = d3.select(this).attr("data-name");
        var val = name + ": "
          + d3.select(this).attr("data-value");
        var g = d3.select(this.parentNode);
        var tooltip = g.append("g")
          .attr("class", "graph-tooltip");
        var text = tooltip.append("text")
          .attr("fill", "#293333")
          .style("font-size", "11px")
          .style("font-weight", "bold")
          .attr("x", 0)
          .attr("y", -8)
          .text(val);
        var bbox = text.node().getBBox();
        tooltip.insert("rect", "text")
          .attr("x", bbox.x - 4)
          .attr("y", bbox.y - 2)
          .attr("width", bbox.width + 8)
          .attr("height", bbox.height + 4)
          .attr("rx", 3)
          .style("fill", "#fff")
          .style("fill-opacity", 0.9)
          .style("stroke", "#d7dbdc")
          .style("stroke-width", 1);
      })
      .on("mouseout", function () {
        d3.select(this.parentNode)
          .selectAll(".graph-tooltip").remove();
      });

    var legend = svg.selectAll(".legend")
      .data(states.slice().reverse())
      .enter().append("g")
      .attr("class", "legend")
      .attr("transform", function (d, i) {
        return "translate(0," + (i * 18) + ")";
      });

    legend.append("rect")
      .attr("x", width + 15)
      .attr("y", 2)
      .attr("width", 8)
      .attr("height", 8)
      .attr("rx", 2)
      .style("fill", function (d) {
        return colors[d];
      });

    legend.append("text")
      .attr("x", width + 30)
      .attr("y", 0)
      .attr("dy", "10")
      .style("font-size", "11px")
      .text(function (d) { return d; });
  }

});
