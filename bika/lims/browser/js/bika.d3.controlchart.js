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
    var lowerlimit_text = "Lower Limit";
    var upperlimit_text = "Upper Limit";

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
     * Draws the chart inside the container specified as 'canvas'
     * Accepts a jquery element identifier (i.e. '#chart')
     */
    this.draw = function(canvas) {
        var width = $(canvas).innerWidth() - 20;
        var height = $(canvas).innerHeight() - 20;
        var margin = {top: 20, right: 20, bottom: 30, left: 30},
        width = width - margin.left - margin.right,
        height = height - margin.top - margin.bottom;
        console.warn(height);

        var x = d3.time.scale()
        .range([0, width]);

        var y = d3.scale.linear()
            .range([height, 0]);

        var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom");

        var yAxis = d3.svg.axis()
            .scale(y)
            .orient("left");

        var line = d3.svg.line()
            .interpolate("basis")
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
            console.warn("X ("+that.xcolumnkey+"): "+x_data_parse(d[that.xcolumnkey]));
            console.warn("Y ("+that.ycolumnkey+"): "+tonumber(d[that.ycolumnkey]));
            d.x_axis = x_data_parse(d[that.xcolumnkey]);
            d.y_axis = tonumber(d[that.ycolumnkey]);
        });

        x.domain(d3.extent(that.datasource, function(d) { return d.x_axis; }));
        y.domain(d3.extent(that.datasource, function(d) { return d.y_axis; }));

        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis);

        svg.append("g")
            .attr("class", "y axis")
            .call(yAxis)
            .append("text")
                .attr("transform", "rotate(-90)")
                .attr("y", 6)
                .attr("dy", ".71em")
                .style("text-anchor", "end")
                .text(that.ylabel);

        svg.append("path")
            .datum(that.datasource)
            .attr("class", "line")
            .attr("d", line);

        // upper limit line
        svg.append("line")
            .attr("class", "limit-line")
            .attr({ x1: 0, y1: y(that.upperlimit), x2: width, y2: y(that.upperlimit) });
        svg.append("text")
            .attr({ x: width + 5, y: y(that.upperlimit) + 4})
            .text(that.upperlimit_text);
        console.warn(that.upperlimit_text);

        // lower limit line
        svg.append("line")
            .attr("class", "limit-line")
            .attr({ x1: 0, y1: y(that.lowerlimit), x2: width, y2: y(that.lowerlimit) });
        svg.append("text")
            .attr({ x: width + 5, y: y(that.lowerlimit) + 4})
            .text(that.lowerlimit_text);
    }
}
