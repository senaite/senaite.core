/** D3js Range Control Chart
 *
 * Currently not used, but kept as reference.
 *
 */
class RangeGraph {
  constructor() {
    this.load = this.load.bind(this);
  }

  load() {
    $(".range-chart").each((_, el) => {
      const $el = $(el);
      const width = parseFloat($el.css("width")) || 100;
      const rangeData = JSON.parse($el.attr("data-range") || "{}");
      const resultData = JSON.parse($el.attr("data-result") || "null");

      this.loadRangeChart(el, width, rangeData, resultData);
      $el.removeClass("range-chart");
    });
  }

  toDictOfFloats(range, result) {
    if (!$.isNumeric(result)) return null;

    const parsedResult = parseFloat(result);
    const min = $.isNumeric(range.min) ? parseFloat(range.min) : parsedResult;
    const max = $.isNumeric(range.max) ? parseFloat(range.max) : parsedResult;
    if (min === max) return null;

    let warnMin = min;
    let warnMax = max;
    if ($.isNumeric(range.warn_min)) {
      warnMin = Math.min(warnMin, parseFloat(range.warn_min));
    }
    if ($.isNumeric(range.warn_max)) {
      warnMax = Math.max(warnMax, parseFloat(range.warn_max));
    }

    return {
      result: parsedResult,
      min,
      max,
      warn_min: warnMin,
      warn_max: warnMax
    };
  }

  loadRangeChart(canvas, width, range, result) {
    const specs = this.toDictOfFloats(range, result);
    if (!specs) return;

    const radius = width * 0.03;
    const height = radius * 2;
    const contentWidth = width - radius * 2;

    const { min, max, warn_min, warn_max, result: res } = specs;
    const minOp = range.min_operator || "geq";
    const maxOp = range.max_operator || "leq";

    const extra = (warn_max - warn_min) / 3;
    const xMin = res < warn_min ? res : warn_min - extra;
    const xMax = res > warn_max ? res : warn_max + extra;

    let inRange = minOp === "gt" ? res > min : res >= min;
    inRange = maxOp === "lt" ? inRange && res < max : inRange && res <= max;

    let inShoulder = false;
    if (!inRange) {
      const inWarnMin = (minOp === "gt" ? res <= min : res < min) && res >= warn_min;
      const inWarnMax = (maxOp === "lt" ? res >= max : res > max) && res <= warn_max;
      inShoulder = inWarnMin || inWarnMax;
    }

    const colorRange = inRange || inShoulder ? "#a8d6cf" : "#cdcdcd";
    const colorDot = inRange ? "#279989" : inShoulder ? "#ffae00" : "#ff0000";
    const colorShoulder = inRange || inShoulder ? "#d9e9e6" : "#dcdcdc";

    const x = d3.scaleLinear()
      .domain([xMin, xMax])
      .range([0, contentWidth]);

    const chart = d3.select(canvas)
      .append("svg")
      .attr("xmlns", "http://www.w3.org/2000/svg")
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", `translate(${radius},0)`);

    const barHeight = height * 0.8;
    const barY = (height - barHeight) / 2;
    const barRadius = radius * 0.9;

    const segments = [
      { x: x(xMin), width: x(warn_min) - x(xMin) + barRadius, fill: "#e9e9e9" },
      { x: x(warn_min), width: x(min) - x(warn_min), fill: colorShoulder },
      { x: x(min), width: x(max) - x(min), fill: colorRange },
      { x: x(max), width: x(warn_max) - x(max), fill: colorShoulder },
      { x: x(warn_max) - barRadius, width: x(xMax) - x(warn_max) + barRadius, fill: "#e9e9e9" }
    ];

    segments.forEach(seg => {
      chart.append("rect")
        .attr("x", seg.x)
        .attr("y", barY)
        .attr("width", seg.width)
        .attr("height", barHeight)
        .attr("rx", barRadius)
        .attr("ry", barRadius)
        .style("fill", seg.fill);
    });

    chart.append("circle")
      .attr("cx", x(res))
      .attr("cy", height / 2)
      .attr("r", radius)
      .style("fill", "white");

    chart.append("circle")
      .attr("cx", x(res))
      .attr("cy", height / 2)
      .attr("r", radius - 1)
      .style("fill", colorDot);
  }
}
