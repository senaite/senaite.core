/**
 * Controller class for Client's Edit view
 */
function ClientEditView() {

    var that = this;
    var check = "#AllowDecimalMark"

    /**
     * Entry-point method for ClientEditView
     */
    that.load = function() {
	
	if( $(check).is(':checked') ){
	    $("#archetypes-fieldname-DecimalMark").hide();
	}
	else {
	    $("#archetypes-fieldname-DecimalMark").fadeIn();
	}

        selectDecimalMarkState();
    }

    /**
     * When the Avoid Client's Decimal Mark Selection checkbox is set,
     * the function will disable Select Decimal Mark dropdown list.
     */
    function selectDecimalMarkState() {
	$(check).click(function(){
	    if( $(this).is(':checked') ){
		$("#archetypes-fieldname-DecimalMark").fadeOut();
	    }
	    else {
		$("#archetypes-fieldname-DecimalMark").fadeIn();
	    }
	});
    }
}
