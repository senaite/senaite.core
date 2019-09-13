/**
 * Controller class for Instrument Certification Edit view
 */
function InstrumentCertificationEditView() {

    var that = this;

    /**
     * Entry-point method for InstrumentCertificationEditView
     */
    that.load = function() {

        $('#Internal').live('change', function() {
            loadAgency();
        });

        loadAgency();
    }

    /**
     * Loads the Agency Field. If the certification is set as Internal,
     * the Agency field is hided.
     */
    function loadAgency() {
        if ($('#Internal').is(':checked')) {
            $('#archetypes-fieldname-Agency').hide();
        } else {
            $('#archetypes-fieldname-Agency').fadeIn('slow');
        }
    }
}
/**
 * Controller class for Instrument Edit view
 */
function InstrumentEditView() {

    var that = this;

    /**
     * Entry-point method for InstrumentEditView
     */
    that.load = function() {
      // Removing 'More' button of RecordsWidget
      $('#ResultFilesFolder_more').remove();
      // Removing 'Delete' button of rows and also deleting last empty row.
      var rows=$('.records_row_ResultFilesFolder');
      for(i=0;i< rows.length;i++){
        if (i>0 && i==(rows.length-1)) {
          rows[i].remove();
        }else{
          rows[i].children[2].remove();
        }
      }
    }

    $('#ImportDataInterface').change(function() {
        updateFolders();
    });

    /**
    When user adds/removes an Interface from select of Interfaces,
    Interface Results Folder will be updated.
    */
    function updateFolders() {
        // First we delete all rows, and then adding new ones accordingly to
        // selected Interfaces.
        var table = $("#ResultFilesFolder_table");
        var rows = $(".records_row_ResultFilesFolder");
        var values = $('#ImportDataInterface').val();
        rows.remove();

        // If no interface is selected we will add empty row
        if (values == null || (values.length==1 && values[0]=='')) {
          var new_row = $(rows[rows.length-1]).clone();
          for(i=0; i<$(new_row).children().length; i++){
              var td = $(new_row).children()[i];
              var input = $(td).children()[0];
              $(input).val('');
          }
          $(new_row).appendTo($(table));
        }else{
          for(i=0; i< values.length; i++){
            if (values[i]!='') {
              var new_row = $(rows[rows.length-1]).clone();
              var interface_td = $(new_row).children()[0];
              var interface_input = $(interface_td).children()[0];
              $(interface_input).val(values[i]);
              var folder_td = $(new_row).children()[1];
              var folder_input = $(folder_td).children()[0];
              $(folder_input).val('');
              $(new_row).appendTo($(table));
            }
          }
          // Checking if ids are Unique
          renameInputs();
        }
    }

    /**
    Updating IDs Interface Name and Folder inputs to be sure they are unique
    */
    function renameInputs() {
      var table = $("#ResultFilesFolder_table");
      var rows = $(".records_row_ResultFilesFolder");
      for(i=0; i< rows.length; i++){
        var inputs = $(rows[i]).find("input[id^='ResultFilesFolder']");
        for(j=0; j< inputs.length; j++){
          var ID = inputs[j].id;
          var prefix = ID.split("-")[0] + "-" + ID.split("-")[1];
          $(inputs[j]).attr('id', prefix + "-" + i);
        }
      }
    }
}


/**
 * Controller class for Instrument Reference Analyses view
 */
function InstrumentReferenceAnalysesView() {

    var that = this;

    /**
     * Entry-point method for InstrumentReferenceAnalysesView
     */
    that.load = function() {

        // Populate analyses selector
        var data = $.parseJSON($('#graphdata').val());
        var qcrec = false;
        $.map(data, function(value,key){
            $('#selanalyses').append('<option value="'+key+'">'+key+'</option>');
        });

        // Draw the chart and filter rows
        if ($('#selanalyses').val()) {
            updateQCSamples(data[$('#selanalyses').val()]);
            filterRows();
            drawControlChart(null, null);
        }

        $('#selanalyses').change(function(e) {
            updateQCSamples(data[$('#selanalyses').val()]);
            drawControlChart(null, null);
            filterRows();
        });

        $('#selqcsample').change(function(e) {
            drawControlChart(null, null);
            filterRows();
        });

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

            // Scaling for print
            var w = 670;
            var h = $('#chart').attr('height');
            drawControlChart(w, h);

            var WinPrint = window.open('', '', 'left=0,top=0,width=800,height=900,toolbar=0,scrollbars=0,status=0');
            var css = '<link href="' + window.portal_url + '/++resource++senaite.core.css/print-graph.css" type="text/css" rel="stylesheet">';
            var h1 = $("span.documentFirstHeading").closest('h1').clone();
            var content = $('#content-core').clone();
            $(content).prepend(h1);
            $(content).find('#selanalyses').after("<span class='bold'>"+$('#selanalyses').val()+"</span>");
            $(content).find('#interpolation').after("<span class='bold'>"+$('#interpolation').val()+"</span>");
            $(content).find('#selqcsample').after("<span class='bold'>"+$('#selqcsample').val()+"</span>");
            $(content).find('#selanalyses').hide();
            $(content).find('#interpolation').hide();
            $(content).find('#selqcsample').hide();

            WinPrint.document.write("<html><head>"+css+"</head><body>"+$(content).html()+"</body></html>");
            WinPrint.document.close();
            WinPrint.focus();
            WinPrint.print();

            // Re-scale
            $("#chart").css('width', '100%');
            $("#chart").removeAttr('height');
            drawControlChart(null, null);

            WinPrint.close();
        });

        $('div.bika-listing-table-container').fadeIn();
    }

    /**
     * Updates the QC Samples picklist
     */
    function updateQCSamples(qcsamples) {
        var presel = $('#selqcsample').val();
        $('#selqcsample option').remove();
        $.map(qcsamples, function(v, k) {
            var selected = k==presel ? ' selected' : '';
            $('#selqcsample').append('<option value="'+k+'"'+selected+'>'+k+'</option>');
        });
    }

    /**
     * Hide/Shows the reference analyses rows from the table in accordance
     * with the selected analysis and qcsample
     */
    function filterRows() {
        var ankeyword = $('#selanalyses').val().split("(");
        ankeyword = ankeyword[ankeyword.length-1].slice(0,-1).trim();
        var idqc = $('#selqcsample').val();
        var count = 0;
        $('div.results-info').remove();
        $('.item-listing-tbody tr').each(function( index ) {
            if ($(this).attr('keyword') != ankeyword
                || $(this).find('td.Partition a').html() != idqc) {
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
        //if ($("#chart svg").length > 0) {
            var w = width == null ? $("#chart").innerWidth() : width;
            var h = height == null ? $("#chart").innerHeight() : height;
            $("#chart").css('width', width);
            $("#chart").css('height', height);
       // }
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
