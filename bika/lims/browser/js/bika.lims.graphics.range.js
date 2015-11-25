/**
 * Controller class for Range graphics
 */
function RangeGraph() {

    var that = this;

    that.load = function() {
        $(".range-chart").each(function(e) {
          var width = Number($(this).css('width').replace(/[^\d\.\-]/g, ''));
          loadRangeChart($(this).get(0),
              width,
              $.parseJSON($(this).attr('data-specs')));
        });
    }

    function loadRangeChart(canvas, wdth, data) {
        var width = wdth;
        var radius = width*0.03;
        var height = radius*2;
        width -= radius*2;

        var result = data[0];
        var range_min = data[1];
        var range_max = data[2];
        var error_min = data[3];
        var error_max = data[3];
        var range_min_shoulder = range_min - calc_shoulder(range_min, error_min);
        var range_max_shoulder = range_max + calc_shoulder(range_max, error_max);
        var result_min_shoulder = result - calc_shoulder(result, error_min);
        var result_max_shoulder = result + calc_shoulder(result, error_max);

        var x_min = range_min_shoulder - (range_max_shoulder - range_min_shoulder)/3;
        x_min = result_min_shoulder < x_min ? result_min_shoulder : x_min;
        var x_max = range_max_shoulder + (range_max_shoulder - range_min_shoulder)/3;
        x_max = result_max_shoulder > x_max ? result_max_shoulder : x_max;

        var inrange = result >= range_min && result <= range_max;
        var inshoulder = (result <= range_min && result >= range_min_shoulder)
                        || (result >= range_max && result <= range_max_shoulder);
        var outofrange = !inrange && !inshoulder;

        var color_range = (inrange || inshoulder) ? "#a8d6cf" : "#cdcdcd";
        var color_dot = inrange ? "#279989" : (inshoulder ? "#ffae00" : "#ff0000");
        var color_shoulder = (inrange || inshoulder) ? "#d9e9e6" : "#dcdcdc";

        var x = d3.scale.linear()
            .domain([x_min, x_max])
            .range([0, width]);

        var chart = d3.select(canvas)
            .append("svg")
            .attr("xmlns", "http://www.w3.org/2000/svg")
            .attr("width", width + (radius*2))
            .attr("height", height)
          .append("g")
            .attr("transform", "translate(" + radius + ",0)");

        // Backgrounds
        var bar_height = (radius*2)*0.8;
        var bar_y = (height/2)-((radius*2*0.8)/2);
        var bar_radius = radius*0.9;

        // Out-of-range left
        chart.append("rect")
            .attr("x", x(x_min))
            .attr("y", bar_y)
            .attr("width", x(range_min_shoulder)+bar_radius)
            .attr("height", bar_height)
            .attr("rx", bar_radius)
            .attr("ry", bar_radius)
            .style("fill", "#e9e9e9");

        // Left shoulder
        chart.append("rect")
            .attr("x", x(range_min_shoulder))
            .attr("y", bar_y)
            .attr("width", x(range_min)-x(range_min_shoulder))
            .attr("height", bar_height)
            .style("fill", color_shoulder);

        // Out-of-range right
        chart.append("rect")
            .attr("x", x(range_max_shoulder)-bar_radius)
            .attr("y", bar_y)
            .attr("width", x(x_max)-x(range_max_shoulder)+bar_radius)
            .attr("height", bar_height)
            .attr("rx", bar_radius)
            .attr("ry", bar_radius)
            .style("fill", "#e9e9e9");

        // Valid range
        // 8a8d8f a8d6cf
        chart.append("rect")
            .attr("x", x(range_min))
            .attr("y", bar_y)
            .attr("width", x(range_max)-x(range_min))
            .attr("height", bar_height)
            .style("fill", color_range);

        // Right shoulder
        chart.append("rect")
            .attr("x", x(range_max))
            .attr("y", bar_y)
            .attr("width", x(range_max_shoulder)-x(range_max))
            .attr("height", bar_height)
            .style("fill", color_shoulder);

        // Min shoulder line
      /*  chart.append("rect")
            .attr("x", x(range_min_shoulder))
            .attr("y", bar_y)
            .attr("width", 1)
            .attr("height", bar_height)
            .style("fill", "white");

        // Min line
        chart.append("rect")
            .attr("x", x(range_min))
            .attr("y", bar_y)
            .attr("width", 1)
            .attr("height", bar_height)
            .style("fill", "white");

        // Max line
        chart.append("rect")
            .attr("x", x(range_max))
            .attr("y", bar_y)
            .attr("width", 1)
            .attr("height", bar_height)
            .style("fill", "white");

        // Max shoulder line
        chart.append("rect")
            .attr("x", x(range_max_shoulder))
            .attr("y", bar_y)
            .attr("width", 1)
            .attr("height", bar_height)
            .style("fill", "white");*/

        // Outer dot
        chart.append("circle")
            .attr("cx", x(result))
            .attr("cy", height/2)
            .attr("r", radius)
            .style("fill", "white");

        // Inner dot
        chart.append("circle")
            .attr("cx", x(result))
            .attr("cy", height/2)
            .attr("r", radius-1)
            .style("fill", color_dot);

    }
    function calc_shoulder(value, error_percentage) {
        return Math.abs(error_percentage) > 0 ? value*(Math.abs(error_percentage)/100) : 0;
    }
}
