/**
 * Controller class for Worksheet templates
 */
function WorksheetTemplateEdit() {

    var that = this;

    that.load = function() {
        // Update the analysis list after method change
        var method_selector = $('#archetypes-fieldname-RestrictToMethod')
            .find('select');
        //update_analysis_list(method_selector);
        $(method_selector).bind('change', function(index, element){
            //update_analysis_list(this);
            update_instruments_list(this);
        });
    };
    /**
    * Updates the instruments list deppending on the selected method
    * @param {method_element} is a select object.
    **/
    function update_instruments_list(method_element){
        var method = $(method_element).val();
        $.ajax({
            url: window.portal_url + "/ajaxgetworksheettemplateinstruments",
            type: 'POST',
            data: {'_authenticator': $('input[name="_authenticator"]').val(),
                   'method_uid': $.toJSON(method) },
            dataType: 'json'
        }).done(function(data) {
            var instrument, i;
            if (data !== null && $.isArray(data)){
                instrument = $("#archetypes-fieldname-Instrument")
                    .find('select');
                $(instrument).find("option").remove();
                // Create an option for each instrument
                for (i=0; data.length > i; i++){
                    $(instrument).append(
                        '<option value="' + data[i].uid +
                        '">' + data[i].m_title + '</option>'
                    );
                }
            }
        }).fail(function() {
            window.bika.lims.log(
                    "bika.lims.worksheettemplate: Something went wrong while "+
                    "retrieving instrument list");
        });
    }
    /**
    * This function restricts the available analysis services to those with
    * the same method as the selected in the worksheet template.
    * @param {method_element} is a select object.
    **/
    function update_analysis_list(method_element){
        var method = $(method_element).val();
        $.ajax({
            url: window.portal_url + "/ajaxgetetworksheettemplateserviceswidget",
            type: 'POST',
            data: {'_authenticator': $('input[name="_authenticator"]').val(),
                   'method_uid': $.toJSON(method) },
            dataType: 'json'
        }).done(function(data) {
            if (data !== null){
                var services_div = $(
                    'div#archetypes-fieldname-Service #folderlisting-main-table')
                    .find('.bika-listing-table').remove();
                var instrument, i;
                var table = $(
                    'div#archetypes-fieldname-Service #folderlisting-main-table');
                $(table).append(data);
            }
        }).fail(function() {
            window.bika.lims.log(
                    "bika.lims.worksheettemplate: Something went wrong while "+
                    "retrieving the analysis services list");
        });
    }
}
