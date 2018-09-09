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
          $(this).removeClass('range-chart');
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
        var warn_min = data[3];
        var warn_max = data[4];
        if (warn_min == 0 && warn_max == 0) {
            warn_min = range_min;
            warn_max = range_max;
        } else {
            warn_min = data[3] < range_min ? data[3] : range_min;
            warn_max = data[4] > range_max ? data[4] : range_max;
        }

        // We want 1/3 of the whole scale length at left and right
        var extra = (warn_max - warn_min)/3;
        var x_min = result < warn_min ? result : warn_min - extra;
        var x_max = result > warn_max ? result : warn_max + extra;
        var inrange = result >= range_min && result < range_max;
        var inshoulder = (result < range_min && result >= warn_min) ||
                         (result >= range_max && result < warn_max);
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
            .attr("width", x(warn_min)-x(x_min)+bar_radius)
            .attr("height", bar_height)
            .attr("rx", bar_radius)
            .attr("ry", bar_radius)
            .style("fill", "#e9e9e9");

        // Left shoulder
        chart.append("rect")
            .attr("x", x(warn_min))
            .attr("y", bar_y)
            .attr("width", x(range_min)-x(warn_min))
            .attr("height", bar_height)
            .style("fill", color_shoulder);

        // Right shoulder
        chart.append("rect")
            .attr("x", x(range_max))
            .attr("y", bar_y)
            .attr("width", x(warn_max)-x(range_max))
            .attr("height", bar_height)
            .style("fill", color_shoulder);

        // Out-of-range right
        chart.append("rect")
            .attr("x", x(warn_max)-bar_radius)
            .attr("y", bar_y)
            .attr("width", x(x_max)-x(warn_max)+bar_radius)
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
}
