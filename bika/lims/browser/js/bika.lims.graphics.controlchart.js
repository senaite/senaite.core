/**
 * D3 Control chart
 */
function ControlChart() {

    var that = this;
    var datasource = [];
    var xcolumnkey = 'date';
    var ycolumnkey = 'value';
    var xlabel = "Date";
    var ylabel = "Value";
    var lowerlimit = 0;
    var upperlimit = 1;
    var centerlimit = 0.5;
    var lowerlimit_text = "Lower Limit";
    var upperlimit_text = "Upper Limit";
    var lowerlimit_text = "Center Limit";
    var interpolation = "basis";
    var pointid = "";

    /**
     * Sets the data to the chart
     *
     * Data format:
     *   [{ "date": "2014-03-12 13:01:00",
     *      "value": "2.13"},
     *    { "date": "2014-03-13 11:11:11",
     *      "value": "5.2"}]
     *
     * By default the column keys are 'date' and 'value', but can be
     * changed using the methods setXColumn and setYColumn. This allows
     * not to restrict the data source to only two columns.
     */
    this.setData = function(data) {
        that.datasource = data;
    }

    /**
     * Sets the X key from the datasource X-values.
     * By default, 'date'
     */
    this.setXColumn = function(xcolumnkey) {
        that.xcolumnkey = xcolumnkey;
    }

    /**
     * Sets the Y key from the datasource Y-values.
     * By default, 'value'
     */
    this.setYColumn = function(ycolumnkey) {
        that.ycolumnkey = ycolumnkey;
    }

    /**
     * Label to display on the Y-axis
     * By default, 'Date'
     */
    this.setYLabel = function(ylabel) {
        that.ylabel = ylabel;
    }

    /**
     * Label to display on the X-axis
     * By default, 'Value'
    */
    this.setXLabel = function(xlabel) {
        that.xlabel = xlabel;
    }

    /**
     * Sets the upper limit line value
     * Default: 1
     */
    this.setUpperLimit = function(upperLimit) {
        that.upperlimit = upperLimit;
    }

    /**
     * Sets the lower limit line value
     * Default: 0
     */
    this.setLowerLimit = function(lowerLimit) {
        that.lowerlimit = lowerLimit;
    }

    /**
     * Sets the center limit line value
     * Default: 0.5
     */
    this.setCenterLimit = function(centerLimit) {
        that.centerlimit = centerLimit;
    }

    /**
     * Sets the text to be displayed above upper limit line
     * By default: 'Upper Limit'
     */
    this.setUpperLimitText = function(upperLimitText) {
        that.upperlimit_text = upperLimitText;
    }

    /**
     * Sets the text to be displayed below lower limit line
     * By default: 'Lower Limit'
     */
    this.setLowerLimitText = function(lowerLimitText) {
        that.lowerlimit_text = lowerLimitText;
    }

    /**
     * Sets the text to be displayed above center limit line
     * By default: 'Center Limit'
     */
    this.setCenterLimitText = function(centerLimitText) {
        that.centerlimit_text = centerLimitText;
    }

    /**
     * Sets the interpolation to be used for drawing the line
     */
    this.setInterpolation = function(interpolation) {
        that.interpolation = interpolation;
    }

    /**
     * Sets the key to be used to set the identifier to each point
     */
    this.setPointId = function(pointId) {
        that.pointid = pointId;
    }

    /**
     * Draws the chart inside the container specified as 'canvas'
     * Accepts a jquery element identifier (i.e. '#chart')
     */
    this.draw = function(canvas) {
        var width = $(canvas).innerWidth() - 20;
        var height = $(canvas).innerHeight() - 20;
        var margin = {top: 20, right: 20, bottom: 30, left: 30},
        width = width - margin.left - margin.right,
        height = height - margin.top - margin.bottom;

        var x = d3.time.scale()
            .range([0, width]);

        var y = d3.scale.linear()
            .range([height,0]);

        var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom")
            .tickSize(0);

        var yAxis = d3.svg.axis()
            .scale(y)
            .orient("left")
            .tickSize(0);

        var line = d3.svg.line()
            .interpolate(that.interpolation)
            .x(function(d) { return x(d.x_axis); })
            .y(function(d) { return y(d.y_axis); });

        var svg = d3.select(canvas).append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
          .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        function tonumber(val) {
            if (!val || typeof o !== 'string') {
              return val;
            }
            return +val;
        }

        // Let's go for fun
        // Convert values to floats
        // "2014-02-19 03:11 PM"
        x_data_parse = d3.time.format("%Y-%m-%d %I:%M %p").parse;
        that.datasource.forEach(function(d) {
            d.x_axis = x_data_parse(d[that.xcolumnkey]);
            d.y_axis = tonumber(d[that.ycolumnkey]);
            d.point_id = d[that.pointid];
        });

        function sortByDateAscending(a, b) {
            return a.x_axis - b.x_axis;
        }
        that.datasource.sort(sortByDateAscending);

        x.domain(d3.extent(that.datasource, function(d) { return d.x_axis; }));
        var min = d3.min(that.datasource, function(d) { return d.y_axis; });
        if (min > that.lowerlimit) {
            min = that.lowerlimit;
        }
        var max = d3.max(that.datasource, function(d) { return d.y_axis; });
        if (max < that.upperlimit) {
            max = that.upperlimit;
        }
        y.domain([min, max]);

        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis)
                .style("font-size", "11px")
                .append("text")
                    .attr("x", width)
                    .attr("dy", "-0.71em")
                    .attr("text-anchor", "end")
                    .text(that.xlabel);

        svg.append("g")
            .attr("class", "y axis")
            .call(yAxis)
            .style("font-size", "11px")
            .append("text")
                .attr("transform", "rotate(-90)")
                .attr("y", 6)
                .attr("dy", ".71em")
                .style("text-anchor", "end")
                .text(that.ylabel);

        svg.append("path")
            .datum(that.datasource)
            .attr("stroke", "#4682b4")
            .attr("stroke-width", "1.5px")
            .attr("fill", "none")
            .attr("class", "line")
            .attr("d", line);

        // set points
        that.datasource.forEach(function(d) {
            svg.append("g")
                .attr("fill", "#2f2f2f")
                .append("circle")
                .attr("id", d.point_id)
                .attr("r", 3)
                .attr("cx", x(d.x_axis))
                .attr("cy", y(d.y_axis))
                .on("mouseout", function() {
                    d3.select(this)
                        .attr("fill", "#2f2f2f")
                        .attr("r", 3);
                    d3.select(this.parentNode.children[1])
                        .remove();
                })
                .on("mouseover",  function() {
                    d3.select(this)
                        .attr("fill", "#4682b4")
                        .attr("r", 6);
                    d3.select(this.parentNode)
                        .append("text")
                            .attr("fill", "#000000")
                            .style("font-size", "10px")
                            .attr("x", x(d.x_axis) - 10)
                            .attr("y", y(d.y_axis) - 10)
                            .text(d.y_axis+that.ylabel);
                }).on("click",  function() {
                    d3.select(this)
                        .attr("fill", "#4682b4")
                        .attr("r", 6);
                    d3.select(this.parentNode)
                        .append("text")
                            .attr("fill", "#000000")
                            .style("font-size", "10px")
                            .attr("x", x(d.x_axis) - 10)
                            .attr("y", y(d.y_axis) - 10)
                            .text(d.y_axis+that.ylabel);
                });
        });

        // upper limit line
        svg.append("line")
            .attr("stroke", "#8e0000")
            .attr("stroke-width", "1px")
            .attr("stroke-dasharray", "5, 5")
            .attr({ x1: 0, y1: y(that.upperlimit), x2: width, y2: y(that.upperlimit) });
        svg.append("text")
            .attr({ x: 30, y: y(that.upperlimit) - 5})
            .style("font-size","11px")
            .text(that.upperlimit_text);

        // lower limit line
        svg.append("line")
            .attr("stroke", "#8e0000")
            .attr("stroke-width", "1px")
            .attr("stroke-dasharray", "5, 5")
            .attr({ x1: 0, y1: y(that.lowerlimit), x2: width, y2: y(that.lowerlimit) });
        svg.append("text")
            .attr({ x: 30, y: y(that.lowerlimit) - 5})
            .style("font-size","11px")
            .text(that.lowerlimit_text);

        // center limit line
        svg.append("line")
            .attr("stroke", "#598859")
            .attr("stroke-width", "1px")
            .attr({ x1: 0, y1: y(that.centerlimit), x2: width, y2: y(that.centerlimit) });
        svg.append("text")
            .attr({ x: 30, y: y(that.centerlimit) - 5})
            .style("font-size","11px")
            .text(that.centerlimit_text);
    }
}
