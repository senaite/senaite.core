/** D3js Control Chart
 *
 * Wrapper class for D3 control chart used for QC samples
 *
 * Used in:
 *   - bika.lims.instrument.js
 *   - bika.lims.referencesample.js
 */
class ControlChart {
  constructor() {
    this.datasource = [];
    this.xcolumnkey = "date";
    this.ycolumnkey = "value";
    this.xlabel = "Date";
    this.ylabel = "Value";
    this.lowerlimit = 0;
    this.upperlimit = 1;
    this.centerlimit = 0.5;
    this.lowerlimit_text = "Lower Limit";
    this.upperlimit_text = "Upper Limit";
    this.centerlimit_text = "Center Limit";
    this.interpolation = "basis";
    this.pointid = "";
  }

  setData(data) {
    this.datasource = data;
  }

  setXColumn(key) {
    this.xcolumnkey = key;
  }

  setYColumn(key) {
    this.ycolumnkey = key;
  }

  setXLabel(label) {
    this.xlabel = label;
  }

  setYLabel(label) {
    this.ylabel = label;
  }

  setUpperLimit(limit) {
    this.upperlimit = limit;
  }

  setLowerLimit(limit) {
    this.lowerlimit = limit;
  }

  setCenterLimit(limit) {
    this.centerlimit = limit;
  }

  setUpperLimitText(text) {
    this.upperlimit_text = text;
  }

  setLowerLimitText(text) {
    this.lowerlimit_text = text;
  }

  setCenterLimitText(text) {
    this.centerlimit_text = text;
  }

  setInterpolation(method) {
    const curves = {
      basis: d3.curveBasis,
      linear: d3.curveLinear,
      step: d3.curveStep,
      cardinal: d3.curveCardinal,
    };
    this.interpolation = curves[method] || d3.curveBasis;
  }

  setPointId(id) {
    this.pointid = id;
  }

  draw(canvas) {
    const widthRaw = $(canvas).innerWidth() - 20;
    const heightRaw = $(canvas).innerHeight() - 20;
    const margin = { top: 20, right: 20, bottom: 30, left: 30 };
    const width = widthRaw - margin.left - margin.right;
    const height = heightRaw - margin.top - margin.bottom;

    const x = d3.scaleTime().range([0, width]);
    const y = d3.scaleLinear().range([height, 0]);

    const xAxis = d3.axisBottom(x).tickSize(0);
    const yAxis = d3.axisLeft(y).tickSize(0).tickFormat(d3.format(".2s"));

    const line = d3.line()
      .curve(this.interpolation)
      .x(d => x(d.x_axis))
      .y(d => y(d.y_axis));

    const svg = d3.select(canvas).append("svg")
      .attr("xmlns", "http://www.w3.org/2000/svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    const parseDate = d3.timeParse("%Y-%m-%d %H:%M:%S");

    this.datasource.forEach(d => {
      d.x_axis = parseDate(d[this.xcolumnkey]);
      d.y_axis = parseFloat(d[this.ycolumnkey]);
      d.point_id = d[this.pointid];
    });

    this.datasource.sort((a, b) => a.x_axis - b.x_axis);

    x.domain(d3.extent(this.datasource, d => d.x_axis));

    let min = d3.min(this.datasource, d => d.y_axis);
    if (min > this.lowerlimit) min = this.lowerlimit;

    let max = d3.max(this.datasource, d => d.y_axis);
    if (max < this.upperlimit) max = this.upperlimit;

    y.domain([min, max]);

    svg.append("g")
      .attr("class", "x axis")
      .attr("transform", `translate(0,${height})`)
      .call(xAxis)
      .style("font-size", "11px")
      .append("text")
      .attr("x", width)
      .attr("dy", "-0.71em")
      .attr("text-anchor", "end")
      .text(this.xlabel);

    svg.append("g")
      .attr("class", "y axis")
      .call(yAxis)
      .style("font-size", "11px")
      .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text(this.ylabel);

    svg.append("path")
      .datum(this.datasource)
      .attr("stroke", "#4682b4")
      .attr("stroke-width", "1.5px")
      .attr("fill", "none")
      .attr("class", "line")
      .attr("d", line);

    // Render data points
    this.datasource.forEach(d => {
      const group = svg.append("g").attr("fill", "#2f2f2f");

      group.append("circle")
        .attr("id", d.point_id)
        .attr("r", 3)
        .attr("cx", x(d.x_axis))
        .attr("cy", y(d.y_axis))
        .on("mouseout", function () {
          d3.select(this).attr("fill", "#2f2f2f").attr("r", 3);
          d3.select(this.parentNode).select("text").remove();
        })
        .on("mouseover", (event) => {
          d3.select(event.currentTarget).attr("fill", "#4682b4").attr("r", 6);
          group.append("text")
            .attr("fill", "#000000")
            .style("font-size", "10px")
            .attr("x", x(d.x_axis) - 10)
            .attr("y", y(d.y_axis) - 10)
            .text(`${d.y_axis} ${this.ylabel}`);
        })
        .on("click", (event) => {
          d3.select(event.currentTarget).attr("fill", "#4682b4").attr("r", 6);
          group.append("text")
            .attr("fill", "#000000")
            .style("font-size", "10px")
            .attr("x", x(d.x_axis) - 10)
            .attr("y", y(d.y_axis) - 10)
            .text(`${d.y_axis} ${this.ylabel}`);
        });
    });

    // Draw limit lines
    const limits = [
      { y: this.upperlimit, color: "#8e0000", text: this.upperlimit_text },
      { y: this.lowerlimit, color: "#8e0000", text: this.lowerlimit_text },
      { y: this.centerlimit, color: "#598859", text: this.centerlimit_text }
    ];

    limits.forEach(lim => {
      svg.append("line")
        .attr("stroke", lim.color)
        .attr("stroke-width", "1px")
        .attr("stroke-dasharray", lim.text.includes("Limit") ? "5,5" : null)
        .attr("x1", 0)
        .attr("y1", y(lim.y))
        .attr("x2", width)
        .attr("y2", y(lim.y));

      svg.append("text")
        .attr("x", 30)
        .attr("y", y(lim.y) - 5)
        .style("font-size", "11px")
        .text(lim.text);
    });
  }
}
