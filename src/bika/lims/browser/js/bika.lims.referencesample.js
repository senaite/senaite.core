/**
 * Controller class for Reference Sample Analyses View
 */
function ReferenceSampleAnalysesView() {

    var that = this;

    /**
     * Entry-point method for ReferenceSampleAnalysesView
     */
    that.load = function() {

        // Populate analyses selector
        var data = $.parseJSON($('#graphdata').val());
        var qcrec = false;
        $.map(data, function(value,key){
            $('#selanalyses').append('<option value="'+key+'">'+key+'</option>');
            if (qcrec == false) {
                $.map(value, function(v, k) {
                    $('#selqcsample').val(k);
                });
                qcrec = true;
            }
        });

        // Draw the chart and filter rows
        if ($('#selanalyses').val()) {
            filterRows();
            drawControlChart(null, null);
        }

        $('#selanalyses').change(function(e) {
            drawControlChart(null, null);
            filterRows();
        });

       /* $('#selqcsample').change(function(e) {
            drawControlChart();
            filterRows();
        });*/

        $('#interpolation').change(function(e) {
            drawControlChart(null, null);
        });

        $('.item-listing-tbody tr').mouseover(function(e) {
            if ($(this).attr('uid') != '') {
                $(this).addClass('selected');
                var uid = $(this).attr('uid');
                $('#chart svg g circle#'+uid).trigger('__onmouseover');
            }
        });
        $('.item-listing-tbody tr').mouseout(function(e) {
            $(this).removeClass('selected');
            if ($(this).attr('uid') != '') {
                var uid = $(this).attr('uid');
                $('#chart svg g circle#'+uid).trigger('__onmouseout');
            }
        });

        $('#printgraph').click(function(e) {
            e.preventDefault();

            $('#selanalyses').find('option[selected]').remove();
            $('#selanalyses').find('option[value="'+$(selanalyses).val()+'"]').prop('selected', true);
            // Scaling for print
            var w = 670;
            var h = $('#chart').attr('height');
            drawControlChart(w, h);

            var WinPrint = window.open('', '', 'left=0,top=0,width=800,height=900,toolbar=0,scrollbars=0,status=0');
            var css = '<link href="' + window.portal_url + '/++resource++bika.lims.css/print-graph.css" type="text/css" rel="stylesheet">';
            var h1 = $("span.documentFirstHeading").closest('h1').clone();
            var content = $('#content-core').clone();
            $(content).prepend(h1);
            $(content).find('#selanalyses').after("<span class='bold'>"+$('#selanalyses').val()+"</span>");
            $(content).find('#interpolation').after("<span class='bold'>"+$('#interpolation').val()+"</span>");
            $(content).find('#selanalyses').hide();
            $(content).find('#interpolation').hide();

            WinPrint.document.write("<html><head>"+css+"</head><body>"+$(content).html()+"</body></html>");
            WinPrint.document.close();
            WinPrint.focus();
            WinPrint.print();
            WinPrint.close();

            // Re-scale
            $("#chart").css('width', '100%');
            $("#chart").removeAttr('height');
            drawControlChart(null, null);

        });

        $('div.bika-listing-table-container').fadeIn();
    }

    /**
     * Hide/Shows the reference analyses rows from the table in accordance
     * with the selected analysis and qcsample
     */
    function filterRows() {
        var ankeyword = $('#selanalyses').val().split("(");
        ankeyword = ankeyword[ankeyword.length-1].slice(0,-1).trim();
        var count = 0;
        $('div.results-info').remove();
        $('.item-listing-tbody tr').each(function( index ) {
            if ($(this).attr('keyword') != ankeyword) {
                $(this).hide();
            } else {
                $(this).fadeIn();
                count+=1;
            }
        });
        $('.bika-listing-table').closest('div').before('<div class="results-info">'+count+' results found</div>');
    }

    /**
     * Draws the control chart in accordance with the selected analysis
     * and qc-sample, as well as the interpolation
     */
    function drawControlChart(width, height) {
        var analysiskey = $('#selanalyses').val();
        var reftype = $('#selqcsample').val();
        var interpolation = $('#interpolation').val()
        var w = width == null ? $("#chart").innerWidth() : width;
        var h = height == null ? $("#chart").innerHeight() : height;
        $("#chart").css('width', width);
        $("#chart").css('height', height);
        $("#chart").html("");
        $("#chart").show();
        var data = $.parseJSON($('#graphdata').val());
        data = data[analysiskey]
        if (!(reftype in data) || data[reftype].length == 0) {
            // There is no results for this type of refsample
            $("#chart").hide();
            return;
        }
        data = data[reftype];
        var unit = data[data.length-1]['unit'];
        var upper = data[data.length-1]['upper'];
        var lower = data[data.length-1]['lower'];
        var target = data[data.length-1]['target'];
        var ylabel = "Result";
        if (unit == '' || typeof unit == 'undefined') {
            unit = "";
        } else {
            ylabel = unit;
        }

        var uppertxt = $.trim("UCL (" + upper+""+unit+")");
        var lowertxt = $.trim("LCL (" + lower+""+unit+")");
        var centrtxt = $.trim("CL ("+target+""+unit+")");
        chart = new ControlChart();
        chart.setData(data);
        chart.setInterpolation(interpolation);
        chart.setXColumn('date');
        chart.setYColumn('result');
        chart.setPointId('id');
        chart.setYLabel(ylabel);
        chart.setXLabel('Date');
        chart.setUpperLimitText(uppertxt);
        chart.setLowerLimitText(lowertxt);
        chart.setCenterLimitText(centrtxt);
        chart.setCenterLimit(target);
        chart.setUpperLimit(upper);
        chart.setLowerLimit(lower);
        chart.draw('#chart');
    }
}
